''' @file test_tau2.py

 @brief Defines a tests for the tau2 camera.

 @section description_test_tau2 Description
 This test runs multiple  tests with the tau 2
 - test_tau_imaging_pass


 @section libraries_test_tau2 Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library


 @section todo_test_tau2 TODO
 - None.

 @section author_test_tau2 Author(s)
 - Created by Louis Timperley on 14/12/2021.
'''

import datetime
import subprocess
import sys
import time
import os
sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger
from shared.tasks import Tasks

def test_tau_imaging_pass():
    logger = create_logger("Test_Tau", "/home/debian/tests/testlog.log")  # required for logging

    # sleep after test start to allow some time for cameras to boot up if needed
    sleepInitial = 5
    logger.info(f"Sleeping for {sleepInitial} secs...")
    time.sleep(sleepInitial)

    config = Config()  # read in configuration information

    starttimeoffset = 120 # start pass test in 1 second (config change every pass)
    transferTimeOffset = 0  # time allowance for late images
    passdurations = [130]  # the simulated pass will be X seconds long

    for passduration in passdurations:
        for i in range(1):
            logger.info("TAU TEST STARTED")

            bbbtime = datetime.datetime.now().timestamp()  # check the current time

            passStartTime = bbbtime + starttimeoffset
            passFinishTime = bbbtime + starttimeoffset + passduration  # determine test imaging pass start and end times

            # calculate image times
            tasks = Tasks()
            times = "--times" + tasks.array_to_string(tasks.capture_timings(50, 550, passStartTime, passFinishTime, 0))

            logger.info("Setup test pass start: " + str(datetime.datetime.fromtimestamp(passStartTime)))
            logger.info("Setup test pass end: " + str(datetime.datetime.fromtimestamp(passFinishTime)))
            logger.info("Pass duration: " + str(passduration))
            #logger.info("repeat number " + str(1 + i))

            # start tau imaging task with time arguments
            logger.info("python3 /home/debian/Tasks/tau2/tau.py " + times + " --gainmode High --agctype LinearAGC --contrast 60 --brightness 100")
            process = subprocess.Popen(("python3 /home/debian/Tasks/tau2/tau.py " + times + " --gainmode High --agctype LinearAGC --contrast 60 --brightness 100"),
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
            # logger.info("Removing previous .dat files...")
            # subprocess.Popen("yes | rm -f *.dat", shell=True)

            # finally assert statements
            assert taucount >= 50  # minimum required

