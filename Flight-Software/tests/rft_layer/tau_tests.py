''' @file tau_tests.py

 @brief Defines the Tau tests in the RFT

 @section description_tau_tests Description
 Defines the Tau tests in the RFT

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
from shared.tasks import Tasks
from shared.logging import create_logger

logsPath = "/home/debian/tests/testlog.log"
logger = create_logger("Test_RFT_Tau", logsPath)  # required for logging

def test_tau_power_cycle():
    global logger

    pinLowSuccess = False
    pinHighSuccess = False

    logger.info("Tau power-cycle test started")

    # set-up the pin for power-cycling
    GPIO.setup("P8_12", GPIO.OUT)

    # check if pin is low
    GPIO.output("P8_12", GPIO.LOW)
    pinState = GPIO.input("P8_12")

    if not pinState:
        pinLowSuccess = True

    time.sleep(1)

    # check if pin is high
    GPIO.output("P8_12", GPIO.HIGH)
    pinState = GPIO.input("P8_12")

    if pinState:
        pinHighSuccess = True

    logger.info("Tau power-cycle test finished")

    assert pinLowSuccess == True and pinHighSuccess == True

def test_tau_capture():
    global logsPath
    global logger

    logger.info("Tau image capture test started")

    starttimeoffset = 120 # start pass test in 1 second (config change every pass)
    transferTimeOffset = 0  # time allowance for late images
    passdurations = [60]  # the simulated pass will be X seconds long

    logsArg = "--logspath " + logsPath

    for passduration in passdurations:
        bbbtime = datetime.datetime.now().timestamp()  # check the current time

        passStartTime = bbbtime + starttimeoffset
        passFinishTime = bbbtime + starttimeoffset + passduration  # determine test imaging pass start and end times

        # calculate image times
        tasks = Tasks()
        times = "--times" + tasks.array_to_string(tasks.capture_timings(10, 550, passStartTime, passFinishTime, 0))

        logger.info("Setup test pass start: " + str(datetime.datetime.fromtimestamp(passStartTime)))
        logger.info("Setup test pass end: " + str(datetime.datetime.fromtimestamp(passFinishTime)))
        logger.info("Pass duration: " + str(passduration))

        # start tau imaging task with time arguments
        logger.info("python3 /home/debian/Tasks/tau2/tau.py " + times + " " + logsArg)
        process = subprocess.Popen(("python3 /home/debian/Tasks/tau2/tau.py " + times + " " + logsArg),
                                    shell=True,
                                    stdin=None,
                                    stdout=None,
                                    stderr=subprocess.STDOUT,
                                    preexec_fn=os.setsid)

        testWaitTime = passFinishTime - datetime.datetime.now().timestamp()
        time.sleep(testWaitTime)  # wait till the end of the test imaging pass
        logger.info("Sleep time: " + str(testWaitTime))

        # scan directory for the number of images taken
        # (to find how many were sucessfully captured)
        files = os.listdir()  # list the files in this directory

        taucount = 0

        # loop through files in current directory to detect how may images were captured
        for f in files:

            # identify file extensions
            length = f.rfind('.')
            extension = f[length:]

            # if tiff, JPEG, JPG then count them as a successfully captured image
            if extension == ".dat":
                taucount = taucount + 1


        logger.info("Number of tau images: " + str(taucount))
        logger.info("PASS TEST FINISHED")

        # wait for any late image captures
        WaitTime = transferTimeOffset
        time.sleep(WaitTime)  # wait till all late images have been captured
        logger.info("Sleep time: " + str(WaitTime))

        # clear up saved images
        logger.info("Removing .dat files...")
        subprocess.Popen("yes | rm -f *.dat", shell=True)

        logger.info("Tau image capture test finished")

        assert taucount >= 10  # minimum required