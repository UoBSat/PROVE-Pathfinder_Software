''' @file tau_tests.py

 @brief Defines the Tau tests in the FFT

 @section description_tau_tests Description
 Defines the Tau tests in the FFT

 @section libraries_tau_tests Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library
 - python Adafruit_BBIO.GPIO library


 @section todo_tau_tests TODO
 - None.

 @section author_fft_tests Author(s)
 - Created by Vilius Stonkus on 02/02/2023.
'''

import datetime
import subprocess
import sys
import time
import os
import Adafruit_BBIO.GPIO as GPIO

sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger


# logs the Tau status, whether it was powered on or not
tauOn = False

logsPath = "/home/debian/tests/testlog.log"
logger = create_logger("Test_FFT_Tau", logsPath)  # required for logging

def test_tau_ping():
    global logsPath
    global logger

    pingSuccess = False

    logger.info("Tau ping test started")

    # power-cycle Tau
    tau_power_cycle()

    libPath = "/home/debian/Tasks/tau2/lib/libthermalgrabber/lib/libthermalgrabber.so"
    programPath = "/home/debian/tests/tau_files/test_tau"
    progArgs = "ping"

    process = subprocess.Popen(("sudo LD_PRELOAD=" + libPath + " " + programPath + " " + progArgs + " >> " + logsPath),
            shell= True,
            stdin= None,
            stdout= None,
            stderr= subprocess.STDOUT,
            preexec_fn=os.setsid)

    # wait 7 seconds to allow camera to initiate and perform the test
    logger.info("Sleeping for 7s to allow Tau perform the test...")
    time.sleep(7)

    # check if camera response is in the logs
    logger.info("Reading Tau response...")
    logsFile = open(logsPath, "r")
    data = logsFile.read()
    logsFile.close()

    # replacing end splitting the text
    # when newline ('\n') is seen.
    dataLines = data.split("\n")

    # search for the response in the last 20 lines
    for lineIndex in range(len(dataLines)-20, len(dataLines)):
        if "Response: No op" in dataLines[lineIndex]:
            pingSuccess = True

    logger.info("Tau ping test finished")

    assert pingSuccess == True

def test_tau_config():
    global logsPath
    global logger

    gainModeSuccess = False
    agcTypeSuccess = False
    contrastSuccess = False
    brightnessSuccess = False

    logger.info("Tau configuration test started")

    # power-cycle Tau
    tau_power_cycle()

    libPath = "/home/debian/Tasks/tau2/lib/libthermalgrabber/lib/libthermalgrabber.so"
    programPath = "/home/debian/tests/tau_files/test_tau"
    progArgs = "config"

    process = subprocess.Popen(("sudo LD_PRELOAD=" + libPath + " " + programPath + " " + progArgs + " >> " + logsPath),
            shell= True,
            stdin= None,
            stdout= None,
            stderr= subprocess.STDOUT,
            preexec_fn=os.setsid)

    # wait 7 seconds to allow camera to initiate and perform the test
    logger.info("Sleeping for 7s to allow Tau perform the test...")
    time.sleep(7)

    # check if camera response is in the logs
    logger.info("Reading Tau response...")
    logsFile = open(logsPath, "r")
    data = logsFile.read()
    logsFile.close()

    # replacing end splitting the text
    # when newline ('\n') is seen.
    dataLines = data.split("\n")

    # search for responses in the last 50 lines
    for lineIndex in range(len(dataLines)-50, len(dataLines)):
        if "Response: Gain Mode: High gain" in dataLines[lineIndex]:
            gainModeSuccess = True
        if "Response: AGC Type: Linear AGC" in dataLines[lineIndex]:
            agcTypeSuccess = True
        if "Response: Contrast: 123" in dataLines[lineIndex]:
            contrastSuccess = True
        if "Response: Brightness: 250" in dataLines[lineIndex]:
            brightnessSuccess = True

    logger.info("Tau configuration test finished")

    assert gainModeSuccess == True and agcTypeSuccess == True and contrastSuccess == True and brightnessSuccess == True

def tau_power_cycle():
    global tauOn
    global logger

    if tauOn == False:
        # Set-up GPIO pins. Pin is held HIGH to prevent capture
        logger.info("Setting Tau trigger pin HIGH...")
        GPIO.setup("P9_41", GPIO.OUT)
        GPIO.output("P9_41", GPIO.HIGH)

        # power cycle tau
        logger.info("Power-cycling Tau...")
        GPIO.setup("P8_12", GPIO.OUT)

        GPIO.output("P8_12", GPIO.LOW)
        time.sleep(1)
        GPIO.output("P8_12", GPIO.HIGH)

        # add delay for powerup
        logger.info("Sleeping for 30s to allow Tau to fully initialise...")
        time.sleep(30)

        tauOn = True