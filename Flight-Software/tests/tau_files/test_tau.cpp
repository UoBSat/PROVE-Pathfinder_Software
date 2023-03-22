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

class Tau
{
    public:
        void connect(bool ping, bool config);
};

void callbackTauImage(TauRawBitmap& tauRawBitmap, void* caller)
{

}

void Tau::connect(bool ping, bool config)
{
    std::cout << "Tau->connect()" << std::endl;

    tGr = new ThermalGrabber(callbackTauImage, this);

    char data[2];

    if (ping) 
    {   
        std::cout << "Starting a {ping} test..." << std::endl;

        // check if communication with camera is established
        tGr->sendCommand(0x00, 0, 0);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
    }
    if (config) 
    {   
        std::cout << "Starting a {config} test..." << std::endl;

        // check gain cmd -> request High Gain
        tGr->setGainMode(thermal_grabber::GainMode::HighGain);

        // check agc type cmd -> request Linear AGC
        data[0] = 0x00;
        data[1] = 0x05;
        tGr->sendCommand(0x13, &data[0], sizeof(data));

        // check contrast -> request 123
        data[0] = 0x00;
        data[1] = 123;
        tGr->sendCommand(0x14, &data[0], sizeof(data));

        // check brightness -> request 250
        data[0] = 0x00;
        data[1] = 250;
        tGr->sendCommand(0x15, &data[0], sizeof(data));  
    }

    std::cout << "Test program ends" << std::endl;

    delete tGr;
}

int main(int argc, char** argv)
{
    std::cout << "main:" << std::endl;

    Tau* tau = new Tau();

    // define expected program arguments
    bool ping = false;
    bool config = false;

    for (int i = 1; i < argc; i++) {
        std::string argString = argv[i]; 
        std::string configParamString = argString.substr(0, argString.find(":"));
        std::string configParamValueString = argString.erase(0, argString.find(":") + 1);

        char* configParamValueChar = new char[configParamValueString.length() + 1];
        strcpy(configParamValueChar, configParamValueString.c_str());

        if (argString == "ping") ping = true;
        if (argString == "config") config = true;
    }

    tau->connect(ping, config); 

    delete tau;

    return 0;
}
