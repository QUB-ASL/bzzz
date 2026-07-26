#include <Arduino.h>
#include "config.hpp"
#include "ahrs.hpp"
#include "motors.hpp"
#include "controller.hpp"
#include "quaternion.hpp"
#include "util.hpp"
#include "raspberryEsp32Interface.hpp"


using namespace bzzz;

//--------objects---------

AHRS ahrs;
MotorDriver motorDriver;
Controller controller;
RaspberryEsp32Interface raspberryEsp32Interface(false);

//--------Variables----------

Quaternion initialQuaternion;
float initialAngularVelocity[3];

float quaterninonData[4];
float measuredOmega[3];
float OmegaCorrected[3];

int motorFL;
int motorFR;
int motorML;
int motorMR;
int motorBL;
int motorBR;

void setup()
{


    Serial.begin(115200);
    delay(2000);

    Serial.println();
    Serial.println("hexacopter RC stabilazier");

    setupBuzzer();

    Serial.print("Setting up AHRS");

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

    Serial.println("Getting Initial Attitude......");

    ahrs.averageQuaternion(initialQuaternion);
    ahrs.averageAngularVelocities(initialAngularVelocity);

    buzz(2);

    Serial.println("waiting for Raspberry pi....");
    waitForPiSerial();
    Serial.println("waiting for ARM command......");
    raspberryEsp32Interface.waitForArmCommand();
    Serial.println("attaching ESC's..............");
    motorDriver.attachAndArm();

    buzz(3);

    Serial.println("RC stabilization Test Ready!");
    Serial.println(); 
}

void loop()
{
    if (!raspberryEsp32Interface.readPiData())
    return;

    if (!ahrs.update())
    return;

    ahrs.quaternion(quaterninonData);
    ahrs.angularVelocity(measuredOmega);

    OmegaCorrected[0] = measuredOmega[0] - initialAngularVelocity[0];
    OmegaCorrected[1] = measuredOmega[1] - initialAngularVelocity[1];
    OmegaCorrected[2] = measuredOmega[2] - initialAngularVelocity[2];

    Quaternion currentQuaternion(quaterninonData);
    Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;

    float yawReferenceQuaternion = ahrs.currentYawRad();

    Quaternion referenceQuaternion(
        yawReferenceQuaternion,
        raspberryEsp32Interface.pitchReferenceAngleRad(),
        raspberryEsp32Interface.rollReferenceAngleRad()
    );

    Quaternion attitudeError =
        referenceQuaternion - relativeQuaternion;

    controller.motorPwmSignals(
        attitudeError,
        OmegaCorrected,
        raspberryEsp32Interface.pitchReferenceAngleRad(),
        raspberryEsp32Interface.throttleReferencePWM(),
        motorFL,
        motorFR,
        motorBL,
        motorBR,
        motorML,
        motorMR
    );


    motorDriver.writeSpeedToEsc(
        motorFL,
        motorFR,
        motorBL,
        motorBR,
        motorML,
        motorMR
    );

    Serial.printf("THR:%4.0f r:%6.3f p:%6.3f y:%6.3f\n",
        raspberryEsp32Interface.pitchReferenceAngleRad(),
        raspberryEsp32Interface.throttleReferencePWM(),
        raspberryEsp32Interface.rollReferenceAngleRad(),
        raspberryEsp32Interface.yawRateReferenceRadSec()
    );

    Serial.printf(" FL:%4d FR:%4d ML:%4d MR:%4d BL:%4d BR:%4d\n\n ",
        motorFL,
        motorFR,
        motorBL,
        motorBR,
        motorML,
        motorMR
    );
}
