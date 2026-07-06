#include <Arduino.h>

#include "ahrs.hpp"
#include "quaternion.hpp"
#include "fdi.hpp"

using namespace bzzz;

AHRS ahrs;

Quaternion initialQuaternion;

float initialAngularVelocity[3];

ModelBasedBayesianFDI fdi;

void setup()
{
    Serial.begin(115200);

    delay(2000);

    Serial.println();
    Serial.println("==========================================");
    Serial.println(" Bayesian Model-Based FDI Hardware Test");
    Serial.println("==========================================");

    ahrs.setup();

    ahrs.preflightCalibrate(false);

    ahrs.averageQuaternion(initialQuaternion);

    ahrs.averageAngularVelocities(initialAngularVelocity);

    Serial.println("IMU Initialized.");
}

void loop()
{
    //-----------------------------------------
    // Read IMU
    //-----------------------------------------

    ahrs.update();

    float q[4];

    float omega[3];

    ahrs.quaternion(q);

    ahrs.angularVelocity(omega);

    //-----------------------------------------
    // Build measured vehicle state
    //-----------------------------------------

    VehicleState measured;

    measured.attitude = Quaternion(q);

    measured.omega[0] = omega[0] - initialAngularVelocity[0];
    measured.omega[1] = omega[1] - initialAngularVelocity[1];
    measured.omega[2] = omega[2] - initialAngularVelocity[2];

    //-----------------------------------------
    // Dummy motor commands
    //-----------------------------------------

    float motorCommand[6];

    motorCommand[0] = 1500;
    motorCommand[1] = 1500;
    motorCommand[2] = 1500;
    motorCommand[3] = 1500;
    motorCommand[4] = 1500;
    motorCommand[5] = 1500;

    //-----------------------------------------
    // Execute Bayesian FDI
    //-----------------------------------------

    fdi.update(measured, motorCommand);

    //-----------------------------------------
    // Print results
    //-----------------------------------------

    Serial.println("-----------------------------------------");

    Serial.print("Residual Cost : ");
    Serial.println(fdi.latestResidualCost(),6);

    Serial.print("Window Cost   : ");
    Serial.println(fdi.latestWindowCost(),6);

    const auto& P = fdi.latestPosterior();

    for(int i=0;i<NUM_HYPOTHESES;i++)
    {
        Serial.print("P(H");
        Serial.print(i);
        Serial.print(") = ");
        Serial.println(P[i],6);
    }

    Serial.print("MAP Decision  : ");

    int motor = fdi.failedMotor();

    if(motor==0)
        Serial.println("Healthy");
    else
    {
        Serial.print("Motor ");
        Serial.println(motor);
    }

    Serial.print("Confidence   : ");
    Serial.println(fdi.confidence(),4);

    Serial.print("Fault Detected : ");

    if(fdi.faultDetected())
        Serial.println("YES");
    else
        Serial.println("NO");

    delay(500);
}