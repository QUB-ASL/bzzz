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

    // check for new measurements from the IMU
    if (ahrs.update())
    {
        ahrs.eulerAngles(drone_euler);
        const float rad2deg = 57.2957795;
        sprintf(buffer, "%.2f\t%.2f\t%.2f",
                rad2deg * drone_euler[0],
                rad2deg * drone_euler[1],
                rad2deg * drone_euler[2]);
        Serial.println(buffer);
    }
}