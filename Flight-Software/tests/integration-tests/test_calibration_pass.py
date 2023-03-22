''' @file test_calibration_passes.py

 @brief Defines a multiple calibration pass test using the tau.

 @section description_test_calibration_passes Description
 This test runs multiple calibration pass tests with the tau
 - test_calibration_pass_multi


 @section libraries_test_calibration_passes Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library


 @section todo_test_calibration_passes TODO
 - None.

 @section author_test_calibration_passes Author(s)
 - Created by Louis Timperley on 27/01/2022.
'''

import datetime
import subprocess
import sys
import time
import os

sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger


def test_calibration_pass_multi():
    logger = create_logger("Test_General", "/home/debian/tests/testlog.log")  # required for logging

    # sleep after test start to allow some time for cameras to boot up if needed
    sleepInitial = 10
    logger.info(f"Sleeping for {sleepInitial} secs...")
    time.sleep(sleepInitial)

    config = Config()  # read in configuration information

    starttimeoffset = 90  # start pass test in 1 second (config change every pass)
    transferTimeOffset = 80  # time allowance for image transfer to SD card
    passdurations = [60]  # the simulated pass will be X seconds long

    for passduration in passdurations:
        for i in range(1):
            logger.info("CAlIBRATION PASS TEST STARTED")

            # clean previous logs
            try:
                os.remove("/media/SD1/logs.log")
            except:
                logger.info("No logs to clean")  # the try except statement means the process does not stop
                # if no logs are found

            bbbtime = datetime.datetime.now().timestamp()  # check the current time

            passStartTime = bbbtime + starttimeoffset
            passFinishTime = bbbtime + starttimeoffset + passduration  # determine test imaging pass start and end times

            # write the new start, end times and pass type to config file
            config.set_operation_type("CALIBRATION")
            config.write_timestamps(passStartTime, passFinishTime)

            logger.info("Setup test calibration pass start: " + str(datetime.datetime.fromtimestamp(passStartTime)))
            logger.info("Setup test calibration pass end: " + str(datetime.datetime.fromtimestamp(passFinishTime)))
            logger.info("Pass duration: " + str(passduration))
            logger.info("repeat number " + str(1 + i))

            # restart scheduler service (if not already running), this will begin the test imaging pass
            process = subprocess.Popen("sudo systemctl restart scheduler.service",
                                       shell=True,
                                       stdin=None,
                                       stdout=None,
                                       stderr=subprocess.STDOUT)

            testWaitTime = passFinishTime - datetime.datetime.now().timestamp() + transferTimeOffset
            time.sleep(testWaitTime)  # wait till the end of the test imaging pass
            logger.info("Sleep time: " + str(testWaitTime))

            # scan image directory on SD card for the number of images taken
            # (to find how many were sucessfully captured)
            SDpath = "/media/SD1"  # mounting point for SD card
            newdirectory = config.recentpasstimestamp()

            newdirectorypath = os.path.join(SDpath, newdirectory)  # path to new directory on SD card
            logger.info("SD path: " + newdirectorypath)

            files = os.listdir(newdirectorypath)  # list the files in this directory

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

            # log times of image captures

            # now log the times these images were captured
            filename = "/media/SD1/logs.log"  # path to log file

            with open(filename) as file:
                logs = file.readlines()


            tautimes = []

            for log in logs:

                if "Tau-INFO-Image" in log:  # keyphrase used in logging image capture
                    tautimes.append(log.split("-tau")[0])

            logger.info("tau captures at :" + str(tautimes))

            # finally assert statements
            assert taucount >= config.configFull.cameras.tau.imgs_per_calibration # minimum required
