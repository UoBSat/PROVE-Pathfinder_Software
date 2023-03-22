#ifndef THERMALGRABBER_H
#define THERMALGRABBER_H

#define LOG

#include <inttypes.h>

class TauInterface;

//! Container for raw tau bitmap.
/*!
*   The "width" and "height" paramter inform about the size of the bitmap.
*   Every pixel value of the tau core has 14 bit resolution and is stored
*   in the data section of this class as 16 bit value.
*   In addition for further processing the min and max values of the
*   raw tau bitmap are delivered by the "min" and "max" values.
*/
class TauRawBitmap
{

public:

    //! Width of raw tau core bitmap.
    /*!
    *    For example 160, 324, 336 or 640.
    */
    unsigned int width;

    //! Height of raw tau core bitmap.
    /*!
    *   For example 128, 256 or 512.
    */
    unsigned int height;

    //! Minimum value of raw tau core bitmap.
    /*!
    *   The range of raw pixel values goes from 0 to 16383.
    */
    unsigned int min;

    //! Maximum value of raw tau core bitmap.
    /*!
    *   The range of raw pixel values goes from 0 to 16383.
    */
    unsigned int max;

    //! PPS Timestamp
    /*!
     * The present pps timestamp value
     * (Milliseconds since last rising edge of ppm signal).
     */
    unsigned int pps_timestamp;

    //! Array of raw pixel values.
    /*!
    *   The raw pixel values (14 bit) are stored in a 16 bit array.
    */
    unsigned short* data;

    //! Constructor of TauRawBitmap.
    /*!
     * Initializes an object for raw tau bitmaps.
     * \param w Width of TauRawBitmap.
     * \param h height of TauRawBitmap.
     */
    TauRawBitmap(unsigned int w, unsigned int h);

    //! Destructor of TauRawBitmap.
    /*!
    *   Cleans up the TauRawBitmap object memory.
    */
    ~TauRawBitmap();
};

//! Container for rgb tau bitmap.
/*!
*   The "width" and "height" paramter inform about the size of the bitmap.
*   Every pixel value is stored in the data section of this class as 24 bit value.
*   The 24 bits per pixel contain 3 RGB channels.
*   Each channel value is 8 bit and all channels contain the same value.
*   The original 14 bit values of the TauRawBitmap pixels are scaled down to 8 bit resolution.
*/
class TauRGBBitmap
{

public:

    //! Width of raw tau core bitmap.
    /*!
    *    For example 160, 324, 336 or 640.
    */
    unsigned int width;

    //! Height of raw tau core bitmap.
    /*!
    *    For example 128, 256 or 512.
    */
    unsigned int height;

    //! Array of rgb pixel values.
    /*!
    *   The rgb pixel values (24 bit for all 3 channels) are stored in a byte array.
    */
    unsigned char * data;

    //! Constructor of TauRGBBitmap.
    /*!
     *  Initializes an object for rgb tau bitmaps.
     *  \param w Width of TauRGBBitmap.
     *  \param h height of TauRGBBitmap.
     */
    TauRGBBitmap(unsigned int width, unsigned int height);

    //! Destructor of TauRGBBitmap.
    /*!
    *   Cleans up the TauRGBBitmap object memory.
    */
    ~TauRGBBitmap();

    //! Scanline function of TauRGBBitmap.
    /*!
    *   For easy access of line addresses.
    */
    unsigned char * scanLine(unsigned int line);
};


enum TLinearResolution { High, Low };

namespace thermal_grabber {
enum GainMode {
    Automatic = 0,
    LowGain = 1,
    HighGain = 2,
    Manual = 3
};
}

//! Class for connecting "Thermal Capture Grabber USB".
/*!
*   Connecting Thermal Capture Grabber USB needs three steps:
*   1. Include the library header file "thermalgrabber.h" into your project.
*   2. Write a callback function for receiving TauRawBitmaps.
*   3. Use the constructor of ThermalGrabber. You will have to put in 2 parameters.
*   Firstly put in the pointer of the callback function.
*   Secondly add the pointer of the calling instance in the constructor.
*/
class ThermalGrabber
{

public:

    //! Type definition of callback.
    typedef void (*callbackThermalGrabber)(TauRawBitmap& tauRawBitmap, void* caller);

    //! Constructor of ThermalGrabber.
    /*!
    *   ThermalGrabber is used to connect the "Thermal Capture Grabber USB" device.
    *   The callback is called every time a full frame is received from the device.
    *   In order to use the callback ThermalGrabber needs to know the
    *   calling instance.
    *   ThermalCapture GrabberUSB uses the digital output of the tau core.
    *   Therefor it configures the tau core on start appropriately. The settings are
    *   volatile.
    *   \param cb Callback.
    *   \param caller Calling instance.
     */
    ThermalGrabber(callbackThermalGrabber cb, void* caller);


    //! Constructor of ThermalGrabber.
    /*!
    *   ThermalGrabber is used to connect the "Thermal Capture Grabber USB" device.
    *   The callback is called every time a full frame is received from the device.
    *   In order to use the callback ThermalGrabber needs to know the
    *   calling instance.
    *   ThermalCapture GrabberUSB uses the digital output of the tau core.
    *   Therefor it configures the tau core on start appropriately. The settings are
    *   volatile.
    *   The parameter iSerialUSB makes it possible to connect a
    *   ThermalCapture GrabberUSB by its unique iSerial. This iSerial can be
    *   identified by inspecting the usb system log of the operation system the
    *   ThermalCapture GrabberUSB is connected to.
    *   \param cb Callback.
    *   \param caller Calling instance.
    *   \param iSerialUSB Char string representation of iSerial.
     */
    ThermalGrabber(callbackThermalGrabber cb, void* caller, char* iSerialUSB);

    //! Destructor of ThermalGrabber.
    /*!
    *   Cleans up the ThermalGrabber object memory and waits for
    *   connection thread to close.
    */
    ~ThermalGrabber();

    //! Change the watchdog count reset value.
    /*!
    *   The watchdog checks every second for frame activity (frames from TCGrabberUSB).
    *   Standardly the counter is set to 10 seconds.
    *   If the watchdog doesn't notice any transfers in that time libthermalgrabber
    *   tries to reconnect TCGrabberUSB.
    *   Normally the counter shouldn't be modified but sometimes it's necessary
    *   (e.g. when using the external sync input - low-high-transition - on pin5 of TCGrabberUSB
    *   with single frame transfers - the watchdog might trigger between two sync input signals).
    *   Please keep in mind that there are situations where TCGrabberUSB can't send frames
    *   for a couple of seconds because Tau 2 Core doesn't transfers data (e.g. while ffc-/shutter-events).
    *   By using "0" for parameter wait_time the watchdog becomes inactive (will keep inactive until next connect).
    *   \param count The waiting time that is used by the watchdog in seconds or "0" to disable the watchdog.
    */
    void changeWatchdogCount(int wait_time);

    //! Convert the TauRawBitmap to TauRGBBitmap.
    /*!
    *   TauRawBitmap has 14bit values per pixel that are stored in a 16 bit array.
    *   The converted TauRGBBitmap has 24bit per pixel that are stored in a byte array.
    */
    void convertTauRawBitmapToTauRGBBitmap(TauRawBitmap &tauRawBitmap, TauRGBBitmap &tauRGBBitmap);

    void convertTauRawBitmapToTauRGBBitmapFusion(TauRawBitmap &tauRawBitmap, TauRGBBitmap &tauRGBBitmap);

    void convertTauRawBitmapToTauRGBBitmapRainbow(TauRawBitmap &tauRawBitmap, TauRGBBitmap &tauRGBBitmap);

    //! Send a command to TauCore.
    /*!
    *   Please have a look at the "FLIR TAU2/QUARK2 SOFTWARE IDD" document for further information.
    *   In general a command consists of function byte (cmd)
    *   and an optional byte array of arguments (data) and
    *   a length info of the data (the function byte/cmd is not counted).
    *   If no additional data are send put a "NULL" for the 2. and "0" for the 3. parameter.
    *   \param cmd The function that is called
    *   \param data Optional data bytes as arguments.
    *   \param data_len The length of the data field.
    */
    void sendCommand(char cmd, char *data, unsigned int data_len);

    //! Get the resolution width.
    /*!
     * Get the resolution width of the tau core that
     * is connected to the ThermalCapture GrabberUSB.
     * \return Width of Resolution or '0' if not found
     */
    unsigned int getResolutionWidth();

    //! Get the resolution height.
    /*!
     * Get the resolution height of the tau core that
     * is connected to the ThermalCapture GrabberUSB.
     * \return Height of Resolution or '0' if not found
     */
    unsigned int getResolutionHeight();

    //! Get Camera Serial Number
    /*!
     * Get Camera Serial Number of the tau core that
     * is connected to the ThermalCapture GrabberUSB.
     * The flir camera serial number is unique.
     * \return Camera Serial Number or '0' if not found
     */
    unsigned int getCameraSerialNumber();

    //! Get Camera Part Number
    /*!
     * Get Camera Part Number of the tau core that
     * is connected to the ThermalCapture GrabberUSB.
     * The ascii based char string contains the
     * flir camera part number that informs about the
     * general type of camera (resolution etc.).
     * \return char* Pointer to the char string or NULL if not available
     */
    const char* getCameraPartNumber() const;


    //! Shutter command
    /*!
    * Triggers a shutter event of the tau core that
    * is used for a Flat Field Correction
    * of the tau core sensor.
    */
    void doFFC();

    //! Set the Gain Mode
    /*!
     * Sets the Gain Mode to Automatic, High, Low or Manual.
     * Remember that Gain Mode is ignored when TLinear is
     * enabled (if TLinear is supported by the device).
     * The enum GainMode is defined in this header.
     * \param gainMode Enum of Type GainMode.
     */
    void setGainMode(thermal_grabber::GainMode gainMode);

    thermal_grabber::GainMode getGainMode();

    //! Enables TLinear in high resolution
    /*!
     * Enables TLinear mode and
     * sets the resolution of the TLinear digital video
     * to high resolution mode (0.04Kelvin/count in 14-bit digital).
     */
    void enableTLinearHighResolution();


    //! Enable TLinear in low resolution
    /*!
     * Enables TLinear mode and
     * sets the resolution of the TLinear digital video
     * to low resolution mode (0.4Kelvin/count in 14-bit digital).
     */
    void enableTlinearLowResolution();

    //! Disable TLinear Mode
    /*!
     * Disables the TLinear Mode of the TauCore to get raw values.
     */
    void disableTLinear();

    //! (Re-)Enable the standard internal sync of Tau 2 Core
    /*!
     * Requirements:
     * 1. This function is supported since firmware 1.3 of TCGrabberUSB (as of december 2017).  Older firmware versions will ignore the TCGrabberUSB related setting of this command. But Tau 2 Core setting of EXTERNAL_SYNC will be done.
     * 2. Requires Tau 2 Core with fast video core (25Hz/30Hz).
     *
     * The frame rate of the Tau 2 Core depends on the synchronization signal.
     * Normally this signal is generated by the Tau 2 Core itself but can also be applied from outside (e.g. from TCGrabberUSB or pin5 (external sync input)).
     * In this case Tau 2 Core generates synchronization signals on it's own and forwards it to pin6 (external sync output) of TCGrabberUSB.
     * The forwarded sync signal on pin6 (external sync output) can be used to synchronize a second TCGrabberUSB that is configured to use external sync signals.
     * Tau 2 Core's config setting of EXTERNAL_SYNC (cmd 0x21) gets set to master.
     */
    void enableInternalSyncByTau2CoreSyncOutOn();

    //! (Re-)Enable the standard internal sync of Tau 2 Core
    /*!
     * Requirements:
     * 1. This function is supported since firmware 1.3 of TCGrabberUSB (as of december 2017). Older firmware versions will ignore the TCGrabberUSB related setting of this command. But Tau 2 Core setting of EXTERNAL_SYNC will be done.
     * 2. Requires a Tau 2 Core with fast video core (25Hz/30Hz).
     *
     * The frame rate of the Tau 2 Core depends on the synchronization signal.
     * Normally this signal is generated by the Tau 2 Core itself but can also be applied from outside (e.g. from TCGrabberUSB or pin5 (external sync input)).
     * In this case Tau 2 Core generates synchronization signals on it's own but the forwarding to pin6 (external sync output) of TCGrabberUSB is not enabled.
     * Tau 2 Core's config setting of EXTERNAL_SYNC (cmd 0x21) gets set to disabled.
     */
    void enableInternalSyncByTau2CoreSyncOutOff();

    //! Enable internal sync by TCGrabberUSB
    /*!
     * Requirements:
     * 1. This function is supported since firmware 1.3 of TCGrabberUSB (as of december 2017). Older firmware versions will ignore the TCGrabberUSB related setting of this command. But Tau 2 Core setting of EXTERNAL_SYNC will be done. Accordingly Tau 2 Core will not work with an TCGrabberUSB with older firmware!
     * 2. Requires a Tau 2 Core with fast video core (25Hz/30Hz).
     *
     * The frame rate of the Tau 2 Core depends on the synchronization signal.
     * Normally this signal is generated by the Tau 2 Core itself but can also be applied from outside (e.g. from TCGrabberUSB or pin5 (external sync input)).
     * In this case TCGrabberUSB generates the sync signal for the Tau 2 Core and forwards it to pin6 (external sync output).
     * The resulting frequency of the sync signal generator has to be defined by the "frequency_parameter".
     * Please take care to only use frequencies in the allowed spectrum.
     * The allowed frequency spectrum depends on whether the PAL or NTSC setting of Tau 2 Core is active.
     * If PAL mode is active a frequency from 22.25Hz to 27.25Hz is supported by Tau 2 Core (default in this case 25Hz).
     * In case NTSC mode is active a frequency from 24.98Hz to 29.98Hz is supported by Tau 2 Core (default in this case 29.97).
     * For a detailed description please refer to the "FLIR Electrical IDD" (http://cvs.flir.com/tau2-electrical-idd).
     * The tables below show the possible frequencies that TCGrabberUSB will generate dependant on the given "frequency_parameter".
     * The value "frequency_parameter" stands for the function parameter and "frequency_result" for the sync signal frequency generated by TCGrabberUSB:
     *
     * Calculations of possible frequencies if PAL is active:
     *
     * frequency_parameter | frequency_result
     * ---- | ------------
     * 224  | 22.4719 Hz
     * 227  | 22.7273 Hz
     * 229  | 22.9885 Hz
     * 232  | 23.2558 Hz
     * 235  | 23.5294 Hz
     * 238  | 23.8095 Hz
     * 240  | 24.0964 Hz
     * 243  | 24.3902 Hz
     * 246  | 24.6914 Hz
     * 250  | 25 Hz
     * 253  | 25.3165 Hz
     * 256  | 25.641 Hz
     * 259  | 25.974 Hz
     * 263  | 26.3158 Hz
     * 266  | 26.6667 Hz
     * 270  | 27.027 Hz
     *
     * Calculations of possible frequencies if NTSC is active:
     *
     *
     * frequency_parameter | frequency_result
     * ---- | ----
     * 250  | 25 Hz
     * 253  | 25.3165 Hz
     * 256  | 25.641 Hz
     * 259  | 25.974 Hz
     * 263  | 26.3158 Hz
     * 266  | 26.6667 Hz
     * 270  | 27.027 Hz
     * 273  | 27.3973 Hz
     * 277  | 27.7778 Hz
     * 281  | 28.169 Hz
     * 285  | 28.5714 Hz
     * 289  | 28.9855 Hz
     * 294  | 29.4118 Hz
     * 298  | 29.8507 Hz
     *
     * The Tau 2 Core will work synchron to this signal (if requirements from above are fulfilled).
     * Direction: TCGrabberUSB -> sync signal -> Tau 2 Core.
     * The Tau 2 Core's config setting EXTERNAL_SYNC (cmd 0x21) gets set to slave.
     * \param frequency_paramter A frequency parameter from the tables above
     * \param count Number of sync pulses to generate (valid values from 1 to 32767) or '0' for continuous sync signal
     */
    void enableInternalSyncByTCGrabberUSB(uint32_t frequency_parameter, uint32_t count);

    //! Enable synchronization mode as slave
    /*!
     * Requirements:
     * 1. This function is supported since firmware 1.3 of TCGrabberUSB (as of december 2017). Older firmware versions will ignore the TCGrabberUSB related setting of this command. But Tau 2 Core setting of EXTERNAL_SYNC will be done. Accordingly Tau 2 Core will not work with an TCGrabberUSB with older firmware!
     * 2. Requires Tau 2 Core with fast video core (25Hz/30Hz)
     *
     * The frame rate of the Tau 2 Core depends on the synchronization signal.
     * Normally this signal is generated by the Tau 2 Core itself but can also be applied from outside (e.g. from TCGrabberUSB or pin5 (external sync input)).
     * In this case the sync signal has to be fed in to pin5 (external sync input) of TCGrabberUSB.
     * The sync signal is then forwarded to Tau 2 Core and to pin6 (external sync output) of TCGrabberUSB.
     * Please take care to only use frequencies in the allowed spectrum.
     * The allowed frequency spectrum depends on whether the PAL or NTSC setting of Tau 2 Core is active.
     * If PAL mode is active a frequency from 22.25Hz to 27.25Hz is supported by Tau 2 Core (default in this case 25Hz).
     * In case NTSC mode is active a frequency from 24.98Hz to 29.98Hz is supported by Tau 2 Core (default in this case 29.97).
     * For a detailed description please refer to the "FLIR Electrical IDD" (http://cvs.flir.com/tau2-electrical-idd).
     * The Tau 2 Core will then work synchron to this signal (if requirements from above are fulfilled).
     * Direction: External sync signal generator -> sync signal -> TCGrabberUSB -> Tau 2 Core.
     * The Tau 2 Core's config setting EXTERNAL_SYNC (cmd 0x21) gets set to slave.
     */
    void enableExternalSyncAsSlave();


private:

    TauInterface* mTauInterface;

    // internally used callback definitions
    static void static_callbackTauData(TauRawBitmap& tauRawBitmap , void* caller);
    void callbackTauData(TauRawBitmap& tRawBitmap);

    // internally used reference to callback and calling instance
    callbackThermalGrabber mCallbackThermalGrabber;
    void* mCallingInstance;

    // internally used helper function for scaling color values.
    unsigned int scale(unsigned int value, unsigned int lowBound, unsigned int upBound , unsigned int minOutput, unsigned int maxOutput);
};

#endif // THERMALGRABBER_H
