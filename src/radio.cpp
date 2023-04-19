#include "radio.hpp"

namespace bzzz
{   
    int channelData[16]; // A 16 int array to store the 16 channels of data sent from the Pi (receiver) via serial 

    void readPiData(void)
    {
        String allDataFromPi;
        
        if (Serial.available() > 0) 
        {
            allDataFromPi = Serial.readStringUntil('\n'); //all 16 channels read by ESP32 

            for (int i = 0; i < 16; i++) 
            {
                // take the substring from the start to the first occurence of a comma, convert it to int and save it in the array
                channelData[i] = allDataFromPi.substring(1, allDataFromPi.indexOf(",")).toInt();

                //cut the data string after the first occurence of a comma
                allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);
            }
        }
    }

    void readRadioData(int &radioThrottle, int &radioRoll, int &radioPitch, int &radioYaw, int &radioSwitchC,
    int &radioVRA, int &radioVRC, int &radioVRB, int &radioArm, int &radioKill, int &radioSwitchD, int &radioVRE) 
    {
        // reformat receiver values to match radio (RadioLink AT10)
        radioThrottle = channelData[2];
        radioRoll = channelData[3];
        radioPitch = channelData[1];
        radioYaw = channelData[0];
        radioSwitchC = channelData[4];
        radioVRA = channelData[5];
        radioVRC = channelData[6];
        radioVRB = channelData[7];
        radioArm = channelData[8]; // radioSwitchB
        radioKill = channelData[9]; // radioSwitchA
        radioSwitchD = channelData[10];
        radioVRE = channelData[11];
    }

}
