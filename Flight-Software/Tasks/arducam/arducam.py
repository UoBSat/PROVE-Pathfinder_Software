#!/usr/bin/env python3
'''@file arducam.py

 @brief Defines the arducam imaging task.

 @section description_scheduler Description
 Defines the arducam imaging task that captures all the images from the arducam according to time stamps received form
 the scheduler service
 - add_arguments
 - defaultProperties
 - set_format
 - set_resolution
 - set_light_mode
 - set_saturation
 - set_brightness
 - set_contrast
 - set_special_effects
 - set_hue
 - set_exposure
 - set_sharpness
 - set_mirror_flip
 - set_compress_quality
 - set_test_pattern
 - main (arducam)


 @section libraries_arducam Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library
 - python argpass library
 - python json library
 - python types library


 @section todo_arducam TODO
 - None.

 @section author_arducam Author(s)
 - Created by Vilius Stonkus on 02/08/2021.
 - Modified by Louis Timperley on 03/08/2021.
'''

from inspect import _void
from re import S
import sys
sys.path.append('/home/debian')
import argparse
from shared.logging import create_logger
from shared.config import Config
import pyBBBCAM
import time
import datetime
import subprocess
import json
import logging
from types import SimpleNamespace

def add_arguments(config: Config):
    """
        Adds command line arguments to a python arguments parser

        Parameters:
            config (Config): config

        Returns:
            parser.parse_args() (object): arguments object with string values
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-res',
        '--resolution', 
        dest='resolution', 
        default=config.arducam.properties.resolution.default, 
        help='change resolution'
    )
    parser.add_argument(
        '-f',
        '--format', 
        dest='format', 
        default=config.arducam.properties.format.default, 
        help='change format'
    )
    parser.add_argument(
        '-lm',
        '--lightmode', 
        dest='lightmode', 
        default=config.arducam.properties.lightmode.default,
        help='change light mode'
    )
    parser.add_argument(
        '-sat',
        '--saturation', 
        dest='saturation', 
        default=config.arducam.properties.saturation.default,
        help='change saturation'
    )
    parser.add_argument(
        '-br',
        '--brightness', 
        dest='brightness', 
        default=config.arducam.properties.brightness.default,
        help='change brightness'
    )
    parser.add_argument(
        '-c',
        '--contrast', 
        dest='contrast', 
        default=config.arducam.properties.contrast.default, 
        help='change contrast'
    )
    parser.add_argument(
        '-spec',
        '--specialeffects', 
        dest='special_effects', 
        default=config.arducam.properties.special_effects.default,
        help='change special effects'
    )
    parser.add_argument(
        '-hu',
        '--hue', 
        dest='hue', 
        default=config.arducam.properties.hue.default, 
        help='change hue'
    )
    parser.add_argument(
        '-exp',
        '--exposure', 
        dest='exposure', 
        default=config.arducam.properties.exposure.default,
        help='change exposure'
    )
    parser.add_argument(
        '-sh',
        '--sharpness', 
        dest='sharpness', 
        default=config.arducam.properties.sharpness.default,
        help='change sharpness'
    )
    parser.add_argument(
        '-mf',
        '--mirrorflip', 
        dest='mirror_flip', 
        default=config.arducam.properties.mirror_flip.default,
        help='change mirror flip'
    )
    parser.add_argument(
        '-cq',
        '--compressquality', 
        dest='compress_quality', 
        default=config.arducam.properties.compress_quality.default,
        help='change compress quality'
    )
    parser.add_argument(
        '-tp',
        '--testpattern', 
        dest='test_pattern', 
        default=config.arducam.properties.test_pattern.default,
        help='change test pattern'
    )
    parser.add_argument(
        '--times',
        nargs='+',
        help='Capture times for ArduCam Images'
    )

    return parser.parse_args()

def set_format(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the image format

        Parameters:
            arg (int): number which represents a certain format setting
                0 - BMP format
                1 - JPEG format
                2 - RAW format
            logger (logging.Logger): returns a custom logger object
            config (Config): config

        Returns:
            void
    """

    args_allowed = [0, 1, 2]
    arg_default = config.arducam.properties.format.default
    
    # return if the value is default
    if arg == arg_default:
        logger.info(f"Format: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_format(arg)
            if result:
                config.arducam.properties.format.value = arg
                config.write_config(config)

                logger.info(f"Format was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the format. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the format: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for format")

def set_resolution(arg1: int, arg2: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the image resolution

        Parameters:
            arg1 (int): number which represents a certain JPEG or RAW resolution setting
                if arg2 is 1 or 0 (JPEG, BMP):
                0 - 320x240 resolution
                1 - 640x480 resolution
                2 - 1024x768 resolution
                3 - 1280x960 resolution
                4 - 1600x1200 resolution
                5 - 2048x1536 resolution
                6 - 2592x1944 resolution
                if arg2 is 2 (RAW):
            arg2 (int): number which represents a certain format setting
                0 - BMP format
                1 - JPEG format
                2 - RAW format
            logger (object): returns a custom logger object

        Returns:
            void
    """

    jpeg_res_allowed = [0, 1, 2, 3, 4, 5, 6]
    raw_res_allowed = [1, 3, 6, 7]
    
    arg_default = config.arducam.properties.resolution.default

    # jpeg, bmp
    if arg2 == 1 or arg2 == 0:
        # return if the value is default
        if arg1 == arg_default:
            logger.info(f"JPEG Resolution: {arg1} (default)")
            return

        if arg1 in jpeg_res_allowed:
            try:
                result = pyBBBCAM.py_set_JPEG_size(arg1)
                if result:
                    config.arducam.properties.resolution.value = arg1
                    config.write_config(config)

                    logger.info(f"JPEG Resolution was changed to: {arg1} (non-default)")
                else:
                    logger.info(f"Error when setting the JPEG resolution. Library result: {result}")
            except Exception as e:
                logger.error(f"Error when setting the JPEG resolution: {e}")
        else:
            logger.warn(f"Argument {arg1} is not allowed for JPEG resolution")
    # raw
    elif arg2 == 2:
        # return if the value is default
        if arg1 == arg_default:
            logger.info(f"RAW Resolution: {arg1} (default)")
            return

        if arg1 in raw_res_allowed:
            try:
                result = pyBBBCAM.py_set_RAW_size(arg1)
                if result:
                    config.arducam.properties.resolution.value = arg1
                    config.write_config(config)

                    logger.info(f"RAW Resolution was changed to: {arg1} (non-default)")
                else:
                    logger.error(f"Error when setting the RAW resolution. Library result: {result}")
            except Exception as e:
                logger.error(f"Error when setting the RAW resolution: {e}")
        else:
            logger.warn(f"Argument {arg1} is not allowed for RAW resolution")
    else:
        logger.warn(f"Argument {arg2} is not allowed for format")

def set_light_mode(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the light mode

        Parameters:
            arg (int): number which represents a certain light mode setting
                0 - Advanced_AWB mode
                1 - Simple_AWB mode
                2 - Manual_day mode
                3 - Manual_A mode
                4 - Manual_cwf mode
                5 - Manual_cloudy mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3, 4, 5]
    arg_default = config.arducam.properties.lightmode.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Light Mode: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Light_Mode(arg)
            if result:
                config.arducam.properties.lightmode.value = arg
                config.write_config(config)

                logger.info(f"Light Mode was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Light Mode. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the light mode: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for light mode")

def set_saturation(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the saturation

        Parameters:
            arg (int): number which represents a certain saturation setting
                0 - Saturation4 mode
                1 - Saturation3 mode
                2 - Saturation2 mode
                3 - Saturation1 mode
                4 - Saturation0 mode
                5 - Saturation_1 mode
                6 - Saturation_2 mode
                7 - Saturation_3 mode 
                8 - Saturation_4 mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    arg_default = config.arducam.properties.saturation.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Saturation: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Color_Saturation(arg)
            if result:
                config.arducam.properties.saturation.value = arg
                config.write_config(config)

                logger.info(f"Saturation was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Saturation. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Saturation: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Saturation")

def set_brightness(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the brightness

        Parameters:
            arg (int): number which represents a certain brightness setting
                0 - Brightness4 mode
                1 - Brightness3 mode
                2 - Brightness2 mode
                3 - Brightness1 mode
                4 - Brightness0 mode
                5 - Brightness_1 mode
                6 - Brightness_2 mode
                7 - Brightness_3 mode 
                8 - Brightness_4 mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    arg_default = config.arducam.properties.brightness.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Brightness: {arg} (default)")
        return

    if arg in args_allowed:     
        try:
            result = pyBBBCAM.py_set_Brightness(arg)
            if result:
                config.arducam.properties.brightness.value = arg
                config.write_config(config)

                logger.info(f"Brightness was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Brightness. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Brightness: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Brightness")

def set_contrast(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the contrast

        Parameters:
            arg (int): number which represents a certain contrast setting
                0 - Contrast4 mode
                1 - Contrast3 mode
                2 - Contrast2 mode
                3 - Contrast1 mode
                4 - Contrast0 mode
                5 - Contrast_1 mode
                6 - Contrast_2 mode
                7 - Contrast_3 mode
                8 - Contrast_4 mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    arg_default = config.arducam.properties.contrast.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Contrast: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Contrast(arg)
            if result:
                config.arducam.properties.contrast.value = arg
                config.write_config(config)

                logger.info(f"Contrast was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Contrast. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Contrast: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Contrast")

def set_special_effects(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the special effects

        Parameters:
            arg (int): number which represents a certain special effects setting
                1 - Bluish mode 
                2 - Greenish mode
                3 - Reddish mode
                4 - BW mode
                5 - Negative mode
                6 - Sepia mode
                7 - Normal mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [1, 2, 3, 4, 5, 6, 7]
    arg_default = config.arducam.properties.special_effects.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Special Effects: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Special_effects(arg)
            if result:
                config.arducam.properties.special_effects.value = arg
                config.write_config(config)

                logger.info(f"Special Effects was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Special effects. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Special effects: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Special effects")

def set_hue(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the hue

        Parameters:
            arg (int): number which represents a certain hue setting
                0 - degree_180 mode
                1 - degree_150 mode
                2 - degree_120 mode
                3 - degree_90 mode
                4 - degree_60 mode
                5 - degree_30 mode
                6 - degree_0 mode
                7 - degree30 mode
                8 - degree60 mode
                9 - degree90 mode
                10 - degree120 mode
                11 - degree150 mode
            logger (object): returns a custom logger object

        Returns:
            void
    """
    
    args_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    arg_default = config.arducam.properties.hue.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Hue: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_hue(arg)
            if result:
                config.arducam.properties.hue.value = arg
                config.write_config(config)

                logger.info(f"Hue was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Hue. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Hue: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Hue")

def set_exposure(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the exposure

        Parameters:
            arg (int): number which represents a certain exposure setting
                0 - Exposure_17_EV mode
                1 - Exposure_13_EV mode
                2 - Exposure_10_EV mode
                3 - Exposure_07_EV mode
                4 - Exposure_03_EV mode
                5 - Exposure_default mode
                6 - Exposure03_EV mode
                7 - Exposure07_EV mode
                8 - Exposure10_EV mode
                9 - Exposure13_EV mode
                10 - Exposure17_EV mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    arg_default = config.arducam.properties.exposure.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Exposure: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Exposure(arg)
            if result:
                config.arducam.properties.exposure.value = arg
                config.write_config(config)

                logger.info(f"Exposure was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Exposure. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Exposure: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Exposure")

def set_sharpness(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the sharpness

        Parameters:
            arg (int): number which represents a certain sharpness setting
                0 - Auto_Sharpness_default mode
                1 - Auto_Sharpness1 mode
                2 - Auto_Sharpness2 mode
                3 - Manual_Sharpnessoff mode
                4 - Manual_Sharpness1 mode
                5 - Manual_Sharpness2 mode
                6 - Manual_Sharpness3 mode
                7 - Manual_Sharpness4 mode
                8 - Manual_Sharpness5 mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    arg_default = config.arducam.properties.sharpness.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Sharpness: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Sharpness(arg)
            if result:
                config.arducam.properties.sharpness.value = arg
                config.write_config(config)

                logger.info(f"Sharpness was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Sharpness. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Sharpness: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Sharpness")

def set_mirror_flip(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the mirror flip setting

        Parameters:
            arg (int): number which represents a certain mirror flip setting
                0 - MIRROR
                1 - FLIP mode
                2 - MIRROR_FLIP mode
                7 - Normal mode
            logger (object): returns a custom logger object

        Returns:
            void
    """
    
    args_allowed = [0, 1, 2, 7]
    arg_default = config.arducam.properties.mirror_flip.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Mirror Flip: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Mirror_flip(arg)
            if result:
                config.arducam.properties.mirror_flip.value = arg
                config.write_config(config)

                logger.info(f"Mirror Flip was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Mirror flip. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Mirror flip: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Mirror flip")

def set_compress_quality(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the compress quality setting

        Parameters:
            arg (int): number which represents a certain compress quality setting
                0 - high quality mode
                1 - default quality mode
                2 - low quality mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2]
    arg_default = config.arducam.properties.compress_quality.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Compressibility Quality: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Compress_quality(arg)
            if result:
                config.arducam.properties.compress_quality.value = arg
                config.write_config(config)

                logger.info(f"Compressibility Quality was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Compress quality. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Compress quality: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Compress quality")

def set_test_pattern(arg: int, config: Config, logger: logging.Logger):
    """
        Sends a request to the ArduCAM library to change the test pattern setting

        Parameters:
            arg (int): number which represents a certain test pattern setting
                0 - Color bar mode
                1 - Color square mode
                2 - BW square mode
                3 - DLI mode
            logger (object): returns a custom logger object

        Returns:
            void
    """

    args_allowed = [0, 1, 2, 3]
    arg_default = config.arducam.properties.test_pattern.default

    # return if the value is default
    if arg == arg_default:
        logger.info(f"Test Pattern: {arg} (default)")
        return

    if arg in args_allowed:
        try:
            result = pyBBBCAM.py_set_Test_Pattern(arg)
            if result:
                config.arducam.properties.test_pattern.value = arg
                config.write_config(config)

                logger.info(f"Test Pattern was changed to: {arg} (non-default)")
            else:
                logger.error(f"Error when setting the Test Pattern. Library result: {result}")
        except Exception as e:
            logger.error(f"Error when setting the Test Pattern: {e}")
    else:
        logger.warn(f"Argument {arg} is not allowed for Test Pattern")


def main():
    """
        Initialises the ArduCAM capturing process based on the parameters passed; Logs the output

        Parameters:
            void

        Returns:
            void
    """

    try:
        # create logger
        logFile = "/media/SD1/logs.log"
        config = Config()
        logger: logging.Logger = create_logger("ArduCam", logFile)

        # parse arguments
        args = add_arguments()
        numbOfImages = len(args.times)
        
        # Images to capture per single call
        imgsToCapture = 1
        # Type = 0 for pass images, 1 for high-res post-pass
        img_type = 0

        logger.info("Removing previous .jpg files...")
        subprocess.Popen("yes | rm -f *.jpg", shell=True)

        
        logger.info("ArduCam args = " + str(args.times))

        camSetup = pyBBBCAM.py_setup()

        # Change camera settings after setup (if specified)
        # Check if argument exists
        if "format" in vars(args):
            set_format(int(args.format), config, logger)
        if "resolution" in vars(args):
            if "format" in vars(args):
                set_resolution(int(args.resolution), int(args.format), config, logger)
            else:
                set_resolution(int(args.resolution), 1, config, logger)
        if "lightmode" in vars(args):
            set_light_mode(int(args.lightmode), config, logger)
        if "saturation" in vars(args):
            set_saturation(int(args.saturation), config, logger)
        if "brightness" in vars(args):
            set_brightness(int(args.brightness), config, logger)
        if "contrast" in vars(args):
            set_contrast(int(args.contrast), config, logger)
        if "special_effects" in vars(args):
            set_special_effects(int(args.special_effects), config, logger)
        if "hue" in vars(args):
            set_hue(int(args.hue), config, logger)
        if "exposure" in vars(args):
            set_exposure(int(args.exposure), config, logger)
        if "sharpness" in vars(args):
            set_sharpness(int(args.sharpness), config, logger)
        if "mirror_flip" in vars(args):
            set_mirror_flip(int(args.mirror_flip), config, logger)
        if "compress_quality" in vars(args):
            set_compress_quality(int(args.compress_quality), config, logger)
        if "test_pattern" in vars(args):
            set_test_pattern(int(args.test_pattern), config, logger)
    
    
        # Check the camera status after its initialisation
        if not camSetup.status:
            if len(camSetup.error) > 0:
                logger.error(camSetup.error)

        # Iteration through the capture times
        for i in range(numbOfImages):
            currentImage = i+1
            currentRealTimestamp = time.time()
            currentImgTimestamp = float(args.times[i])

            # Wait until the capture time is reached and its time to take an image
            if currentRealTimestamp < currentImgTimestamp:           
                logger.info("Waiting (s):")
                waitTime = currentImgTimestamp - currentRealTimestamp            
                logger.info(waitTime)
                time.sleep(waitTime)

            # Change the img type to have different image names for post-pass imaging
            if "resolution" in vars(args):
                if int(args.resolution) == int(6):
                    img_type = 1    

            # Start capture & save
            camCapture = pyBBBCAM.py_capture(imgsToCapture, currentImage, img_type)
            
            # Check the camera status after the capture
            if not camCapture.status:
                if len(camCapture.error) > 0:
                    logger.error(camCapture.error)

    except Exception as e:
        logger.error(f"{e}")

if __name__ == "__main__":
    main()

