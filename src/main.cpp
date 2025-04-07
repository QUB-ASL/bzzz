#include <Arduino.h>
#include "quaternion.hpp"
#include "config.hpp"
#include "motors.hpp"
#include "raspberryEsp32Interface.hpp"
#include "ahrs.hpp"
#include "controller.hpp"
#include "fail_safes.hpp"
#include "util.hpp"

using namespace bzzz;

hw_timer_t *timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
MotorDriver motorDriver;
RaspberryEsp32Interface raspberryEsp32Interface(true);
AHRS ahrs;
Controller controller;
Quaternion initialQuaternion;
FailSafes failSafes(TX_CONNECTION_TIMEOUT_IN_uS);
float yawReferenceRad = 0.0;
float initialAngularVelocity[3];
float IMUData[6];
int motorFL, motorFR, motorBL, motorBR;

#if UAV_TYPE == UAV_TYPE_HEXACOPTER
int motorML, motorMR;
#endif

bool wasKill = 0;
bool isKill = 0;
unsigned long timestampLastKill = 0;
bool isThrottleStickDown = 0;

volatile bool timerState = true;

void IRAM_ATTR onTimer()
{
  taskENTER_CRITICAL_ISR(&timerMux);
  timerState = !timerState;
  taskEXIT_CRITICAL_ISR(&timerMux);
}

void setupTimer()
{
  timer = timerBegin(TIMER_ID, TIMER_PRESCALER, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, TIMER_INTERVAL_uS, true);
  timerAlarmEnable(timer);
}

void setupAHRS()
{
  ahrs.setup();
  ahrs.preflightCalibrate(false);
  ahrs.calibrateMagnetometer(MAGNETOMETER_BIAS_X, MAGNETOMETER_BIAS_Y, MAGNETOMETER_BIAS_Z,
                             MAGNETOMETER_SCALE_X, MAGNETOMETER_SCALE_Y, MAGNETOMETER_SCALE_Z);
}

void setup()
{
  setupTimer();
  setupBuzzer();
  Serial.begin(SERIAL_BAUD_RATE);
  setupAHRS();
  ahrs.averageQuaternion(initialQuaternion);
  ahrs.averageAngularVelocities(initialAngularVelocity);
  buzz(2);
  logSerial(LogVerbosityLevel::Info, "waiting for PiSerial...");
  waitForPiSerial();
  buzz(4);
  logSerial(LogVerbosityLevel::Info, "waiting for arm...");
  raspberryEsp32Interface.waitForArmCommand();
  logSerial(LogVerbosityLevel::Info, "arming...");
  buzz(2, 400);
  motorDriver.attachAndArm();
  buzz(6);
}

void setGainsFromRcTrimmers()
{
  controller.setQuaternionGain(-QUATERNION_XY_GAIN * RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN);
  controller.setAngularVelocityXYGain(-OMEGA_XY_GAIN * RADIO_TRIMMER_MAX_OMEGA_XY_GAIN);
  controller.setYawAngularVelocityGain(-OMEGA_Z_GAIN * RADIO_TRIMMER_MAX_OMEGA_Z_GAIN);
}

void loop()
{
  taskENTER_CRITICAL_ISR(&timerMux);
  timerState = !timerState;
  taskEXIT_CRITICAL_ISR(&timerMux);

  float quaternionImuData[4];
  float measuredAngularVelocity[3];
  float angularVelocityCorrected[3];

  if (!timerState)
    return;

  if (raspberryEsp32Interface.readPiData())
  {
    raspberryEsp32Interface.sendFlightDataToPi(
        IMUData[0], IMUData[1], IMUData[2], IMUData[3], IMUData[4], IMUData[5],
        motorFL, motorFR, motorBL, motorBR);
    failSafes.setLastRadioReceptionTime(micros());

    wasKill = isKill;
    isKill = raspberryEsp32Interface.kill();
    isThrottleStickDown = raspberryEsp32Interface.throttleReferencePercentage() < MAX_ARMING_THROTTLE_PERCENTAGE;
    logSerial(LogVerbosityLevel::Debug, ">> [%d, %d] >> %lu\n", isKill, wasKill, timestampLastKill);
  }

  if (!isKill && wasKill)
  {
    unsigned long timeElapsedSinceKill = millis() - timestampLastKill;
    if (timeElapsedSinceKill >= UN_KILL_KILL_SWITCH_TIMEOUT_IN_ms)
    {
      if (!isThrottleStickDown)
      {
        motorDriver.disarm();
        isKill = 1;
        return;
      }
    }
  }

  if (isKill || failSafes.isSerialTimeout())
  {
    if (!wasKill)
    {
      timestampLastKill = millis();
    }
    motorDriver.disarm();
    return;
  }

  ahrs.update();
  setGainsFromRcTrimmers();
  ahrs.quaternion(quaternionImuData);
  ahrs.angularVelocity(measuredAngularVelocity);

  angularVelocityCorrected[0] = measuredAngularVelocity[0] - initialAngularVelocity[0];
  angularVelocityCorrected[1] = measuredAngularVelocity[1] - initialAngularVelocity[1];
  angularVelocityCorrected[2] = measuredAngularVelocity[2] - initialAngularVelocity[2];

  float yawRateRC = raspberryEsp32Interface.yawRateReferenceRadSec();
  float deadZoneYawRate = 0.017;
  float yawRateReference = 0.;

  if (yawRateRC >= deadZoneYawRate)
  {
    yawRateReference = yawRateRC - deadZoneYawRate;
  }
  else if (yawRateRC <= -deadZoneYawRate)
  {
    yawRateReference = yawRateRC + deadZoneYawRate;
  }

  yawReferenceRad = ahrs.currentYawRad();

  Quaternion referenceQuaternion(
      yawReferenceRad,
      raspberryEsp32Interface.pitchReferenceAngleRad(),
      raspberryEsp32Interface.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;
  Quaternion attitudeError = referenceQuaternion - relativeQuaternion;

  IMUData[0] = relativeQuaternion[1];
  IMUData[1] = relativeQuaternion[2];
  IMUData[2] = relativeQuaternion[3];
  ahrs.getAccelerometerValues(IMUData + 3);

  float throttleRef = raspberryEsp32Interface.throttleReferencePWM();

  controller.motorPwmSignals(attitudeError,
                             angularVelocityCorrected,
                             yawRateReference,
                             throttleRef,
                             motorFL, motorFR, motorBL, motorBR);

#if UAV_TYPE == UAV_TYPE_HEXACOPTER
  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR, motorML, motorMR);
#else
  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);
#endif

  logSerial(LogVerbosityLevel::Debug, "PR: %f %f\n",
            IMUData[1], IMUData[2]);
}
