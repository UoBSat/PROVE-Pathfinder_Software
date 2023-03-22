'''@file basler.py
 @brief Defines the basler imaging task.
 @section description_scheduler Description
 Defines the basler imaging task that captures all the images from the basler according to time stamps received form
 the scheduler service
 - add_arguments
 - defaultProperties
 - set_format
 - set_resolution
 - set_light_mode
 - set_saturation
 - set_brightness
 - set_contrast
 - set_special_effects
 - set_hue
 - set_exposure
 - set_sharpness
 - set_mirror_flip
 - set_compress_quality
 - set_test_pattern
 - main (basler)
 @section libraries_basler Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python pypylon library
 - python argpass library
 - python psutil library
 - python PIL library
 @section todo_basler TODO
 - None.
 @section author_basler Author(s)
 - Created by Vilius Stonkus on 02/08/2021.
 - Created by Nicole Li on 02/08/2021.
 - Modified by Louis Timperley on 03/08/2021.
'''

from pypylon import pylon
from PIL import Image
import datetime
import psutil
import time
import argparse
import subprocess
import os
import sys
import Adafruit_BBIO.GPIO as GPIO
import json
import logging
sys.path.append('/home/debian')

# only for Nicole's local dev
sys.path.append('/Users/nicolekwli/Documents/Bristol/PROVE/Flight-Software/Flight-Software')

from shared.logging import create_logger
from shared.config import Config

def add_arguments():
    """
    Adds command line arguments to a python argument parser
    Parameters:
        parser(object): command line argument parser object
    Returns:
        parser.parse_args() (object): arguments object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
                '--times',
                nargs='+',
                help='Capture times for VIS Images')

    #parser.add_argument(
    #            '--resolution',
    #            dest='resolution',
    #            nargs='+',
    #            help='Resolution for VIS Images')

    parser.add_argument(
                '--gain',
                nargs='+',
                dest='gain',
                help='Set Gain raw, increase the brightness of the images output, 192-1023?')

    parser.add_argument(
                '--triggertype',
                nargs='+',
                dest='trigger_type',
                help='Set trigger type(trigger selector) as one of the following values, FrameStart, FrameEnd, FrameActive, FrameBurstStart etc')

    parser.add_argument(
                '--exposuremode',
                nargs='+',
                dest='exposure_mode',
                help='Set a method for determining the length of exposure, e.g. Timed')

    parser.add_argument(
                '--exposureauto',
                nargs='+',
                dest='exposure_auto',
                help='Set automatic adjusting of the exposure time within specified limits until a target brightness has been reached, e.g. Off, Once, Continuous')
                
    parser.add_argument(
                '--exposuretime',
                nargs='+',
                dest='exposure_time',
                help='Set exposure time, integer value')

    parser.add_argument(
                '--black',
                nargs='+',
                dest='black_level',
                help='Set black level, integer value')

    parser.add_argument(
                '--white',
                nargs='+',
                dest='white_balance',
                help='Set white balance, decimal value')

    parser.add_argument(
                '--saturation',
                nargs='+',
                dest='saturation',
                help='Set saturation, decimal value')

    parser.add_argument(
                '--pixelformat',
                nargs='+',
                dest='pixel_format',
                help='Set pixel format, default is BayerRG12')
    
    return parser.parse_args()

# Camera configuration functions ----------------------------
def set_gain(camera, config: Config, logger: logging.Logger, gain):
    """
    Configure camera gain value with given value.
    """

    default = config.configFull.cameras.basler.properties.gain.default

    # return if the value is default
    if gain == default:
        logger.info(f"Gain: {gain} (default)")
        return

    try:
        # if gain:
        camera.GainRaw.SetValue(gain)
        # else:
        #     camera.GainRaw = camera.GainRaw.Min

        config.configFull.cameras.basler.properties.gain.value = gain
        config.write_config(config.configFull)

        logger.info(f"Gain was changed to: {gain} (non-default)")
    except Exception as e:
        logger.error(f"Error when setting the gain: {type(e).__name__}: {e}")
        raise type(e).__name__
        
        
def set_trigger_type(camera, config: Config, logger: logging.Logger, triggerType):
    """
    Configure camera gain value with given value.
    """

    default = config.configFull.cameras.basler.properties.trigger_type.default

    # return if the value is default
    if triggerType == default:
        logger.info(f"Trigger Type: {triggerType} (default)")
        return
    
    try:
        camera.TriggerSelector.SetValue(triggerType)

        config.configFull.cameras.basler.properties.trigger_type.value = triggerType
        config.write_config(config.configFull)

        logger.info(f"Trigger Type was changed to: {triggerType} (non-default)")
    except Exception as e:
        logger.error(f"Error when setting the trigger type: {e}")
        raise
        
def set_exposure_mode(camera, config: Config, logger: logging.Logger, mode):
    """
    Configure camera exposure mode with given value.
    """

    default = config.configFull.cameras.basler.properties.exposure_mode.default

    # return if the value is default
    if mode == default:
        logger.info(f"Exposure Mode: {mode} (default)")
        return

    try:
        camera.TriggerSelector.SetValue('FrameStart')
        logger.info("Trigger selecter(type) set to FrameStart as required.")
        camera.TriggerMode.SetValue('On')
        logger.info("Trigger mode turned on as required.")
        # TODO set trigger source
        camera.ExposureMode.SetValue(mode)

        config.configFull.cameras.basler.properties.exposure_mode.value = mode
        config.write_config(config.configFull)

        logger.info(f"Exposure Mode was changed to: {mode} (non-default)")
        # Set the TriggerSource parameter to one of the available hardware trigger sources, e.g., Line1.
        # camera.TriggerSource.SetValue(Line1)
        # camera.ExposureMode.SetValue('Timed')
    except Exception as e:
        logger.error(f"Error when setting the exposure mode: {e}")  
        raise
    
def set_exposure_auto(camera, config: Config, logger: logging.Logger, auto):
    """
    Configure camera exposure auto mode with given value.
    """

    default = config.configFull.cameras.basler.properties.exposure_auto.default

    # return if the value is default
    if auto == default:
        logger.info(f"Exposure Auto: {auto} (default)")
        return

    try:
        camera.ExposureAuto.SetValue(auto)

        config.configFull.cameras.basler.properties.exposure_auto.value = auto
        config.write_config(config.configFull)

        logger.info(f"Exposure Auto was changed to: {auto} (non-default)")  
    except Exception as e:
        logger.error(f"Error when setting the exposure auto: {e}")
        raise

def set_exposure_time(camera, config: Config, logger: logging.Logger, time):
    """
    Configure camera exposure time with given value.
    """

    default = config.configFull.cameras.basler.properties.exposure_time.default

    # return if the value is default
    if time == default:
        logger.info(f"Exposure Time: {time} (default)")
        return

    try:
        camera.ExposureMode.SetValue("Timed")
        camera.ExposureAuto.SetValue("Off")
        camera.ExposureTimeAbs.SetValue(time)

        config.configFull.cameras.basler.properties.exposure_time.value = time
        config.write_config(config.configFull)

        logger.info(f"Exposure Time was changed to: {time} (non-default)") 
        # E.g. camera.ExposureTimeAbs.SetValue(10036)
    except Exception as e:
        logger.error(f"Error when setting the exposure time: {e}")
        raise

def set_black_level(camera, config: Config, logger: logging.Logger, black):
    """
    Configure camera black level with given value.
    """

    default = config.configFull.cameras.basler.properties.black_level.default

    # return if the value is default
    if black == default:
        logger.info(f"Black Level: {black} (default)")
        return

    try:
        camera.BlackLevelRaw.SetValue(black) # E.g. camera.BlackLevelRaw.SetValue(0)
        
        config.configFull.cameras.basler.properties.black_level.value = black
        config.write_config(config.configFull)

        logger.info(f"Black Level was changed to: {black} (non-default)") 
    except Exception as e:
        logger.error(f"Error when setting the exposure time: {e}")
        raise

def set_white_balance(camera, config: Config, logger: logging.Logger, white):
    """
    Configure camera white balance with given value.
    """
    
    default = config.configFull.cameras.basler.properties.white_balance.default

    # return if the value is default
    if white == default:
        logger.info(f"White Balance: {white} (default)")
        return

    try:
        camera.BalanceRatioAbs.SetValue(white)

        config.configFull.cameras.basler.properties.white_balance.value = white
        config.write_config(config.configFull)

        logger.info(f"White Balance was changed to: {white} (non-default)") 
    except Exception as e:
        logger.error(f"Error when setting the white balance: {e}")
        raise

def set_pixel_format(camera, config: Config, logger: logging.Logger, pixelFormat):
    """
    Configure camera pixel format with given value.
    """

    default = config.configFull.cameras.basler.properties.pixel_format.default

    # return if the value is default
    if pixelFormat == default:
        logger.info(f"Pixel Format: {pixelFormat} (default)")
        return

    try:
        camera.PixelFormat.SetValue(pixelFormat)

        config.configFull.cameras.basler.properties.pixel_format.value = pixelFormat
        config.write_config(config.configFull)

        logger.info(f"Pixel Format was changed to: {pixelFormat} (non-default)") 
    except Exception as e:
        logger.error(f"Error when setting the pixel format: {e}")
        raise


def set_saturation(camera, config: Config, logger: logging.Logger, saturation):
    """
    Configure camera saturation level with given value.
    """

    default = config.configFull.cameras.basler.properties.saturation.default

    # return if the value is default
    if saturation == default:
        logger.info(f"Saturation: {saturation} (default)")
        return

    try:
        camera.BslSaturation.SetValue(saturation)

        config.configFull.cameras.basler.properties.saturation.value = saturation
        config.write_config(config.configFull)

        logger.info(f"Saturation was changed to: {saturation} (non-default)") 
    except Exception as e:
        logger.error(f"Error when setting the saturation: {e}")
        raise


# Camera functions ------------------------------------------
def basler_connect(logger):
    # now power basler
    logger.info("Powering Basler")
    GPIO.setup("P8_8", GPIO.OUT)
    GPIO.output("P8_8", GPIO.HIGH)

    # add delay for powerup time
    time.sleep(60)

    try:
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        camera.Open()
        name = camera.GetDeviceInfo().GetModelName()
        logger.info(f"Camera opened, using camera: {name}")
        time.sleep(2)

        # Need to cycle through a few different network configurations before reaching the correct one
        # Print the model name of the camera.
        logger.info("Using device ", str(camera.GetDeviceInfo().GetModelName()))
        # Packet Size
        camera.GevSCPSPacketSize.SetValue(16404)
        # Frame transmission delay
        camera.GevSCFTD.SetValue(60000)
        # Inter - Packet Delay
        camera.GevSCPD.SetValue(12126)

        logger.info("completed network set parameters phase 1")
        time.sleep(2)

        # Packet Size
        camera.GevSCPSPacketSize.SetValue(1000)
        # Frame transmission delay
        camera.GevSCFTD.SetValue(60000)
        # Inter - Packet Delay
        camera.GevSCPD.SetValue(10186)

        logger.info("completed network set parameters phase 2")
        time.sleep(2)
        return camera
    except Exception as e:
        logger.error(f"Error when opening the camera: {e}")
        logger.info("Quitting program...")
        # power down basler
        GPIO.output("P8_8", GPIO.LOW)
        # Cleanup GPIO pins
        GPIO.cleanup()
        camera.Close()
        sys.exit(1) # exit with errors
    

def main():
    """
    Main code for the basler camera.
    Steps:
        Parse arguments
        Instantiate logger
        Take pictures
        Save pictures and thumbnails
    """

    error_count = 0
    captures_complete = False
    while (error_count < 5 and captures_complete is False):
        try:
            # parse arguments
            args = add_arguments()

            # init process
            # only remove previous files on first attempt
            if error_count == 0:
                logger.info("Removing previous .tiff files...")
                subprocess.Popen("yes | rm -f *.tiff", shell=True)
                logger.info("Removing previous .jpeg files...")
                subprocess.Popen("yes | rm -f *.jpeg", shell=True)

            logger.info("Basler args = " + str(args.times))

            logger.info("---START BASLER---")

            # Set camera configuration
            logger.info("Applying camera configurations.")
            if args.gain:
                set_gain(camera, logger, args.gain)

            if args.trigger_type:
                set_trigger_type(camera, logger, args.trigger_type)

            if args.exposure_mode:
                set_exposure_mode(camera, logger, args.exposure_mode)

            if args.exposure_auto:
                set_exposure_auto(camera, logger, args.exposure_auto)

            if args.exposure_time:
                set_exposure_time(camera, logger, args.exposure_time)
                
            if args.black_level:
                set_black_level(camera, logger, args.black_level)

            if args.white_balance:
                set_white_balance(camera, logger, args.white_balance)

            if args.pixel_format:
                set_pixel_format(camera, logger, args.pixel_format)

            if args.saturation:
                set_saturation(camera, logger, args.saturation)

            logger.info("Camera configurations done.")

            # init converter
            converter = pylon.ImageFormatConverter()
            # converting to opencv bgr format
            converter.OutputPixelFormat = pylon.PixelType_RGB8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            # definition of thumbnail variables
            thumbnailImage = int(len(args.times)/2)
            thumbnailSaved = False

            for testNum in range(len(args.times)):            
                # demonstrate some feature access
                new_width = camera.Width.GetValue() - camera.Width.GetInc()
                if new_width >= camera.Width.GetMin():
                    camera.Width.SetValue(new_width)

                logger.info("New width assigned")
                

                numberOfImagesToGrab = 1
                camera.StartGrabbingMax(numberOfImagesToGrab)

                logger.info("StartGrabbingMax done")

                num = 0

                myimagList = []

                while camera.IsGrabbing():
                    if time.time() < float(args.times[testNum]):
                        
                        logger.info("Waiting (s):")
                        waitTime = float(args.times[testNum]) - time.time()
                        
                        logger.info(waitTime)
                        time.sleep(waitTime)
                    
                    grabResult = camera.RetrieveResult(50000, pylon.TimeoutHandling_ThrowException)

                    if grabResult.GrabSucceeded():
                        
                        logger.info("Grab Succeeded")
                        # Access the image data.
                        
                        logger.info("SizeX: " + str(grabResult.Width))
                        
                        logger.info("SizeY: " + str(grabResult.Height))
                        image = converter.Convert(grabResult)
                        img = image.GetArray()
                        
                        logger.info("Colour of first pixel: " + str(img[0, 0]))
                        myimagList.append( Image.fromarray(img))
                        # myimagList.append( cv2.fromarray(img))

                        #im.save(f"basler-{num}-{testNum}.png")
                        #print("AFTER SAVING:-", datetime.datetime.now())
                    else:
                        logger.error("Grab Failed")
                    num=num+1
                    grabResult.Release()


                for i, im in enumerate(myimagList):
                    # cv2.imwrite("basler-{testNum+1}.tiff", im) 
                    im.save(f"basler-{testNum+1}.tiff")
                    logger.info(f"Image {testNum+1} was saved")

                    # saves a thumbnail
                    if testNum+1 == thumbnailImage:
                        im.save(f"thumb-{thumbnailImage}.jpeg")
                        logger.info(f"Thumbnail of img {thumbnailImage} was saved")
                        thumbnailSaved = True
                    
                    # saves a thumbnail if it failed to be saved before
                    if testNum+1 > thumbnailImage:
                        if thumbnailSaved is False:
                            logger.warning(f"Thumbnail FAILED to be saved for image {thumbnailImage}")
                            im.save(f"thumb-{testNum+1}.jpeg")
                            logger.info(f"Thumbnail of img {testNum+1} was saved")
                            thumbnailSaved = True

            camera.Close()
            logger.info("Camera closed")
            # power down basler
            GPIO.output("P8_8", GPIO.LOW)
            # Cleanup GPIO pins
            GPIO.cleanup()

            captures_complete = True

        except Exception as e:
            error_count += 1
            logger.error(f"{e}")
            # try to set up camera connection again
            camera = basler_connect(logger)

    logger.info("Too many errors occured. Quitting program...")
    camera.Close() # need to close camera interface before quitting
    # power down basler
    GPIO.output("P8_8", GPIO.LOW)
    # Cleanup GPIO pins
    GPIO.cleanup()
    sys.exit(1) # exit with errors


if __name__ == "__main__":

    # Create logger
    logger = create_logger("Basler", "/media/SD1/logs.log")
    # set up camera connection
    camera = basler_connect(logger)
    # initiate config
    config = Config()
    
    # Main 
    main()

