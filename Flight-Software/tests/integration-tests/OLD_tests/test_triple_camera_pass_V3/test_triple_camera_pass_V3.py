''' @file test_triple_camera_pass_V3.py

 @brief Defines a multiple pass test using all three cameras and power cycling.

 @section description_test_triple_camera_pass_V1 Description
 This test runs imaging pass tests with the three cameras and sweeps through a set of different pass durations, and can
 be use alongside power cycles between pass tests
 i.e. multiple V1 tests with different durations and power cycling
 - main (test_triple_camera_pass_V3)


 @section libraries_test_triple_camera_pass_V3 Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library


 @section todo_test_triple_camera_pass_V3 TODO
 - need to improve stability in sweeping through different pass durations and coordinating with timed power cycles

 @section author_test_triple_camera_pass_V3 Author(s)
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

    with open('test_durations.txt') as f:
        for line in f:
            pass
        passduration = float(line)

    logger.info("PASS TEST STARTED")

    bbbtime = datetime.datetime.now().timestamp()

    passStartTime = bbbtime + starttimeoffset
    passFinishTime = bbbtime + starttimeoffset + passduration

    # write the new start and end times to config file
    config.write_timestamps(passStartTime, passFinishTime)

    logger.info("Setup test pass start: " + str(datetime.datetime.fromtimestamp(passStartTime)))
    logger.info("Setup test pass end: " + str(datetime.datetime.fromtimestamp(passFinishTime)))
    logger.info("Pass duration: " + str(passduration))

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

    #finally remove last line from durations file
    file = open("test_durations.txt", "r")
    d = file.read() #read in all lines of the files
    file.close()
    os.remove("test_durations.txt")
    m = d.split("\n")
    s = "\n".join(m[:-1])
    logger.info(f"{s}")
    file = open("test_durations.txt", "w+")
    for i in range(len(s)): #rewrite all but last line
        file.write(s[i])
    file.close()

if __name__ == "__main__":
    main()
