#include "radio.hpp"

namespace bzzz
{   
    int data[16];

    void readPiData(void)
    {
        String dataFromClient;
        
        if (Serial.available() > 0) 
        {
            dataFromClient = Serial.readStringUntil('\n');

            for (int i = 0; i < 16; i++) 
            {
                // take the substring from the start to the first occurence of a comma, convert it to int and save it in the array
                data[i] = dataFromClient.substring(1, dataFromClient.indexOf(",")).toInt();

                //cut the data string after the first occurence of a comma
                dataFromClient = dataFromClient.substring(dataFromClient.indexOf(",") + 1);
            }
        }
    }

    void readRadioData(int &radioThrottle, int &radioRoll, int &radioPitch, int &radioYaw, int &radioSwitchC,
    int &radioVRA, int &radioVRC, int &radioVRB, int &radioArm, int &radioKill, int &radioSwitchD, int &radioVRE) 
    {
        readPiData();
        // reformat receiver values to match radio (RadioLink AT10)
        radioThrottle = data[2];
        radioRoll = data[3];
        radioPitch = data[1];
        radioYaw = data[0];
        radioSwitchC = data[4];
        radioVRA = data[5];
        radioVRC = data[6];
        radioVRB = data[7];
        radioArm = data[8]; // radioSwitchB
        radioKill = data[9]; // radioSwitchA
        radioSwitchD = data[10];
        radioVRE = data[11];
    }

}
