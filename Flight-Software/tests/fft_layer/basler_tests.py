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
from pypylon import pylon

sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger


# logs the Tau status, whether it was powered on or not
baslerOn = False

logsPath = "/home/debian/tests/testlog.log"
logger = create_logger("Test_FFT_Basler", logsPath)  # required for logging

def test_connection():
    # power-cycle Basler
    basler_power_cycle()

    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    cameraname = camera.GetDeviceInfo().GetModelName()
    camera.Close()
    assert cameraname == "acA5472-5gc"

def test_basler_config():
    # power-cycle Basler
    basler_power_cycle()

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

    # pass
    print("ModelName: ", camera.GetDeviceInfo().GetModelName())

    basler.set_trigger_type(camera, logger, 'FrameStart')
    assert "FrameStart" == camera.TriggerSelector.Value
    basler.set_trigger_type(camera, logger, "FrameEnd")
    assert "FrameEnd" == camera.TriggerSelector.Value
    basler.set_trigger_type(camera, logger, "FrameActive")
    assert "FrameActive" == camera.TriggerSelector.Value
    basler.set_trigger_type(camera, logger, "FrameBurstStart")
    assert "FrameBurstStart" == camera.TriggerSelector.Value

    basler.set_exposure_mode(camera, logger, 'Timed')
    # assert "FrameTimedStart" == camera.ExposureMode.Value
    assert "Timed" == camera.ExposureMode.Value

    basler.set_exposure_auto(camera, logger, 'Once')
    assert "Once" == camera.ExposureAuto.Value
    basler.set_exposure_auto(camera, logger, 'Continuous')
    assert "Continuous" == camera.ExposureAuto.Value
    basler.set_exposure_auto(camera, logger, 'Off')
    assert "Off" == camera.ExposureAuto.Value

    basler.set_exposure_time(camera, logger, 3500.0)
    assert 3500.0 == camera.ExposureTime.Value

    basler.set_black_level(camera, logger, 32)
    assert 32 == camera.BlackLevelRaw.Value

    basler.set_white_balance(camera, logger, 1.08789)
    assert 1.08789 == camera.BalanceRatioAbs.Value

    basler.set_pixel_format(camera, logger, 'BayerRG12')
    assert 'BayerRG12' == camera.PixelFormat.Value

    basler.set_saturation(camera, logger, 'BayerRG12')
    assert 'BayerRG12' == camera.PixelFormat.Value
    camera.Close()

def basler_power_cycle():
    global baslerOn
    global logger

    if baslerOn == False:
        # power cycle basler
        logger.info("Power-cycling Tau...")
        GPIO.setup("P8_8", GPIO.OUT)

        GPIO.output("P8_8", GPIO.LOW)
        time.sleep(1)
        GPIO.output("P8_8", GPIO.HIGH)

        # add delay for powerup
        logger.info("Sleeping for 30s to allow basler to fully initialise...")
        time.sleep(30)

        baslerOn = True