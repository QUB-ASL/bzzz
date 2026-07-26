#include <Arduino.h>
#include "config.hpp"
#include "ahrs.hpp"
#include "motors.hpp"
#include "controller.hpp"
#include "quaternion.hpp"
#include "util.hpp"
#include "raspberryEsp32Interface.hpp"
#include "prediction.hpp"
#include "fdi.hpp"
#include "reconfiguration.hpp"


// ---- fault injection: which motor switch A kills ----
#define FAULT_MOTOR  motorFL   // <-- change: motorFL, motorFR, motorML, motorMR, motorBL, motorBR
 



using namespace bzzz;

//--------objects---------

AHRS ahrs;
MotorDriver motorDriver;
Controller controller;
Reconfiguration reconfiguration;
RaspberryEsp32Interface raspberryEsp32Interface(true);
static const int NUM_HYP = 7;
Predictor    pred[NUM_HYP];
ResidualCost cost[NUM_HYP];

// which gamma index fails, per hypothesis;  -1 = healthy
// predictor motor order: FR(0) FL(1) ML(2) BL(3) BR(4) MR(5)
static const int FAIL_IDX[NUM_HYP] = { -1, 1, 0, 5, 4, 3, 2 };
//                              J0  J1 J2 J3 J4 J5 J6
//                            ok  FL FR MR BR BL ML


//--------Variables----------

Quaternion initialQuaternion;
float initialAngularVelocity[3];

float quaterninonData[4];
float measuredOmega[3];
float OmegaCorrected[3];

float lastThrottle = 1000;
float lastRoll = 0.0f;
float lastPitch = 0.0f;
float controlDebug[3] = {0.0f, 0.0f, 0.0f};

int motorFL;
int motorFR;
int motorML;
int motorMR;
int motorBL;
int motorBR;

float pwmOffset = 800.0f;

float resQ[4], resW[3], qPredOut[4], wPredOut[3];
float J[NUM_HYP];
int   bestHyp = 0;
int   candidate = 0;
int   streak = 0;
int   lockedHyp = 0;

// trend tracking: short rolling history of J per hypothesis
static const int TREND_LEN = 10;
float Jhist[NUM_HYP][TREND_LEN];
int   trendCount = 0;



static const float EMA_ALPHA = 0.05f;   // weight on new sample; 0.9 stays on history


// [qw qx qy qz wx wy wz], from healthy-log residual RMS (props off)
  static const float SIGMA[7] = {1e6f, 1e6f, 1e6f, 1e6f, 9.30f, 5.14f, 4.48f};


void setup()
{


    Serial.begin(SERIAL_BAUD_RATE);
    Serial.setTimeout(5);
    Serial.println("#BOOT v2 nJ=10");


    setupBuzzer();



    if (! ahrs.setup())
    {
        Serial.println("IMU setup Failed!");
        while(1);

    }
    ahrs.preflightCalibrate(false);

    ahrs.calibrateMagnetometer(
        MAGNETOMETER_BIAS_X,
        MAGNETOMETER_BIAS_Y,
        MAGNETOMETER_BIAS_Z,
        MAGNETOMETER_SCALE_X,
        MAGNETOMETER_SCALE_Y,
        MAGNETOMETER_SCALE_Z);


    ahrs.averageQuaternion(initialQuaternion);
    ahrs.averageAngularVelocities(initialAngularVelocity);

    buzz(2);


    waitForPiSerial();
   
    raspberryEsp32Interface.waitForArmCommand();
    
    Serial.println("settling AHRS...");
    uint32_t t0 = millis();
    while (millis() - t0 < 4000) { ahrs.update(); }

  static const float GAMMA[NUM_HYP][6] = {
    //   FR    FL    ML    BL    BR    MR
        {1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f},   // J0 healthy
        {1.0f, 0.0f, 1.0f, 1.0f, 1.0f, 1.0f},   // J1 FL failed
        {0.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f},   // J2 FR failed
        {1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 0.0f},   // J3 MR failed
        {1.0f, 1.0f, 1.0f, 1.0f, 0.0f, 1.0f},   // J4 BR failed
        {1.0f, 1.0f, 1.0f, 0.0f, 1.0f, 1.0f},   // J5 BL failed
        {1.0f, 1.0f, 0.0f, 1.0f, 1.0f, 1.0f}    // J6 ML failed
    };

    for (int h = 0; h < NUM_HYP; h++)
    {
        pred[h].setGamma(GAMMA[h]);
        pred[h].setPwmMapping(U_TO_PWM, ZERO_ROTOR_SPEED, ABSOLUTE_MAX_PWM);
        J[h] = 0.0f;
    }
    motorDriver.attachAndArm();
  
  
  
    buzz(3);

 
}
 void setGainsFromRcTrimmers()
{
    
    float qGain =
        - raspberryEsp32Interface.trimmerVRAPercentage() * RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN;

    
    float omegaXYGain =
        - raspberryEsp32Interface.trimmerVRBPercentage()*RADIO_TRIMMER_MAX_OMEGA_XY_GAIN;

    
    float omegaZGain =
        -  raspberryEsp32Interface.trimmerVRCPercentage()*RADIO_TRIMMER_MAX_OMEGA_Z_GAIN;

    controller.setQuaternionGain(qGain);
    controller.setAngularVelocityXYGain(omegaXYGain);
    controller.setYawAngularVelocityGain(omegaZGain);

    reconfiguration.setQuaternionGain(qGain);
    reconfiguration.setAngularVelocityXYGain(omegaXYGain);
    reconfiguration.setYawAngularVelocityGain(omegaZGain);
        
    pwmOffset = 700.0f + raspberryEsp32Interface.trimmerVREPercentage() * 200.0f;  // sweeps 700-900

 
}

    static float yawOf(Quaternion &q)
{
    return atan2f(2.0f * (q[0]*q[3] + q[1]*q[2]),
                  1.0f - 2.0f * (q[2]*q[2] + q[3]*q[3]));
}





void loop()
{
    
    bool rcValid = raspberryEsp32Interface.readPiData();
    bool injectFault = raspberryEsp32Interface.switchA();

    if (rcValid)
{
    lastThrottle = raspberryEsp32Interface.throttleReferencePWM();
    lastRoll = raspberryEsp32Interface.rollReferenceAngleRad();
    lastPitch = raspberryEsp32Interface.pitchReferenceAngleRad();
}

   if (!ahrs.update())
        return;

    static uint8_t imuDiv = 0;
    if (++imuDiv < 2) return;      // 250 Hz -> 125 Hz
    imuDiv = 0;



    setGainsFromRcTrimmers();



    ahrs.quaternion(quaterninonData);

    ahrs.angularVelocity(measuredOmega);

    OmegaCorrected[0] = measuredOmega[0] - initialAngularVelocity[0];
    OmegaCorrected[1] = measuredOmega[1] - initialAngularVelocity[1];
    OmegaCorrected[2] = measuredOmega[2] - initialAngularVelocity[2];

    

    Quaternion currentQuaternion(quaterninonData);
    Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;


 
    float yawReferenceQuaternion = yawOf(relativeQuaternion);


    Quaternion referenceQuaternion(
        yawReferenceQuaternion,
        raspberryEsp32Interface.pitchReferenceAngleRad(),
        raspberryEsp32Interface.rollReferenceAngleRad()
    );

    Quaternion attitudeError =
        referenceQuaternion - relativeQuaternion;

    

    static uint32_t tPrevLoop = 0;
    uint32_t tNowLoop = micros();
    float dtActual = (tNowLoop - tPrevLoop) * 1e-6f;
    bool dtOk = (tPrevLoop != 0) &&
                (dtActual > 0.5f * SAMPLING_TIME) &&
                (dtActual < 2.0f * SAMPLING_TIME);
    tPrevLoop = tNowLoop;






        
    if (raspberryEsp32Interface.kill())
    {
        motorDriver.disarm();
        // reset all fault-decision state on disarm — lock should never
        // carry over from one flight to the next, only reboot did this before
        lockedHyp = 0;
        candidate = 0;
        streak = 0;
        return;
    }

// controller.motorPwmSignals(
//         attitudeError,
//         OmegaCorrected,
//         raspberryEsp32Interface.yawRateReferenceRadSec(),
//         raspberryEsp32Interface.throttleReferencePWM(),
//         motorFL,
//         motorFR,
//         motorBL,
//         motorBR,
//         motorML,
//         motorMR
//     );
// float controlDebug[3];
// controller.getLastControl(controlDebug);

if (lockedHyp == 0)
{
    // H0: healthy hexacopter
    controller.motorPwmSignals(
        attitudeError,
        OmegaCorrected,
        raspberryEsp32Interface.yawRateReferenceRadSec(),
        raspberryEsp32Interface.throttleReferencePWM(),
        motorFL,
        motorFR,
        motorBL,
        motorBR,
        motorML,
        motorMR
    );
}
else
{
    // H1-H6: fault-tolerant reconfiguration
    reconfiguration.motorPwmSignals(
        lockedHyp,
        attitudeError,
        OmegaCorrected,
        raspberryEsp32Interface.yawRateReferenceRadSec(),
        raspberryEsp32Interface.throttleReferencePWM(),
        motorFL,
        motorFR,
        motorBL,
        motorBR,
        motorML,
        motorMR
    );
}

float controlDebug[3];
controller.getLastControl(controlDebug);



   if (injectFault)
    FAULT_MOTOR = 905;

    // predictor motor order: FR FL ML BL BR MR — same order as GAMMA/m_B
    // predictor motor order: FR FL ML BL BR MR — same order as GAMMA/m_B
    float pwmActual[6] = {
        (float)motorFR, (float)motorFL, (float)motorML,
        (float)motorBL, (float)motorBR, (float)motorMR
    };

    // write to ESCs FIRST — don't let FDI math delay motor response
    motorDriver.writeSpeedToEsc(
        motorFL,
        motorFR,
        motorBL,
        motorBR,
        motorML,
        motorMR
    );
    for (int h = 0; h < NUM_HYP; h++)
    {
        pred[h].step(relativeQuaternion, OmegaCorrected, pwmActual, pwmOffset, SAMPLING_TIME);

        float rq[4], rw[3];
        if (pred[h].residual(rq, rw) && dtOk)
            J[h] = cost[h].push(rq, rw, SIGMA);
    }

    if (!pred[0].residual(resQ, resW)) {
        for (int i = 0; i < 4; i++) resQ[i] = 0.0f;
        for (int i = 0; i < 3; i++) resW[i] = 0.0f;
    }
    pred[0].maturedPrediction(qPredOut, wPredOut);

    // shift history, push newest J
    for (int h = 0; h < NUM_HYP; h++)
    {
        for (int k = 0; k < TREND_LEN - 1; k++)
            Jhist[h][k] = Jhist[h][k + 1];
        Jhist[h][TREND_LEN - 1] = J[h];
    }
    if (trendCount < TREND_LEN) trendCount++;

    // compute slope: newer-half average minus older-half average
    float slope[NUM_HYP];
    if (trendCount >= TREND_LEN)
    {
        for (int h = 0; h < NUM_HYP; h++)
        {
            float oldAvg = 0.0f, newAvg = 0.0f;
            for (int k = 0; k < TREND_LEN / 2; k++) oldAvg += Jhist[h][k];
            for (int k = TREND_LEN / 2; k < TREND_LEN; k++) newAvg += Jhist[h][k];
            oldAvg /= (TREND_LEN / 2);
            newAvg /= (TREND_LEN / 2);
            slope[h] = newAvg - oldAvg;   // negative = sustained decline
        }
    }
    else
    {
        for (int h = 0; h < NUM_HYP; h++) slope[h] = 0.0f;   // not enough history yet
    }

    // bestHyp = instantaneous raw argmin, no delay, but must be MEANINGFULLY
    // lower than healthy — protects against ordinary maneuvers where model
    // imperfection makes one hyp marginally, coincidentally beat J0.
    int rawBest = 0;
    for (int h = 1; h < NUM_HYP; h++)
        if (J[h] < J[rawBest]) rawBest = h;

        static const float MARGIN = 0.6f;
        static const float J0_MIN = 0.50f;

        bool windowFull = cost[0].count() >= 8;

        bool faultCandidate =
            windowFull &&
            rawBest != 0 &&
            J[0] > J0_MIN &&
            J[rawBest] < MARGIN * J[0];

        bestHyp = faultCandidate ? rawBest : 0;
    // streak tracks how long the SAME non-healthy hypothesis has kept
    // winning, in a row. Switching between different wrong hypotheses is
    // fine — it just resets the streak, never locks, no penalty. Going
    // back to healthy (bestHyp==0) also resets it.
    static const int LOCK_LEN = 15;

static float lastPwmFDI[6] = {
    1000.0f, 1000.0f, 1000.0f,
    1000.0f, 1000.0f, 1000.0f
};

float maxPwmStep = 0.0f;

for (int i = 0; i < 6; i++)
{
    float dPwm = fabsf(pwmActual[i] - lastPwmFDI[i]);

    if (dPwm > maxPwmStep)
        maxPwmStep = dPwm;

    lastPwmFDI[i] = pwmActual[i];
}

const bool aggressiveManeuver = (maxPwmStep > 5.0f);

    // if (!lockedHyp)
    // {
    //     if (bestHyp != 0)
    //     {
    //         if (bestHyp == candidate) streak++;
    //         else { candidate = bestHyp; streak = 1; }

    //         if (streak >= LOCK_LEN) lockedHyp = bestHyp;
    //     }
    //     else
    //     {
    //         streak = 0;
    //     }
    // }

    if (!lockedHyp)
{
    if (aggressiveManeuver)
    {
        streak = 0;
    }
    else if (bestHyp != 0)
    {
        if (bestHyp == candidate) streak++;
        else
        {
            candidate = bestHyp;
            streak = 1;
        }

        if (streak >= LOCK_LEN)
            lockedHyp = bestHyp;
    }
    else
    {
        streak = 0;
    }
}

    else
    {
        bestHyp = lockedHyp;  // stay locked
    }

    // // TEMPORARY diagonal correction — front/back pairs only (FR<->BL, FL<->BR),
    
    float Jsend[NUM_HYP + 9];

for (int h = 0; h < NUM_HYP; h++)
    Jsend[h] = J[h];

// Existing diagnostic values
Jsend[NUM_HYP + 0] = (float)bestHyp;
Jsend[NUM_HYP + 1] = injectFault ? 1.0f : 0.0f;
Jsend[NUM_HYP + 2] = dtActual * 1000.0f;

// Command references
Jsend[NUM_HYP + 3] = lastPitch;
Jsend[NUM_HYP + 4] = lastRoll;
Jsend[NUM_HYP + 5] =
    raspberryEsp32Interface.yawRateReferenceRadSec();

// Controller outputs
Jsend[NUM_HYP + 6] = controlDebug[0];   // uRoll
Jsend[NUM_HYP + 7] = controlDebug[1];   // uPitch
Jsend[NUM_HYP + 8] = controlDebug[2];   // uYaw

    raspberryEsp32Interface.sendFlightDataToPi(
    relativeQuaternion[0], relativeQuaternion[1],
    relativeQuaternion[2], relativeQuaternion[3],
    OmegaCorrected[0], OmegaCorrected[1], OmegaCorrected[2],
    motorFL, motorFR, motorBL, motorBR, motorML, motorMR,
    qPredOut[0], qPredOut[1], qPredOut[2], qPredOut[3],
    wPredOut[0], wPredOut[1], wPredOut[2],
    Jsend, NUM_HYP + 9);

}



