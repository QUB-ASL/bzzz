#include "radio.hpp"

namespace bzzz
{   
    /**
     * Channel    Variable
     * 1          yaw rate
     * 2          pitch
     * 3          throttle
     * 4          roll
     * 5          Switch C
     * 6          Trimmer VRA 
     * 7          Trimmer VRC
     * 8          Trimmer VRB
     * 9          Switch B (for arming)
     * 10         Switch A (kill)
     * 11         Switch D
     * 12         Trimmer VRE
     */
    static int channelData[16];

    void readPiData(void)
    {
        String allDataFromPi;
        
        if (Serial.available() > 0) 
        {
            allDataFromPi = Serial.readStringUntil('\n');

            for (int i = 0; i < 16; i++) 
            {
                // take the  substring from the start to the first occurence of a comma, convert it to int and save it in the array
                channelData[i] = allDataFromPi.substring(1, allDataFromPi.indexOf(",")).toInt();
    
                //cut the channelData string after the first occurence of a comma
                allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);
            }
        }
    }

    void readRadioData(
        int &radioThrottle, 
        int &radioRoll, 
        int &radioPitch, 
        int &radioYawRate, 
        int &radioSwitchC,
        int &radioVRA, 
        int &radioVRC, 
        int &radioVRB, 
        int &radioArm, 
        int &radioKill, 
        int &radioSwitchD, 
        int &radioVRE)
    {
        // reformat receiver values  to match radio (RadioLink AT10)
        radioThrottle = channelData[2];
        radioRoll = channelData[3];
        radioPitch = channelData[1];
        radioYawRate = channelData[0];  
        radioSwitchC = channelData[4];
        radioVRA = channelData[5];
        radioVRC = channelData[6];
        radioVRB = channelData  [7];
        radioArm = channelData[ 8]; // radioSwitchB
        radioKill = channelData[9]  ; // radioSwitchA
        radioSwitchD = channelData[10];
        radioVRE = channelData[11];
    }


    static float mapRadioToAngle(float x){
        return -PITCH_MAX_RAD + (x - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN)*2*PITCH_MAX_RAD;
    }

    float pitchReferenceAngleRad(){ 
        return mapRadioToAngle(channelData[1]);
    }

    float rollReferenceAngleRad(){ 
        return mapRadioToAngle(channelData[3]);
    }

    float yawRateReferenceRadSec() 
    {
        return -RADIO_MAX_YAW_RATE_RAD_SEC + 
            (channelData[0] - RADIO_STICK_MIN)
                /(RADIO_STICK_MAX - RADIO_STICK_MIN)*2*RADIO_MAX_YAW_RATE_RAD_SEC;
    }

    float throttleReferencePercentage() {
        return  (channelData[2] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    bool armed()
    {
        return channelData[8] >= 1500;
    }

    bool kill()
    {
        return channelData[9] <= 500;
    }

    ThreeWaySwitch switchC()
    {
        int switchValue = channelData[4];
        if (switchValue <= 450) {
            return ThreeWaySwitch::DOWN;
        } else if (switchValue <= 1200) {
            return ThreeWaySwitch::MID;
        }
        return ThreeWaySwitch::UP;
    }

    bool switchD(){
        return channelData[4];
    }

    float trimmerVRAPercentage(){
        return (channelData[5] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    float trimmerVRCPercentage(){
        return (channelData[6] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    float trimmerVRBPercentage(){
        return (channelData[7] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    float trimmerVREPercentage(){
        return (channelData[11] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

}
