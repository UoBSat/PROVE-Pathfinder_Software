#include "thermalgrabber.h"
#include <stdbool.h>
#include <cstdlib>
#include <iostream>
#include <chrono>
#include <thread>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <fstream>
#include <typeinfo>

using namespace std;

ThermalGrabber* tGr;
class Test
{
public:
    void test(int cppduration, char* gainMode, char* agcType, char* contrast, char* brightness);
};

void callbackTauImage(TauRawBitmap& tauRawBitmap, void* caller)
{
    //std::cout << "updateTauRawBitmap -> w/h: " << tauRawBitmap.width << "/" << tauRawBitmap.height << " min/max: " << tauRawBitmap.min << "/" << tauRawBitmap.max << std::endl;
    
    static int fileNo = 0;
    int i = 0;

    char myarray[50];

    int n=sprintf(myarray,"pass-1-file-%d.dat",fileNo);

    printf("%s",myarray);

    ofstream fout(myarray, ios::binary);// open image file
    // when the headers alone are written to the file, 54 bytes are written which is to be expected
    while(i < tauRawBitmap.width * tauRawBitmap.height)         {
            //std::cout << i << "\t"<< tauRawBitmap.data[i] << std::endl; //print pixel value (really slows things down)
            fout.write((char*)&tauRawBitmap.data[i], sizeof(tauRawBitmap.data[i])); //save pixel value
            i++;
        }
    fileNo ++;
    fout.close();
}
void Test::test(int cppduration, char* gainMode, char* agcType, char* contrast, char* brightness)
{
    std::cout << "Test" << std::endl;
    tGr = new ThermalGrabber(callbackTauImage, this);

    // configurations
    char data[2];

    // get default configuration values
    // TODO: delete this later
    std::cout << "Get Gain Mode..." << std::endl;
    tGr->sendCommand(0x0A, 0, 0);

    std::cout << "Get AGC Type..." << std::endl;
    tGr->sendCommand(0x13, 0, 0);

    std::cout << "Get Contrast.." << std::endl;
    tGr->sendCommand(0x14, 0, 0);

    std::cout << "Get Brightness.." << std::endl;
    tGr->sendCommand(0x15, 0, 0);


    if (strlen(gainMode) > 0) 
    {   
        std::cout << "Setting Gain Mode to {" << gainMode << "}..." << std::endl;

        // set gain mode
        if (std::string{gainMode} == "Automatic") tGr->setGainMode(thermal_grabber::GainMode::Automatic);
        else if (std::string{gainMode} == "Low") tGr->setGainMode(thermal_grabber::GainMode::LowGain);
        else if (std::string{gainMode} == "High") tGr->setGainMode(thermal_grabber::GainMode::HighGain);
        else if (std::string{gainMode} == "Manual") tGr->setGainMode(thermal_grabber::GainMode::Manual);
        else 
        {
            std::cout << "Gain Mode value {" << gainMode << "} was not recognized!" << std::endl;
        }   
    }
    if (strlen(agcType) > 0) 
    {   
        std::cout << "Setting AGC Type to {" << agcType << "}..." << std::endl;

        // set agc type
        if (std::string{agcType} == "PlateauHistogram") 
        {
            data[0] = 0x00;
            data[1] = 0x00;
            tGr->sendCommand(0x13, &data[0], sizeof(data));
        }
        else if (std::string{agcType} == "OnceBright") 
        {
            data[0] = 0x00;
            data[1] = 0x01;
            tGr->sendCommand(0x13, &data[0], sizeof(data));
        }
        else if (std::string{agcType} == "AutoBright") 
        {
            data[0] = 0x00;
            data[1] = 0x02;
            tGr->sendCommand(0x13, &data[0], sizeof(data));
        }
        else if (std::string{agcType} == "Manual") 
        {
            data[0] = 0x00;
            data[1] = 0x03;
            tGr->sendCommand(0x13, &data[0], sizeof(data));
        }
        else if (std::string{agcType} == "LinearAGC") 
        {
            data[0] = 0x00;
            data[1] = 0x05;
            tGr->sendCommand(0x13, &data[0], sizeof(data));
        }
        else 
        {
            std::cout << "AGC Type value {" << agcType << "} was not recognized!" << std::endl;
        }   
    }
    if (strlen(contrast) > 0) 
    {   
        std::cout << "Setting Contrast to {" << contrast << "}..." << std::endl;

        int contrastInt = atoi(contrast);

        // set contrast
        if (contrastInt >= 0 && contrastInt <= 255) 
        {
            data[0] = 0x00;
            data[1] = contrastInt;
            tGr->sendCommand(0x14, &data[0], sizeof(data));
        }
        else 
        {
            std::cout << "Contrast value {" << contrast << "} was not recognized!" << std::endl;
        }   

        //std::cout << "Get Contrast.." << std::endl;
        //tGr->sendCommand(0x14, 0, 0);
    }
    if (strlen(brightness) > 0) 
    {   
        std::cout << "Setting Brightness to {" << brightness << "}..." << std::endl;

        int brightnessInt = atoi(brightness);

        // set brightness
        if (brightnessInt >= 0 && brightnessInt <= 16383) 
        {
            data[0] = 0x00;
            data[1] = brightnessInt;
            tGr->sendCommand(0x15, &data[0], sizeof(data));
        }
        else 
        {
            std::cout << "Brightness value {" << brightness << "} was not recognized!" << std::endl;
        }   

        //std::cout << "Get Brightness.." << std::endl;
        //tGr->sendCommand(0x15, 0, 0);
    }

    std::cout << "Setting Watchdog Count to {0}..." << std::endl;
    tGr->changeWatchdogCount(0);

    unsigned int mWidth = tGr->getResolutionWidth();
    unsigned int mHeight = tGr->getResolutionHeight();
    std::cout << "Resolution w/h " << mWidth << "/" << mHeight << std::endl;
    // run demo for length of imaging pass
    std::cout << "program duration " << cppduration << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(cppduration));
    std::cout << "program ends " << std::endl;
    delete tGr;
}
int main(int argc, char** argv)
{
    std::cout << "main:" << std::endl;
    {
        Test* t = new Test();

        // capture duration is the 1st argument
        int duration = atoi(argv[1]);

        // all other arguments are configuration arguments
        char* gainMode = "";
        char* agcType = "";
        char* contrast = "";
        char* brightness = "";

        for (int i = 2; i < argc; i++) {
            std::string argString = argv[i]; 
            std::string configParamString = argString.substr(0, argString.find(":"));
            std::string configParamValueString = argString.erase(0, argString.find(":") + 1);

            char* configParamValueChar = new char[configParamValueString.length() + 1];
            strcpy(configParamValueChar, configParamValueString.c_str());

            if (configParamString == "gain_mode") gainMode = configParamValueChar;
            if (configParamString == "agc_type") agcType = configParamValueChar;
            if (configParamString == "contrast") contrast = configParamValueChar;
            if (configParamString == "brightness") brightness = configParamValueChar;
        }

        t->test(duration, gainMode, agcType, contrast, brightness); 
        delete t;
    }
    return 0;
}
