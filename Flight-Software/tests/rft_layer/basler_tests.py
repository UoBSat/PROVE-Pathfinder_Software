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

def test_basler_capture():
    # set up camera connection
    # now power basler
    print("Powering Basler")
    GPIO.setup("P8_8", GPIO.OUT)
    GPIO.output("P8_8", GPIO.HIGH)

    # add delay for powerup time
    time.sleep(60)

    try:
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        camera.Open()
        name = camera.GetDeviceInfo().GetModelName()
        print(f"Camera opened, using camera: {name}")
        time.sleep(2)

        # Need to cycle through a few different network configurations before reaching the correct one
        # Print the model name of the camera.
        print("Using device ", str(camera.GetDeviceInfo().GetModelName()))
        # Packet Size
        camera.GevSCPSPacketSize.SetValue(16404)
        # Frame transmission delay
        camera.GevSCFTD.SetValue(60000)
        # Inter - Packet Delay
        camera.GevSCPD.SetValue(12126)

        print("completed network set parameters phase 1")
        time.sleep(2)

        # Packet Size
        camera.GevSCPSPacketSize.SetValue(1000)
        # Frame transmission delay
        camera.GevSCFTD.SetValue(60000)
        # Inter - Packet Delay
        camera.GevSCPD.SetValue(10186)

        print("completed network set parameters phase 2")
        time.sleep(2)

    except Exception as e:
        print(f"Error when opening the camera: {e}")
        print("Quitting program...")
        # power down basler
        GPIO.output("P8_8", GPIO.LOW)
        # Cleanup GPIO pins
        GPIO.cleanup()
        camera.Close()
        sys.exit(1) # exit with errors

    # init converter
    converter = pylon.ImageFormatConverter()
    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_RGB8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


    for testNum in range(6):
        # demonstrate some feature access
        new_width = camera.Width.GetValue() - camera.Width.GetInc()
        if new_width >= camera.Width.GetMin():
            camera.Width.SetValue(new_width)

        print("New width assigned")

        numberOfImagesToGrab = 1
        camera.StartGrabbingMax(numberOfImagesToGrab)

        print("StartGrabbingMax done")

        num = 0

        myimagList = []

        while camera.IsGrabbing():

            grabResult = camera.RetrieveResult(50000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():

                print("Grab Succeeded")
                # Access the image data.

                print("SizeX: " + str(grabResult.Width))

                print("SizeY: " + str(grabResult.Height))
                image = converter.Convert(grabResult)
                img = image.GetArray()

                print("Colour of first pixel: " + str(img[0, 0]))
                myimagList.append(Image.fromarray(img))
                # myimagList.append( cv2.fromarray(img))

                # im.save(f"basler-{num}-{testNum}.png")
                # print("AFTER SAVING:-", datetime.datetime.now())
            else:
                print("Grab Failed")
            num = num + 1
            grabResult.Release()

        for i, im in enumerate(myimagList):
            # cv2.imwrite("basler-{testNum+1}.tiff", im)
            im.save(f"basler-{testNum + 1}.tiff")
            print(f"Image {testNum + 1} was saved")