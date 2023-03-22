''' @file test_basler.py

 @brief Defines a tests for the tau2 camera.

 @section description_test_basler Description
 This test runs multiple  tests with the tau 2
 - test_tau_imaging_pass


 @section libraries_test_basler Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library


 @section todo_test_basler TODO
 - None.

 @section author_test_basler Author(s)
 - Created by Louis Timperley on 15/12/2021.
'''
import datetime
import subprocess
import sys
import time
import os
sys.path.append('/home/debian')
from shared.config import Config
from shared.tasks import Tasks
import pytest
import os
from pypylon import pylon
from shared.logging import create_logger
from Tasks.basler import basler

logger = create_logger("Test_Basler", "/home/debian/tests/testlog.log")


def test_basler_imaging_pass():
    logger = create_logger("Test_Basler", "/home/debian/tests/testlog.log")  # required for logging

    # sleep after test start to allow some time for cameras to boot up if needed
    sleepInitial = 5
    logger.info(f"Sleeping for {sleepInitial} secs...")
    time.sleep(sleepInitial)

    config = Config()  # read in configuration information

    starttimeoffset = 120 # start pass test in 1 second (config change every pass)
    transferTimeOffset = 60  # time allowance for late images
    passdurations = [150]  # the simulated pass will be X seconds long

    for passduration in passdurations:
        for i in range(1):
            logger.info("BASLER TEST STARTED")

            bbbtime = datetime.datetime.now().timestamp()  # check the current time

            passStartTime = bbbtime + starttimeoffset
            passFinishTime = bbbtime + starttimeoffset + passduration  # determine test imaging pass start and end times

            # calculate image times
            tasks = Tasks()
            times = "--times" + tasks.array_to_string(tasks.capture_timings(10, 550, passStartTime, passFinishTime, 0))

            logger.info("Setup test pass start: " + str(datetime.datetime.fromtimestamp(passStartTime)))
            logger.info("Setup test pass end: " + str(datetime.datetime.fromtimestamp(passFinishTime)))
            logger.info("Pass duration: " + str(passduration))
            #logger.info("repeat number " + str(1 + i))

            # start tau imaging task with time arguments
            logger.info("python3 /home/debian/Tasks/basler/basler.py " + times)
            process = subprocess.Popen(("python3 /home/debian/Tasks/basler/basler.py " + times),
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

            baslercount = 0

            # loop through files in current directory to detect how may images were captured
            for f in files:

                # identify file extensions
                length = f.rfind('.')
                extension = f[length:]

                # if tiff, JPEG, JPG then count them as a successfully captured image
                if extension == ".tiff":
                    baslercount = baslercount + 1


            logger.info("Number of basler images: " + str(baslercount))
            logger.info("PASS TEST FINISHED")

            # wait for any late image captures
            WaitTime = transferTimeOffset
            time.sleep(WaitTime)  # wait till all late images have been captured
            logger.info("Sleep time: " + str(WaitTime))

            # clear up saved images
            logger.info("Removing previous .tiff files...")
            subprocess.Popen("yes | rm -f *.tiff", shell=True)
            logger.info("Removing previous .jpeg files...")
            subprocess.Popen("yes | rm -f *.jpeg", shell=True)

            # finally assert statements
            assert baslercount >= 10 # minimum required



def test_connection():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    cameraname = camera.GetDeviceInfo().GetModelName()
    camera.Close()
    assert cameraname == "acA5472-5gc"

def test_parse_arguements():
    # TODO
    pass

def test_set_gain():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    # Set GainRaw to min value (192)
    value = camera.GainRaw.Min
    basler.set_gain(camera, logger, value)
    assert 192 == camera.GainRaw.Value

    # Set GainRaw to max value (1023)
    value = camera.GainRaw.Max
    basler.set_gain(camera, logger, value)
    assert 1023 == camera.GainRaw.Value

    # Set GainRaw to 500
    value = 500
    basler.set_gain(camera, logger, value)
    assert 500 == camera.GainRaw.Value

    value = 'a'
    with pytest.raises(TypeError):
        basler.set_gain(camera, logger, value)

    value = -100
    with pytest.raises(Exception):
        basler.set_gain(camera, logger, value)
    camera.Close()


def test_set_trigger_type():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    # pass
    print("ModelName: ", camera.GetDeviceInfo().GetModelName())
    camera.Open()

    basler.set_trigger_type(camera, logger, 'FrameStart')
    assert "FrameStart" == camera.TriggerSelector.Value
    basler.set_trigger_type(camera, logger, "FrameEnd")
    assert "FrameEnd" == camera.TriggerSelector.Value
    basler.set_trigger_type(camera, logger, "FrameActive")
    assert "FrameActive" == camera.TriggerSelector.Value
    basler.set_trigger_type(camera, logger, "FrameBurstStart")
    assert "FrameBurstStart" == camera.TriggerSelector.Value
    camera.Close()

def test_set_exposure_mode():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_exposure_mode(camera, logger, 'Timed')
    # assert "FrameTimedStart" == camera.ExposureMode.Value
    assert "Timed" == camera.ExposureMode.Value
    camera.Close()

def test_set_exposure_auto():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_exposure_auto(camera, logger, 'Once')
    assert "Once" == camera.ExposureAuto.Value
    basler.set_exposure_auto(camera, logger, 'Continuous')
    assert "Continuous" == camera.ExposureAuto.Value
    basler.set_exposure_auto(camera, logger, 'Off')
    assert "Off" == camera.ExposureAuto.Value
    camera.Close()

def test_set_exposure_time():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_exposure_time(camera, logger, 3500.0)
    assert 3500.0 == camera.ExposureTime.Value
    camera.Close()

def test_set_black_level():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_black_level(camera, logger, 32)
    assert 32 == camera.BlackLevelRaw.Value
    camera.Close()

def test_set_white_balance():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_white_balance(camera, logger, 1.08789)
    assert 1.08789 == camera.BalanceRatioAbs.Value
    camera.Close()

def test_set_pixel_format():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_pixel_format(camera, logger, 'BayerRG12')
    assert 'BayerRG12' == camera.PixelFormat.Value
    camera.Close()

def test_set_saturation():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    basler.set_saturation(camera, logger, 'BayerRG12')
    assert 'BayerRG12' == camera.PixelFormat.Value
    camera.Close()
