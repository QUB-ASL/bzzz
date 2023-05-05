#include <Arduino.h>
#include "ahrs.hpp"

bzzz::AHRS ahrs;

void setup()
{
    Serial.begin(115200);
    ahrs.setup();
    ahrs.preflightCalibrate();
}

void loop()
{
    char buffer[40];
    float drone_euler[3] = {0};
    float quaternion[4] = {0};
    float angularVelocity[3] = {0};

    //** UNCOMMENT THE TEST TO CARRY OUT **//

    // // TEST TO CHECK EULER ANGLES
    // // check for new measurements from the IMU
    // if (ahrs.update()) 
    // {
    //     ahrs.eulerAngles(drone_euler);
    //     const float rad2deg = 57.2957795;
    //     sprintf(buffer, "%.2f\t%.2f\t%.2f",
    //             rad2deg * drone_euler[0],
    //             rad2deg * drone_euler[1],
    //             rad2deg * drone_euler[2]);
    //     Serial.println(buffer);
    // }

    // // TEST TO CHECK QUATERNION
    // if (ahrs.update()) 
    // {
    //     ahrs.quaternion(quaternion);
    //     sprintf(buffer, "%.2f\t%.2f\t%.2f\t%.2f",
    //             quaternion[0],
    //             quaternion[1],
    //             quaternion[2],
    //             quaternion[3]);
    //     Serial.println(buffer);
    // }

    // // TEST TO CHECK ANGULAR VELOCITIES
    // if (ahrs.update()) 
    // {
    //     ahrs.angularVelocity(angularVelocity);
    //     sprintf(buffer, "%.2f\t%.2f\t%.2f",
    //           angularVelocity[0],
    //           angularVelocity[1],
    //           angularVelocity[2]);
    //     Serial.println(buffer);
    // }
}