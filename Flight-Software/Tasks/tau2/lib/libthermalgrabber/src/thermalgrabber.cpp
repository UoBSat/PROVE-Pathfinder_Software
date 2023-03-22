#include "thermalgrabber.h"
#include "tauinterface.h"
#include "tauimagedecoder.h"
#include "fastftdi.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>

ThermalGrabber::ThermalGrabber(callbackThermalGrabber ptr, void* caller)
{
    mTauInterface = NULL;
    mCallbackThermalGrabber = ptr;
    mCallingInstance = caller;
    mTauInterface = new TauInterface(static_callbackTauData, this);
    bool ok = mTauInterface->connect();

    if (!ok)
        std::cerr << "Connect camera failed" << std::endl;
}

ThermalGrabber::ThermalGrabber(callbackThermalGrabber ptr, void* caller, char* iSerialUSB)
{
    mTauInterface = NULL;
    mCallbackThermalGrabber = ptr;
    mCallingInstance = caller;
    mTauInterface = new TauInterface(static_callbackTauData, this);
    bool ok = mTauInterface->connect(iSerialUSB);

    if (!ok)
        std::cerr << "Connect camera failed" << std::endl;
}

ThermalGrabber::~ThermalGrabber()
{
    if (mTauInterface != NULL)
        delete mTauInterface;
}

void ThermalGrabber::static_callbackTauData(TauRawBitmap& tauRawBitmap, void* caller)
{
    //std::cout << "check " << tauRawBitmap.width << "/" << tauRawBitmap.height << " - " << tauRawBitmap.pps_timestamp << std::endl;

    ThermalGrabber* tg=(ThermalGrabber*)caller;

    tg->callbackTauData(tauRawBitmap);
}

void ThermalGrabber::callbackTauData(TauRawBitmap& tauRawBitmap)
{
    mCallbackThermalGrabber(tauRawBitmap, mCallingInstance);
}

void ThermalGrabber::sendCommand(char cmd, char* data, unsigned int data_len)
{
    if (mTauInterface != NULL)
        mTauInterface->sendCommand(cmd, data, data_len);
}

unsigned int ThermalGrabber::scale(unsigned int value, unsigned int lowBound, unsigned int upBound , unsigned int minOutput, unsigned int maxOutput)
{
    if( upBound == lowBound )
    {
        std::cerr << "Error: Boundaries equal: " << lowBound << ", " << upBound << std::endl;
        return 0;
    }

    if( value > 0 )
    {
        if( value <= lowBound )
        {
            return minOutput;
        }

        if( value >= upBound )
        {
            return maxOutput;
        }

        int res = ((maxOutput-minOutput) * (value-lowBound) / (upBound-lowBound)) + minOutput;

        if( res <= (int)minOutput )
        {
            res = minOutput;
        }
        else if( res >= (int)maxOutput )
        {
            res = maxOutput;
        }
        return res;
    }
    return 0;
}

void ThermalGrabber::changeWatchdogCount(int wait_time)
{
    if (wait_time == 0)
    {
        // Watchdog will be disabled
        std::cout << "WARNING: The watchdog will be disabled with parameter \"0\"!" << std::endl;
    }
    else if (wait_time < 5)
    {
        std::cout << "WARNING: A watchdog wait time below 5 seconds is generally not needed. Successfull init of the connection might not be possible with too low watchdog wait time!" << std::endl;
    }

    if (mTauInterface != NULL)
    {
        std::cout << "Watchdog wait time set to " << wait_time << " seconds" << std::endl;
        mTauInterface->setWatchdogTime(wait_time);
    }
}

void ThermalGrabber::convertTauRawBitmapToTauRGBBitmap(TauRawBitmap &tauRawBitmap, TauRGBBitmap &tauRGBBitmap)
{

    if ((tauRawBitmap.data != NULL && tauRawBitmap.width > 0 && tauRawBitmap.height > 0)
            &&
            (tauRawBitmap.width == tauRGBBitmap.width && tauRawBitmap.height == tauRGBBitmap.height))
    {
        for (int i=0; i<tauRawBitmap.height*tauRawBitmap.width; i++)
        {
            unsigned int val = tauRawBitmap.data[i];
            unsigned int s = scale(val, tauRawBitmap.min, tauRawBitmap.max, 0, 255);
            tauRGBBitmap.data[i*3] = s;
            tauRGBBitmap.data[i*3+1] = s;
            tauRGBBitmap.data[i*3+2] = s;
        }
    }
    else
    {
        std::cerr << "Error: Cannot convert TauData to TauImage" << std::endl;
    }
}

void ThermalGrabber::convertTauRawBitmapToTauRGBBitmapFusion(TauRawBitmap &tauRawBitmap, TauRGBBitmap &tauRGBBitmap)
{
    if ((tauRawBitmap.data != NULL && tauRawBitmap.width > 0 && tauRawBitmap.height > 0)
            &&
            (tauRawBitmap.width == tauRGBBitmap.width && tauRawBitmap.height == tauRGBBitmap.height))
    {
        for (int i=0; i<tauRawBitmap.height*tauRawBitmap.width; i++)
        {
            unsigned int val = tauRawBitmap.data[i];

            unsigned int r = 0;
            unsigned int g = 0;
            unsigned int b = 0;

            unsigned int colorRange = 100;
            unsigned int s = scale( val, tauRawBitmap.min, tauRawBitmap.max, 0, (5*colorRange)-1 );

            unsigned int dcr;
            unsigned int shiftFactor = 20;


            if( s < colorRange )
            {
                dcr = (s<<shiftFactor)/colorRange;
                r = (70*dcr)>>shiftFactor;
                g = (40*dcr)>>shiftFactor;
                b = (130*dcr)>>shiftFactor;
            }
            else if( s < 2*colorRange )
            {
                s -= colorRange;
                dcr = (s<<shiftFactor)/colorRange;
                r = 70 + ((140*dcr)>>shiftFactor);
                g = 40;
                b = 130;
            }
            else if( s < 3*colorRange )
            {
                s -= 2*colorRange;
                dcr = (s<<shiftFactor)/colorRange;
                r = 210 + ((30*dcr)>>shiftFactor);
                g = 40 + ((70*dcr)>>shiftFactor);
                b = 130 - ((90*dcr)>>shiftFactor);
            }
            else if( s < 4*colorRange )
            {
                s -= 3*colorRange;
                dcr = (s<<shiftFactor)/colorRange;
                r = 240 + ((14*dcr)>>shiftFactor);
                g = 110 + ((90*dcr)>>shiftFactor);
                b = 20 - ((10*dcr)>>shiftFactor);
            }
            else
            {
                s -= 4*colorRange;
                dcr = (s<<shiftFactor)/colorRange;
                r = 255;
                g = 200 + ((54*dcr)>>shiftFactor);
                b = 10 + ((244*dcr)>>shiftFactor);
            }

            tauRGBBitmap.data[i*3] = r;
            tauRGBBitmap.data[i*3+1] = g;
            tauRGBBitmap.data[i*3+2] = b;

        }
    }
    else
    {
        std::cerr << "Error: Cannot convert TauData to TauImage" << std::endl;
    }
}

void ThermalGrabber::convertTauRawBitmapToTauRGBBitmapRainbow(TauRawBitmap &tauRawBitmap, TauRGBBitmap &tauRGBBitmap)
{
    if ((tauRawBitmap.data != NULL && tauRawBitmap.width > 0 && tauRawBitmap.height > 0)
            &&
            (tauRawBitmap.width == tauRGBBitmap.width && tauRawBitmap.height == tauRGBBitmap.height))
    {
        for (int i=0; i<tauRawBitmap.height*tauRawBitmap.width; i++)
        {
            unsigned int val = tauRawBitmap.data[i];

            unsigned int r = 0;
            unsigned int g = 0;
            unsigned int b = 0;

            unsigned int colorRange = 100;
            unsigned int s = scale( val, tauRawBitmap.min, tauRawBitmap.max, 0, (8*colorRange)-1 );

            unsigned int dcr;
            unsigned int shiftFactor = 20;

            if( s < colorRange )
            {
                dcr = (s<<shiftFactor)/colorRange;

                r = ((216*dcr)>>shiftFactor);
                g = 0;
                b = ((212*dcr)>>shiftFactor);
            }
            else if( s < 2*colorRange )
            {
                s -= colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 216 - ((195*dcr)>>shiftFactor);
                g = 0 + ((3*dcr)>>shiftFactor);
                b = 212 - ((49*dcr)>>shiftFactor);
            }
            else if( s < 3*colorRange )
            {
                s -= 2*colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 21  - ((16*dcr)>>shiftFactor);
                g = 3   + ((215*dcr)>>shiftFactor);
                b = 163 + ((71*dcr)>>shiftFactor);
            }
            else if( s < 4*colorRange )
            {
                s -= 3*colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 5   - ((5*dcr)>>shiftFactor);
                g = 218 - ((134*dcr)>>shiftFactor);
                b = 234 - ((234*dcr)>>shiftFactor);
            }
            else if( s < 5*colorRange )
            {
                s -= 4*colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 0  + ((229*dcr)>>shiftFactor);
                g = 84 + ((143*dcr)>>shiftFactor);
                b = 0  + ((5*dcr)>>shiftFactor);
            }
            else if( s < 6*colorRange )
            {
                s -= 5*colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 229 - ((108*dcr)>>shiftFactor);
                g = 227 - ((218*dcr)>>shiftFactor);
                b = 5   - ((5*dcr)>>shiftFactor);
            }
            else if( s < 7*colorRange )
            {
                s -= 6*colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 121 + ((88*dcr)>>shiftFactor);
                g = 9   + ((36*dcr)>>shiftFactor);
                b = 0   + ((43*dcr)>>shiftFactor);
            }
            else if( s < 8*colorRange )
            {
                s -= 7*colorRange;
                dcr = (s<<shiftFactor)/colorRange;

                r = 209 + ((46*dcr)>>shiftFactor);
                g = 45  + ((210*dcr)>>shiftFactor);
                b = 43  + ((212*dcr)>>shiftFactor);
            }
            else
            {
                std::cout << "I shouldn't be here" << std::endl;
                // I shouldn't be here
                r = 0;
                g = 0;
                b = 0;
            }


            tauRGBBitmap.data[i*3] = r;
            tauRGBBitmap.data[i*3+1] = g;
            tauRGBBitmap.data[i*3+2] = b;
        }
    }
    else
    {
        std::cerr << "Error: Cannot convert TauData to TauImage" << std::endl;
    }
}

unsigned int ThermalGrabber::getResolutionWidth()
{
    // Try to derive resolution details from the camera part number.
    // This is a string with the general type information of the tau core.
    // Parse the string and try to translate it to number.
    unsigned int result = 0;

    if (mTauInterface != NULL)
    {
        result = mTauInterface->getWidth();
//        const char* cameraPartNumber = mTauInterface->getCameraPartNumber();

//        if (cameraPartNumber[0] != 0) // string ok?
//        {
//            std::string str = std::string(cameraPartNumber);
//            std::size_t pos = str.find('^');

//            if (pos!=std::string::npos && (pos+4)<str.length())
//            {
//                std::string strRes = str.substr(pos+3, 3);
//                std::istringstream(strRes) >> result;

//                if (result != 640 && result != 336 && result != 324 && result != 160)
//                    result = 0;
//            }
//        }
    }

    return result;
}

unsigned int ThermalGrabber::getResolutionHeight()
{
    // Try to derive resolution details from the camera part number.
    // This is a string with the general type information of the tau core.
    // Parse the string and try to translate it to number.
    unsigned int result = 0;

    if (mTauInterface != NULL)
    {
        result = mTauInterface->getHeight();
//        const char* cameraPartNumber = mTauInterface->getCameraPartNumber();

//        if (cameraPartNumber[0] != 0) // string ok?
//        {
//            std::string str = std::string(cameraPartNumber);
//            std::size_t pos = str.find('^');

//            if (pos!=std::string::npos && (pos+4)<str.length())
//            {
//                std::string strRes = str.substr(pos+3, 3);
//                std::istringstream(strRes) >> result;

//                if (result == 640)  // type 640x512
//                    result = 512;
//                else if (result == 336 || result == 324) // type 336x256 or 324x256
//                    result =256;
//                else if (result == 160) // type 160x128
//                    result = 128;
//            }
//        }
    }
    return result;
}

unsigned int ThermalGrabber::getCameraSerialNumber()
{
    if (mTauInterface != NULL)
        return mTauInterface->getCameraSerialNumber();

    return 0;
}

const char* ThermalGrabber::getCameraPartNumber() const
{
    if (mTauInterface != NULL)
        return mTauInterface->getCameraPartNumber();
    return NULL;
}

void ThermalGrabber::doFFC()
{
    if (mTauInterface != NULL)
        mTauInterface->doFFC();
    else
        std::cerr << "doFFC failed: No connection to tau core" << std::endl;
}

void ThermalGrabber::setGainMode(thermal_grabber::GainMode gm)
{
    if (mTauInterface != NULL)
    {
        switch (gm)
        {
        case thermal_grabber::GainMode::Automatic:
//            std::cout << "setGainMode to Automatic" << std::endl;
            mTauInterface->enableGainModeAutomatic();
            break;

        case thermal_grabber::GainMode::HighGain:
//            std::cout << "setGainMode to High" << std::endl;
            mTauInterface->enableGainModeHigh();
            break;

        case thermal_grabber::GainMode::LowGain:
//            std::cout << "setGainMode to Low" << std::endl;
            mTauInterface->enableGainModeLow();
            break;

        case thermal_grabber::GainMode::Manual:
//            std::cout << "setGainMode to Manual" << std::endl;
            mTauInterface->enableGainModeManual();
            break;

        default:
            std::cerr << "setGainMode with invalid parameter" << std::endl;
        }
    }
    else
        std::cerr << "setGainMode failed: No connection to tau core" << std::endl;
}

thermal_grabber::GainMode ThermalGrabber::getGainMode()
{
    mTauInterface->getGainMode();
}

void ThermalGrabber::enableTLinearHighResolution()
{
    if (mTauInterface != NULL)
    {
        mTauInterface->enableTLinear();
        mTauInterface->setTLinearHighResolution();
    }
    else
    {
        std::cerr << "setTLinearHighResolution failed: No connection to tau core" << std::endl;
    }
}

void ThermalGrabber::enableTlinearLowResolution()
{
    if (mTauInterface != NULL)
    {
        mTauInterface->enableTLinear();
        mTauInterface->setTlinearLowResolution();
    }
    else
    {
        std::cerr << "setTLinearLowResolution failed: No connection to tau core" << std::endl;
    }
}

void ThermalGrabber::disableTLinear()
{
    if (mTauInterface != NULL)
        mTauInterface->disableTLinear();
    else
        std::cerr << "disableTLinear failed: No connection to tau core" << std::endl;
}

void ThermalGrabber::enableInternalSyncByTau2CoreSyncOutOn()
{
    std::cout << "ThermalGrabber: enableInternalSyncByTau2CoreSyncOutOn" << std::endl;

    if (mTauInterface != NULL)
    {
        // No sync signal generation by TCGrabberUSB or sync signal from Pin 5 (external sync input)
        mTauInterface->disableExternalSynchronization();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        // Tau 2 Core generates sync signal by its own and forwards it to Pin 6 (external sync output) of TCGrabberUSB
        mTauInterface->setExternalSyncToMaster();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    else
        std::cerr << "enableInternalSyncByTau2CoreSyncOutOn failed: No connection to tau core" << std::endl;
}

void ThermalGrabber::enableInternalSyncByTau2CoreSyncOutOff()
{
    std::cout << "ThermalGrabber: enableInternalSyncByTau2CoreSyncOutOff" << std::endl;

    if (mTauInterface != NULL)
    {
        // No sync signal generation by TCGrabberUSB or sync signal from Pin 5 (external sync input)
        mTauInterface->disableExternalSynchronization();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        // Tau 2 Core generates sync signal by its own without forwarding it to Pin 6 (external sync output) of TCGrabberUSB
        mTauInterface->setExternalSyncToDisabled();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    else
        std::cerr << "enableInternalSyncByTau2CoreSyncOutOff failed: No connection to tau core" << std::endl;
}

void ThermalGrabber::enableInternalSyncByTCGrabberUSB(uint32_t frequency_parameter, uint32_t count)
{
    std::cout << "ThermalGrabber: enableInternalSyncByTCGrabberUSB" << std::endl;

    if (mTauInterface != NULL)
    {
        // Tau 2 Core as slave (gets sync signal from TCGrabberUSB)
        mTauInterface->setExternalSyncToSlave();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        // TCGrabberUSB generates sync signal and forwards it to Pin 6 (external sync output)
        mTauInterface->enableExternalSynchronizationMasterMode(frequency_parameter, count);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    else
        std::cerr << "enableInternalSyncByTCGrabberUSB failed: No connection to tau core" << std::endl;
}

void ThermalGrabber::enableExternalSyncAsSlave()
{
    if (mTauInterface != NULL)
    {

        // Tau 2 Core as slave (gets sync signal from Pin 5 (sync signal input) of TCGrabberUSB
        mTauInterface->setExternalSyncToSlave();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        // Pin 5 (external sync input) of TCGrabberUSB is sync signal source
        //mTauInterface->disableExternalSynchronization(); // this remove
        mTauInterface->enableExternalSynchronizationSlaveMode();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    else
        std::cerr << "enableExternalSyncAsSlave failed: No connection to tau core" << std::endl;
}
