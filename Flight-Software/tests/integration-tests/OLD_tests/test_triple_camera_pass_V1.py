'''@file test_triple_camera_pass_V1.py

 @brief Defines a single pass test using all three cameras.

 @section description_test_triple_camera_pass_V1 Description
 This test runs an imaging pass with a defined duration and defined number of repeats, using all three cameras
 - main (test_triple_camera_pass_V1)


 @section libraries_test_triple_camera_pass_V1 Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library


 @section todo_test_triple_camera_pass_V1 TODO
 - None.

 @section author_test_triple_camera_pass_V1 Author(s)
 - Created by Louis Timperley on 02/08/2021.
'''

import datetime
import subprocess
import sys
import time
import os

sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger


def main():
    logger = create_logger("Test_General", "/home/debian/tests/testlog.log")

    # sleep after service start to allow some time for basler to boot up
    sleepInitial = 30
    logger.info(f"Sleeping for {sleepInitial} secs...")
    time.sleep(sleepInitial)

    config = Config()

    starttimeoffset = 1  # start pass test in X seconds (config change every pass)
    transferTimeOffset = 80  # time allowance for image transfer to SD card
    fullResArducamCaptureOffset = 240
    passduration = 170  # the simulated pass will be X seconds long


    # with one repeat
    for i in range(2):
        logger.info("PASS TEST STARTED")

        bbbtime = datetime.datetime.now().timestamp()

        passStartTime = bbbtime + starttimeoffset
        passFinishTime = bbbtime + starttimeoffset + passduration

        # write the new start and end times to config file
        config.write_timestamps(passStartTime, passFinishTime)

        logger.info("Setup test pass start: " + str(datetime.datetime.fromtimestamp(passStartTime)))
        logger.info("Setup test pass end: " + str(datetime.datetime.fromtimestamp(passFinishTime)))
        logger.info("Pass duration: " + str(passduration))
        logger.info("repeat number " + str(1 + i))

        # restart scheduler service (if not already running)
        process = subprocess.Popen("sudo systemctl restart scheduler.service",
                                   shell=True,
                                   stdin=None,
                                   stdout=None,
                                   stderr=subprocess.STDOUT)

        testWaitTime = passFinishTime - datetime.datetime.now().timestamp() + transferTimeOffset + fullResArducamCaptureOffset
        time.sleep(testWaitTime)
        logger.info("Sleep time: " + str(testWaitTime))

        # scan image directory on SD card for the number of images takem
        SDpath = "/media/SD1"  # mounting point for SD card
        newdirectory = config.recentpasstimestamp()

        newdirectorypath = os.path.join(SDpath, newdirectory)  # path to new directory on SD card
        logger.info("SD path: " + newdirectorypath)

        files = os.listdir(newdirectorypath)

        baslercount = 0
        arducamcount = 0
        thumbnailcount = 0

        # loop through files in current directory
        for f in files:

            # identify file extensions
            lenght = f.rfind('.')
            extension = f[lenght:]

            # if tiff, JPEG, JPG then move Image to directory on SD card
            if extension == ".tiff":
                baslercount = baslercount + 1

            if extension == ".thumbnail":
                thumbnailcount = thumbnailcount + 1

            if extension == ".jpg":
                arducamcount = arducamcount + 1

        logger.info("Number of Basler images: " + str(baslercount))
        logger.info("Number of ArduCam images: " + str(arducamcount))
        logger.info("Number of thumbnail images: " + str(thumbnailcount))
        logger.info("PASS TEST FINISHED")




if __name__ == "__main__":
    main()
