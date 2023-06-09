#include <iostream>
#include <fstream>

#include <fastftdi.h>

#include <iostream>
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#include <thermograbber.h>
#include <unistd.h>
#include <thread>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

#define MAX_FRAME_BUFFER_SIZE 384000 // 640x600 max
#define MIN_FRAME_BUFFER_SIZE 20480 // 160x128

using namespace std;

struct ThermoGrabberPrivate
{
    FTDIDevice dev;
    int stop;
    int stopped; // to check if thread has reached end (last transfers done)
    int byte_count;
    int parser_state;
    int bytecount;
    int linecount;
    int size;
    int frames;
    int uart_in_size;
    int uart_in_counter;
    unsigned char uart_in_buffer[256];
    struct timespec starttime;
    uint16_t framebuffer[MAX_FRAME_BUFFER_SIZE];
};

ThermoGrabber::ThermoGrabber() : grabberRuns(false), mPPSTimestamp(0)
{
    tgP= new ThermoGrabberPrivate;
    tgP->stop=0;
    tgP->stopped=0;
    tgP->byte_count=0;
    tgP->parser_state=0;
    tgP->bytecount=0;
    tgP->linecount=0;
    tgP->size=0;
    tgP->frames=0;
    tgP->uart_in_size=0;
    tgP->uart_in_counter=0;
}

ThermoGrabber::~ThermoGrabber()
{
    delete tgP;
}

void ThermoGrabber::reenableFTDI()
{
    tgP->stop = 0;
    tgP->stopped = 0;
}

void ThermoGrabber::stopGrabber()
{

#ifdef USE_FTDI

    tgP->stop=1;
    FT_Close(&tgP->dev);

#else
    std::cout << "Setting stop order" << std::endl;
    tgP->stop=1;

    //std::this_thread::sleep_for(std::chrono::milliseconds(1000)); remove test
    int attempts = 5;

    // Check if transfers are cleaned up and fastftdi::FTDIDevice_ReadStream()
    // reached end.
    // If there's no reaction until attempts reach zero ignore it and go on
    // with device close.
    while (attempts > 0)
    {
        attempts--;

        // wait time is intentionally in front of "stopped"-check
        // to be on the safe side.
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));

        if (tgP->stopped)
            break;
    }

    std::cout << "Requesting device close" << std::endl;
    FTDIDevice_Close(&tgP->dev);

#endif

}

int ThermoGrabber::static_readCallback(uint8_t *buffer, int length, void *progress, void *userdata)
{
    ThermoGrabber * tg=(ThermoGrabber*) userdata;
    return tg->readCallback(buffer,length,progress);
}

int ThermoGrabber::readCallback(uint8_t *buffer, int length, void *)
{

    if( tgP->byte_count==0)
    {
#ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time
        struct timespec ts;
        clock_serv_t cclock;
        mach_timespec_t mts;
        host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &cclock);
        clock_get_time(cclock, &mts);
        mach_port_deallocate(mach_task_self(), cclock);
        ts.tv_sec = mts.tv_sec;
        ts.tv_nsec = mts.tv_nsec;
        tgP->starttime = ts;
#else
        clock_gettime(CLOCK_REALTIME, &tgP->starttime);
#endif
    }

    tgP->byte_count+=length;

    for(int i=0;i<length;i++)
    {
        switch( tgP->parser_state) // state machine searches 'TEAX' or 'UART' header and following bytes
        {

        case 0:
        default:

            if(buffer[i]=='T')
            {
                tgP->parser_state=1;
            }
            else if(buffer[i]=='U')
            {
                tgP->parser_state=10;

            }
            break;

        case 1:

            if (buffer[i]=='E')
            {
                tgP->parser_state=2;
            }
            else
            {
                tgP->parser_state=0;
            }
            break;

        case 2:

            if(buffer[i]=='A')
            {
                tgP->parser_state=3;
            }
            else
            {
                tgP->parser_state=0;
            }
            break;


        case 3:

            if(buffer[i]=='X')
            {
                tgP->parser_state=4;
            }
            else
            {
                tgP->parser_state=0;
            }
            break;

        case 4:
            tgP->size=buffer[i];
            tgP->parser_state=5;
            break;

        case 5:
            tgP->size|=buffer[i]<<8;
            tgP->parser_state=6;
            break;

        case 6:
            tgP->size|=buffer[i]<<16;
            tgP->parser_state=7;
            break;

        case 7:
            tgP->size|=buffer[i]<<24;

            // check for reasonable size of data frame
            if ((tgP->size < MAX_FRAME_BUFFER_SIZE) && (tgP->size > MIN_FRAME_BUFFER_SIZE))
                tgP->parser_state=8;    // size ok -> go on
            else
                tgP->parser_state=0;    // reset state machine
            break;

        case 8:

            if(tgP->bytecount>=(tgP->size*2))
            {
                tgP->parser_state=0;
                processVideoData(tgP->framebuffer, tgP->bytecount/2);
                //usleep(10000);
                std::this_thread::sleep_for(std::chrono::microseconds(10000));
                tgP->bytecount=0;
                tgP->frames++;
            }
            else
            {
                if((tgP->bytecount%2)==0)
                {
                    tgP->framebuffer[tgP->bytecount/2]=buffer[i];
                }
                else
                {
                    tgP->framebuffer[tgP->bytecount/2]|=buffer[i]<<8;
                }
                tgP->bytecount++;
            }
            break;

        case 10:

            if(buffer[i]=='A')
            {
                tgP->parser_state=11;
            }
            else
            {
                tgP->parser_state=0;
            }
            break;

        case 11:

            if(buffer[i]=='R')
            {
                tgP->parser_state=12;
            }
            else
            {
                tgP->parser_state=0;
            }
            break;

        case 12:

            if(buffer[i]=='T')
            {
                tgP->parser_state=13;
            }
            else
            {
                tgP->parser_state=0;
            }
            break;

        case 13:
            tgP->uart_in_size=buffer[i];
            tgP->uart_in_counter=0;
            tgP->parser_state=14;
            break;

        case 14:
            tgP->uart_in_buffer[tgP->uart_in_counter++]=buffer[i];

            if((tgP->uart_in_counter+1)>=tgP->uart_in_size)
            {
                processUartData(tgP->uart_in_buffer,tgP->uart_in_size);
                tgP->parser_state=0;
            }
            break;
        }
    }
    return tgP->stop;
}


int ThermoGrabber::runGrabber(char* iSerialUSB)
{
    //    FTDI_PrintDeviceList();

    int err = FTDIDevice_Open(&(tgP->dev), iSerialUSB);

    if (err)
    {
        std::cerr <<  "USB: Error opening device" << std::endl;
        return 1;
    }



    std::cout << "Resetting ftdi transfer mode" << std::endl;
    // reenable async mode
    err = FTDIDevice_SetMode(&(tgP->dev),
                             FTDI_INTERFACE_A,
                             FTDI_BITMODE_RESET, // reset
                             0xFF,
                             0);

    if (err)
    {
        std::cerr << "USB: Error SetMode\n";
        return 1;
    }


    std::cout << "Setting synchronous mode" << std::endl;
    // enable sync mode
    err = FTDIDevice_SetMode(&(tgP->dev),
                             FTDI_INTERFACE_A,
                             FTDI_BITMODE_SYNC_FIFO,
                             0xFF,
                             0);
    if (err)
    {
        std::cerr << "USB: Error SetMode\n";
        return 1;
    }

    //    FTDIDevice_WriteByteSync(&(tgP->dev),
    //                             FTDI_INTERFACE_A,
    //                             0x00); // Cmd: NO_OP

    // Now TG usb setup is done
    grabberRuns = true;

    // To keep track of the FTDIDevice_ReadStream return below
    tgP->stopped = 0;

    err = FTDIDevice_ReadStream(&(tgP->dev), // dev
                                FTDI_INTERFACE_A, // interface
                                (int (*)(uint8_t*, int, FTDIProgressInfo*, void*))static_readCallback,
                                this, // userdata
                                8, // packetsPerTransfer
                                256); // numTransfers

    // If FTDIDevice_ReadStream returned provide this info in tgP->stopped variable
    tgP->stopped = 1;

    //-------------------------------------------------------------------------
    // TEST

    //#ifdef WIN32

    //    // Change the ftdi mode from ft245 to ft232 on exit.
    //    // This way we keept compatible with config software.
    //    std::cout << std::endl << "Change mode on windows exit" << std::endl;

    //    err = FTDIDevice_Open(&(tgP->dev), iSerialUSB);

    //    err = FTDIDevice_SetMode(&(tgP->dev),
    //                             FTDI_INTERFACE_A,
    //                             FTDI_BITMODE_BITBANG, //FTDI_BITMODE_SYNC_FIFO,
    //                             0xFF,
    //                             0);
    //    if (err)
    //    {
    //        std::cerr << "USB: Error SetMode\n";
    //        return 1;
    //    }
    //    else
    //        std::cout << "Device mode reset on exit done" << std::endl;


    //#endif


    grabberRuns = false;

    //---------------------------------------------------------
    // This has to be enabled if working without watchdog!!!
    //FTDIDevice_Close(&(tgP->dev));

    return 0;
}


void ThermoGrabber::writeUartHeader(uint8_t* buffer, uint8_t dataSize)
{
    buffer[0]='U';
    buffer[1]='A';
    buffer[2]='R';
    buffer[3]='T';
    buffer[4]=dataSize;
}

void ThermoGrabber::sendUartData(uint8_t* buffer, uint32_t length)
{
    uint8_t out_buffer[128];

    if((length+5)>(sizeof(out_buffer)))
    {
        std::cerr << "sendUartData: overflow: can not send data" << std::endl;
    }

    writeUartHeader(out_buffer,length);
    memcpy(out_buffer+5,buffer,length);

    int result = FTDIDevice_Write(&(tgP->dev),
                                  FTDI_INTERFACE_A,
                                  out_buffer,
                                  length+5,
                                  0);
}

void ThermoGrabber::writeSyncHeader(uint8_t* buffer)
{
    buffer[0]='S';
    buffer[1]='Y';
    buffer[2]='N';
    buffer[3]='A';
}

void ThermoGrabber::sendSyncValues(uint8_t syncMode, uint32_t time, uint32_t count)
{
    uint8_t buffer[32];

    writeSyncHeader(buffer);
    buffer[4]=count&0xFF;
    buffer[5]=((count>>8)&0x7F)|((time&0x01)<<7);
    buffer[6]=(time>>1);
    buffer[7]=((time>>9)&0x3F)|((syncMode&0x03)<<6);

    int result = FTDIDevice_Write(&(tgP->dev),
                                  FTDI_INTERFACE_A,
                                  buffer,
                                  8,
                                  0);
}

void ThermoGrabber::setSyncModeNoExternalSyncOrMaster()
{
    sendSyncValues(0, 0, 0);
}

void ThermoGrabber::setSyncModeCameraSlave()
{
    sendSyncValues(1, 0, 0);
}

void  ThermoGrabber::setSyncModeGrabberMaster(uint32_t freq, uint32_t count)
{
    // Clock with 2kHz

    // Signal generator:
    // Timebase 500us (2kHz)

    // Calc:
    // 25.0Hz -> 250 (fixed point with factor 10x)
    // 20000/250=80

    // Check:
    // 80*500us=0.04
    // 1/0.04=25Hz
    uint32_t time=20000/freq;

    sendSyncValues(2, time-1, count);
}



