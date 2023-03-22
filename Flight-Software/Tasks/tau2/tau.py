'''@file tau.py
 @brief Defines the tau imaging task.
 @section tau_version File Version:
 - v0.1.0-alpha
 @section description_scheduler Description
 @section libraries_tau Libraries/Modules
 @section todo_tau TODO
 - Handle input from schduler
 - Initilise all data
 - Run tau image collection
 - Error Handling
 - Image processing
 - Hard and soft crashes
 @section author_tau Author(s)
 - Created by Michael Jon O'Donnell mo14776@bristol.ac.uk
 - Modified by Vilius Stonkus X/10/2022
 @section history Histoy:
 - 2021/11/08 - v0.1.0-alpha
'''

import Adafruit_BBIO.GPIO as GPIO
import datetime
import argparse
import subprocess
import os
import sys
import traceback
import time
import typing
import signal
import logging
# Set system path
sys.path.append('/home/debian')

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
        help='Capture times for tau Images')

    parser.add_argument(
        '--logspath',
        nargs='+',
        dest='logs_path',
        help='Path to the log file')
    
    parser.add_argument(
        '--gainmode',
        nargs='+',
        dest='gain_mode',
        help='Set Gain Mode: Automatic, Low Gain Only, High Gain Only, Manual')

    parser.add_argument(
        '--agctype',
        nargs='+',
        dest='agc_type',
        help='Set AGC algorhithm type: PlateauHistogram, OnceBright, AutoBright, Manual, LinearAGC')

    parser.add_argument(
        '--contrast',
        nargs='+',
        dest='contrast',
        help='Set the contrast value used by once-bright, auto-bright, and manual AGC algorithms: 0-255')

    parser.add_argument(
        '--brightness',
        nargs='+',
        dest='brightness',
        help='Sets the AGC brightness value used by the manual and auto-bright AGC algorithms: 0-16383')

    return parser.parse_args()

# Camera configuration functions ----------------------------
def set_gain_mode(logger: logging.Logger, gainMode: str) -> str:
    """
    Configure camera gain mode value with given value.
    """

    default: str = config.configFull.cameras.tau.properties.gain_mode.default

    # return an empty string if the value is default (no argument for a c++ program)
    if gainMode == default:
        logger.info(f"Gain Mode: {gainMode} (default)")
        return ""

    # create an argument for a c++ tau program
    progArg: str = " " + "gain_mode:" + gainMode

    config.configFull.cameras.tau.properties.gain_mode.value = gainMode
    config.write_config(config.configFull)

    logger.info(f"Gain Mode will be changed to: {gainMode} (non-default)")

    return progArg

def set_agc_type(logger: logging.Logger, agcType: str):
    """
    Configure camera AGC (Auto Gain Control) algorithm type value with given value.
    """

    default: str = config.configFull.cameras.tau.properties.agc_type.default

    # return an empty string if the value is default (no argument for a c++ program)
    if agcType == default:
        logger.info(f"AGC Type: {agcType} (default)")
        return ""

    # create an argument for a c++ tau program
    progArg: str = " " + "agc_type:" + agcType

    config.configFull.cameras.tau.properties.agc_type.value = agcType
    config.write_config(config.configFull)

    logger.info(f"AGC Type will be changed to: {agcType} (non-default)")

    return progArg

def set_contrast(logger: logging.Logger, contrast: str):
    """
    Configure camera contrast value with given value.
    """

    default: int = config.configFull.cameras.tau.properties.contrast.default

    # return an empty string if the value is default (no argument for a c++ program)
    if int(contrast) == default:
        logger.info(f"Contrast: {contrast} (default)")
        return ""

    # create an argument for a c++ tau program
    progArg: str = " " + "contrast:" + contrast

    config.configFull.cameras.tau.properties.contrast.value = int(contrast)
    config.write_config(config.configFull)

    logger.info(f"Contrast will be changed to: {contrast} (non-default)")

    return progArg

def set_brightness(logger: logging.Logger, brightness: str):
    """
    Configure camera brightness value with given value.
    """

    default: int = config.configFull.cameras.tau.properties.brightness.default

    # return an empty string if the value is default (no argument for a c++ program)
    if int(brightness) == default:
        logger.info(f"Brightness: {brightness} (default)")
        return ""

    # create an argument for a c++ tau program
    progArg: str = " " + "brightness:" + brightness

    config.configFull.cameras.tau.properties.brightness.value = int(brightness)
    config.write_config(config.configFull)

    logger.info(f"Brightness will be changed to: {brightness} (non-default)")

    return progArg


def tau_image_capture(logger, GPIOPin: str, captureTimes, fileLocation: str, passNumber: int) :
    """
    Function to control the accurate capture of images using the Tau2.
    Function takes the capture times and performs the oscillatory response
    required to activate the camera.

    Parameters
    ----------
    GPIOPin : str
        Contains the string corresponding to the GPIO pin used to control
        pin oscillation.
    captureTimes : list[int]
        A list of integers corresponding to the capture times required for
        image capture.
    fileLocation : str
        Contains the path to file storage location for tau images
    passNumber : int
        The number of this image pass, for labelling purposes
    Returns
    -------
    Success : boolean
        If True, capture was successful and data can be worked upon.
        If False, data capture has failed in 2 potential places. Logfile needs
        to be checked

    """


    logger.info("Running image capture")
    #Maintain high output to prevent image capture
    GPIO.output(GPIOPin, GPIO.HIGH)

    mSeconds = 2000
    pinLowTime = mSeconds/1000 # convert milli to seconds

    maxCaptureRetries = 20

    imagePythonTimes = []

    # Get the number of images to capture. This will start at N images, and be
    # decrimented by 1 for every captured image
    ImagesToCapture =len(captureTimes)
    logger.debug(f"Capture times length of: {ImagesToCapture}")

    # Assume list is sorted from closest time (smallest) to furthest
    # time (smallest). i.e chronological order
    # Assume list has at least 1 image.
    # Assume list is in nanoseconds

    currentImage = captureTimes.pop(0)
    retry = 0
    imageNo = 0

    while ImagesToCapture>0 and retry < maxCaptureRetries:

        currentTime = time.time_ns()

        if currentTime>=currentImage:

            preLowPinTime = time.time_ns()
            GPIO.output(GPIOPin, GPIO.LOW)
            postLowPinTime = time.time_ns()
            logger.info(f"P9_41 low")

            # Hold low to allow image capture
            time.sleep(pinLowTime)

            preHighPinTime = time.time_ns()
            GPIO.output(GPIOPin, GPIO.HIGH)
            postHighPinTime = time.time_ns()
            logger.info(f"P9_41 high")


            # Set expected image file name
            imageFileName = f"{fileLocation}pass-{passNumber}-file-{imageNo}.dat"
            # Check image was taken

            if os.path.exists(imageFileName):
                logger.info(f"Image {imageFileName} compeletion: {ImagesToCapture}")

                # Store all pin timings
                imagePythonTimes.append([preLowPinTime,postLowPinTime,preHighPinTime,postHighPinTime])
                # Reduce number of images left to capture
                ImagesToCapture-=1
                imageNo +=1
                #Get next image
                try:
                    currentImage = captureTimes.pop(0)
                except IndexError:
                    logger.info("IndexError - assume no images left to capture")
                    pass
                except:
                    logger.exception("Non-index error exception in image capture")

                    # Soft exit function to handle error
                    return False

                # reset retries
                retry = 0

            else:
                # image capture was unsuccessful
                # Increment retry variable and reattempt
                retry +=1
                logger.critical(f"Retrying {currentImage} : {retry}")

        else:
            pass

    # Write timings to file

    timingsFileName = f"{fileLocation}pass-{passNumber}-timings.dat"
    with open(timingsFileName,"w") as f:
        logger.debug(f"Writing image timings to file: {timingsFileName}")
        for index,line in enumerate(imagePythonTimes):
            f.write(f"{index} {imagePythonTimes}")

    # Check if capture ended due to a retry halt
    if retry >= maxCaptureRetries:
        logger.critical(f"Retrying {currentImage} : Max retries reached. Image capture halted")
        return False

    # Assume all images captured succesfully
    logger.info("Image capture complete")

    return True



def tau_camera_start(logger, timeNow, endTime, tauConfigArgs, logsPath):
    """
    Start a Tau c++ program in the background which waits for a capture trigger

    Parameters
    ----------
    timeNow : int
        Current timestamp.
    endTime : int
        Expected capture end timestamp.
    tauConfigArgs : str
        A string of camera configuration arguments to be passed to a c++ program
    Returns
    -------
    process : subprocess
        A subprocess variable representing the the background c++ program

    """

    # Set-up GPIO pins. Pin is held HIGH to prevent capture
    logger.info("Set GPIO pins")
    GPIO.setup("P9_41", GPIO.OUT)
    GPIO.output("P9_41", GPIO.HIGH)

    # now power tau
    logger.info("Powering Tau")
    GPIO.setup("P8_12", GPIO.OUT)

    # power-down first
    GPIO.output("P8_12", GPIO.LOW)
    time.sleep(1)
    GPIO.output("P8_12", GPIO.HIGH)

    # add delay for powerup
    time.sleep(30)

    # Run the C++ capture program
    # firstly process arguments to hand to the cpp programme
    # duration the program should run - first two arguments
    cppduration = int(1000000*(endTime - timeNow + 3)) # 3 extra seconds to account for final time offset TODO consider removing
    progArgs = str(cppduration) + tauConfigArgs
    logger.info(f"Cpp program arguments: {progArgs}")

    # Using Popen as allows for non-blocking program run
    try:
        process = subprocess.Popen(("sudo LD_PRELOAD=/home/debian/Tasks/tau2/lib/libthermalgrabber/lib/libthermalgrabber.so /home/debian/Tasks/tau2/main " + progArgs + " >> " + logsPath),
                                    shell= True,
                                    stdin= None,
                                    stdout= None,
                                    stderr= subprocess.STDOUT,
                                    preexec_fn=os.setsid)
    except:
        logger.exception("C++ capture program run failure")

        # Force exit the program as the C++ program has not started
        raise SystemExit

    # Wait 5 seconds to allow camera to initiate and configure itself
    time.sleep(5)

    return process

def main():
    """
    Main code for the tau2 camera.
    Steps:
        Parse arguments
        Instantiate logger
        Take pictures
        Save pictures
    """

    # Read and parse arguments
    args = add_arguments()

    # default logs path
    logsPath = "/media/SD1/logs.log"

    if args.logs_path:
        logsPath = args.logs_path[0]
    
    if "test" in logsPath:
        logger = create_logger("Test_Tau", logsPath)
    else:
        logger = create_logger("Tau", logsPath)

    logger.info("Tau capture times = " + str(args.times))

    #first covert capture time arguments to nano second ints
    captureTimes = []
    for element in args.times:
        captureTimes.append(float(element) * 10 ** 9)

    timenow = float(datetime.datetime.now().timestamp()) * 10 ** 9

    # remove previous images
    logger.info("Removing previous .dat files...")
    subprocess.Popen("yes | rm -f *.dat", shell=True)

    logger.info("---START TAU---")

    # Set camera configuration
    logger.info("Applying camera configurations.")

    # create a string of config args for a tau c++ program
    tauConfigArgs = ""

    if args.gain_mode:
        gainMode = args.gain_mode[0]
        tauConfigArgs += set_gain_mode(logger, gainMode)
    if args.agc_type:
        agcType = args.agc_type[0]
        tauConfigArgs += set_agc_type(logger, agcType)
    if args.contrast:
        contrast = args.contrast[0]
        tauConfigArgs += set_contrast(logger, contrast)
    if args.brightness:
        brightness = args.brightness[0]
        tauConfigArgs += set_brightness(logger, brightness)

    logger.info("Tau config args:" + tauConfigArgs)

    # Start the camera
    process = tau_camera_start(logger, timenow, captureTimes[-1], tauConfigArgs, logsPath)

    # Perform capture
    fileLocation=""
    passNumber = 1

    if tau_image_capture(logger, "P9_41",captureTimes,fileLocation, passNumber):
        logger.info("Image pass success")
    else:
        logger.info("Image pass failure")


    # Clean up C++ program


    GPIO.output("P9_41", GPIO.HIGH)
    # Ensure program is terminated

    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    # Cleanup GPIO pins
    GPIO.cleanup()

    #os.killpg(os.getpgid(process.pid), signal.SIGTERM)# this may happen early

    # power down tau
    GPIO.output("P8_12", GPIO.LOW)
    # Cleanup GPIO pins
    GPIO.cleanup()
    timeVal = time.time()

if __name__ == "__main__":
    # set up camera connection
    # TODO: camera setup similar to basler e.g. camera = basler_connect(logger)

    # initiate config
    config = Config()
    
    # Main 
    main()