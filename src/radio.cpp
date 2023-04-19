#include "radio.hpp"

namespace bzzz
{   
    Radio::Radio(){};

    void Radio::readPiData(void)
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
                //Serial.print(channelData[i]);
                //Serial.print(", ");
            }
            //Serial.println(".");

        }
    }

    void Radio::readRadioData(
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


    float Radio::mapRadioToAngle(float x){
        return -PITCH_MAX_RAD + (x - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN)*2*PITCH_MAX_RAD;
    }

    float Radio::pitchReferenceAngleRad(){ 
        return mapRadioToAngle(channelData[1]);
    }

    float Radio::rollReferenceAngleRad(){ 
        return mapRadioToAngle(channelData[3]);
    }

    float Radio::yawRateReferenceRadSec() 
    {
        return -RADIO_MAX_YAW_RATE_RAD_SEC + 
            (channelData[0] - RADIO_STICK_MIN)
                /(RADIO_STICK_MAX - RADIO_STICK_MIN)*2*RADIO_MAX_YAW_RATE_RAD_SEC;
    }

    float Radio::throttleReferencePercentage() {
        return  (float)(channelData[2] - RADIO_STICK_MIN)/ ((float)(RADIO_STICK_MAX - RADIO_STICK_MIN));
    }

    bool Radio::armed()
    {
        return channelData[8] >= 1500;
    }

    bool Radio::kill()
    {
        return channelData[9] <= 500;
    }

    ThreeWaySwitch Radio::switchC()
    {
        int switchValue = channelData[4];
        if (switchValue <= 450) {
            return ThreeWaySwitch::DOWN;
        } else if (switchValue <= 1200) {
            return ThreeWaySwitch::MID;
        }
        return ThreeWaySwitch::UP;
    }

    bool Radio::switchD(){
        return channelData[4];
    }

    float Radio::trimmerVRAPercentage(){
        return (channelData[5] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    float Radio::trimmerVRCPercentage(){
        return (channelData[6] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    float Radio::trimmerVRBPercentage(){
        return (channelData[7] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

    float Radio::trimmerVREPercentage(){
        return (channelData[11] - RADIO_STICK_MIN)/(RADIO_STICK_MAX - RADIO_STICK_MIN);
    }

}
