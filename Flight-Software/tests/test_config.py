''' @file test_config.py

@brief Defines test for the config class methods.

@section description_test_config Description
Defines the unit tests for the config class methods
- test_get_config
- test_get_pass_duration
- test_write_timestamps
- test_recentpasstimestamp


@section libraries_config Libraries/Modules
- python pytest library
- python sys library
- python json library
- python datetime library



@section todo_config TODO
- None.

@section author_config Author(s)
- Created by Louis Timperley on 12/08/2021.
'''
import pytest
import json
import datetime
import os
import sys
sys.path.append('/home/debian')
from shared.config import Config

def test_get_config():
    """
           Tests the initialisation of the config object, i.e. the get_config function, by checking the contents of the
           retrieved json object

           Parameters:
               none

           Returns:
               void
    """
    #first need to write the test config file
    # generate test config json
    config = {
        "general":
        {
            "next_pass_type": "PRIMARY",
            "safe_mode": False,
            "pass_start_timestamp": 1727292818,
            "pass_end_timestamp": 1727292968,
            "pre_pass_init": 60,
            "post_pass_timeout": 60,
            "altitude": 500,
            "pass_completion_time": 15
        },
        "cameras":
        {
            "basler":
            {
                "imgs_per_pass": 10,
                "finaltimeoffset": 6,
                "properties":
                {
                    "gain":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "trigger_type":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_mode":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_auto":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_time":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "black_level":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "white_balance":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "pixel_format":
                    {
                        "value": "BayerRG12",
                        "default": "BayerRG12"
                    },
                    "saturation":
                    {
                        "value": -1,
                        "default": -1
                    }
                }
            },
            "tau":
            {
                "imgs_per_pass": 50,
                "imgs_per_calibration": 5,
                "finaltimeoffset": 6,
                "properties": {
                    "gain_mode": {
                        "value": "High",
                        "default": "Automatic"
                    },
                    "agc_type": {
                        "value": "PlateauHistogram",
                        "default": "PlateauHistogram"
                    },
                    "contrast": {
                        "value": 50,
                        "default": 32
                    },
                    "brightness": {
                        "value": 120,
                        "default": 0
                    }
                }
            }
        },
        "sensors": {
            "collection_cadence": 10,
            "T_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "CPU_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "T_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            }
        }
    }


    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/config.json', r'/home/debian/Scheduler/configtemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/config.json', 'w') as jsonFile:
        json.dump(config, jsonFile)


    config = Config() #get_config is run on initialisation of the Config class

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    # assert that all relived variable types are correct (however really this tests the content of config.json)
    assert config.configFull.general.next_pass_type == "PRIMARY"
    assert config.configFull.general.pass_start_timestamp == 1727292818
    assert config.configFull.general.pass_end_timestamp == 1727292968
    assert config.configFull.general.pre_pass_init == 0
    assert config.configFull.general.post_pass_timeout == 60
    assert config.configFull.general.altitude == 500
    assert config.configFull.general.pass_completion_time == 15
    assert config.configFull.cameras.tau.finaltimeoffset == 6
    assert config.configFull.cameras.basler.finaltimeoffset == 6
    assert config.configFull.cameras.basler.imgs_per_pass == 10
    assert config.configFull.cameras.tau.imgs_per_pass == 50
    assert config.configFull.sensors.collection_cadence == 10
    assert config.configFull.sensors.T_TEMP.warn_threshold == 10
    assert config.configFull.sensors.T_TEMP.error_threshold == 20
    assert config.configFull.sensors.B_TEMP.warn_threshold == 10
    assert config.configFull.sensors.B_TEMP.error_threshold == 20
    assert config.configFull.sensors.A_TEMP.warn_threshold == 10
    assert config.configFull.sensors.A_TEMP.error_threshold == 20
    assert config.configFull.sensors.CPU_TEMP.warn_threshold == 10
    assert config.configFull.sensors.CPU_TEMP.error_threshold == 20
    assert config.configFull.sensors.T_CUR.warn_threshold == 10
    assert config.configFull.sensors.T_CUR.error_threshold == 20
    assert config.configFull.sensors.B_CUR.warn_threshold == 10
    assert config.configFull.sensors.B_CUR.error_threshold == 20
    assert config.configFull.sensors.A_CUR.warn_threshold == 10
    assert config.configFull.sensors.A_CUR.error_threshold == 20

def test_get_pass_duration():
    """
           Tests the get_pass_duration function, by comparing the pass duration saved to the config.json
           file to the result of the get_pass_duration function

           Parameters:
               none

           Returns:
               void
    """

    # first need to write the test config file
    # generate test config json
    config = {
        "general":
        {
            "next_pass_type": "PRIMARY",
            "safe_mode": False,
            "pass_start_timestamp": 1727292818,
            "pass_end_timestamp": 1727292968,
            "pre_pass_init": 60,
            "post_pass_timeout": 60,
            "altitude": 500,
            "pass_completion_time": 15
        },
        "cameras":
        {
            "basler":
            {
                "imgs_per_pass": 10,
                "finaltimeoffset": 6,
                "properties":
                {
                    "gain":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "trigger_type":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_mode":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_auto":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_time":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "black_level":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "white_balance":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "pixel_format":
                    {
                        "value": "BayerRG12",
                        "default": "BayerRG12"
                    },
                    "saturation":
                    {
                        "value": -1,
                        "default": -1
                    }
                }
            },
            "tau":
            {
                "imgs_per_pass": 50,
                "imgs_per_calibration": 5,
                "finaltimeoffset": 6,
                "properties": {
                    "gain_mode": {
                        "value": "High",
                        "default": "Automatic"
                    },
                    "agc_type": {
                        "value": "PlateauHistogram",
                        "default": "PlateauHistogram"
                    },
                    "contrast": {
                        "value": 50,
                        "default": 32
                    },
                    "brightness": {
                        "value": 120,
                        "default": 0
                    }
                }
            }
        },
        "sensors": {
            "collection_cadence": 10,
            "T_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "CPU_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "T_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            }
        }
    }

    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/config.json', r'/home/debian/Scheduler/configtemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/config.json', 'w') as jsonFile:
        json.dump(config, jsonFile)

    correctduration = 150

    # now retrieve pass duration using config
    config = Config()
    configduration = config.get_pass_duration()

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert configduration == correctduration

def test_write_timestamps():
    """
           Tests the write_timestamps function by running the write_timestamps function and then checking the
           config.json file for the correct timestamps
           Parameters:
               none

           Returns:
               void
    """

    passStartTime = 0
    passFinishTime = 200

    config = Config()

    # write the new start and end times to config file
    config.write_timestamps(passStartTime, passFinishTime)

    retrievedpassStartTime = config.configFull.general.pass_start_timestamp
    retrievedpassFinishTime = config.configFull.general.pass_end_timestamp

    assert retrievedpassStartTime == passStartTime
    assert retrievedpassFinishTime == passFinishTime

def test_enter_safe_mode():
    """
           Tests the enter_safe_mode function by running the enter_safe_mode function and then checking the
           config.json file for the correct safe mode flag
           Parameters:
               none

           Returns:
               void
    """

    config = Config()

    # write the new start and end times to config file
    config.enter_safe_mode()

    retrievedsafemode = config.configFull.general.safe_mode

    assert retrievedsafemode == True

def test_exit_safe_mode():
    """
           Tests the enter_safe_mode function by running the enter_safe_mode function and then checking the
           config.json file for the correct safe mode flag
           Parameters:
               none

           Returns:
               void
    """

    config = Config()

    # write the new start and end times to config file
    config.exit_safe_mode()

    retrievedsafemode = config.configFull.general.safe_mode

    assert retrievedsafemode == False


def test_recentpasstimestamp():
    """
           Tests the recentpasstimestamp function by running the write_timestamps function and then checking the
           against the hardcoded input
           Parameters:
               none

           Returns:
               void
    """

    # first need to write the test config file
    # generate test config json
    config = {
        "general":
        {
            "next_pass_type": "PRIMARY",
            "safe_mode": False,
            "pass_start_timestamp": 1727292818,
            "pass_end_timestamp": 1727292968,
            "pre_pass_init": 60,
            "post_pass_timeout": 60,
            "altitude": 500,
            "pass_completion_time": 15
        },
        "cameras":
        {
            "basler":
            {
                "imgs_per_pass": 10,
                "finaltimeoffset": 6,
                "properties":
                {
                    "gain":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "trigger_type":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_mode":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_auto":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_time":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "black_level":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "white_balance":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "pixel_format":
                    {
                        "value": "BayerRG12",
                        "default": "BayerRG12"
                    },
                    "saturation":
                    {
                        "value": -1,
                        "default": -1
                    }
                }
            },
            "tau":
            {
                "imgs_per_pass": 50,
                "imgs_per_calibration": 5,
                "finaltimeoffset": 6,
                "properties": {
                    "gain_mode": {
                        "value": "High",
                        "default": "Automatic"
                    },
                    "agc_type": {
                        "value": "PlateauHistogram",
                        "default": "PlateauHistogram"
                    },
                    "contrast": {
                        "value": 50,
                        "default": 32
                    },
                    "brightness": {
                        "value": 120,
                        "default": 0
                    }
                }
            }
        },
        "sensors": {
            "collection_cadence": 10,
            "T_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "CPU_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "T_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            }
        }
    }

    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/config.json', r'/home/debian/Scheduler/configtemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/config.json', 'w') as jsonFile:
        json.dump(config, jsonFile)

    retrievedpasstimestamp = 1727292818

    #now retrieving it using config
    config = Config()

    passtimestamp = float(config.recentpasstimestamp())

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert passtimestamp == retrievedpasstimestamp

def test_set_operation_type():
    """
           Tests the set_operation_type function by running the get_config function and then checking the output
           against the hardcoded input
           Parameters:
               none

           Returns:
               void
    """

    # first need to write the test config file
    # generate test config json
    config = {
        "general":
        {
            "next_pass_type": "PRIMARY",
            "safe_mode": False,
            "pass_start_timestamp": 1727292818,
            "pass_end_timestamp": 1727292968,
            "pre_pass_init": 60,
            "post_pass_timeout": 60,
            "altitude": 500,
            "pass_completion_time": 15
        },
        "cameras":
        {
            "basler":
            {
                "imgs_per_pass": 10,
                "finaltimeoffset": 6,
                "properties":
                {
                    "gain":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "trigger_type":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_mode":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_auto":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "exposure_time":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "black_level":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "white_balance":
                    {
                        "value": -1,
                        "default": -1
                    },
                    "pixel_format":
                    {
                        "value": "BayerRG12",
                        "default": "BayerRG12"
                    },
                    "saturation":
                    {
                        "value": -1,
                        "default": -1
                    }
                }
            },
            "tau":
            {
                "imgs_per_pass": 50,
                "imgs_per_calibration": 5,
                "finaltimeoffset": 6,
                "properties": {
                    "gain_mode": {
                        "value": "High",
                        "default": "Automatic"
                    },
                    "agc_type": {
                        "value": "PlateauHistogram",
                        "default": "PlateauHistogram"
                    },
                    "contrast": {
                        "value": 50,
                        "default": 32
                    },
                    "brightness": {
                        "value": 120,
                        "default": 0
                    }
                }
            }
        },
        "sensors": {
            "collection_cadence": 10,
            "T_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "CPU_TEMP":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "T_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "B_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            },
            "A_CUR":
            {
                "warn_threshold": 10,
                "error_threshold": 20
            }
        }
    }

    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/config.json', r'/home/debian/Scheduler/configtemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/config.json', 'w') as jsonFile:
        json.dump(config, jsonFile)

    # now retrieving it using config
    config = Config()

    config.set_operation_type("UPDATEDVALUE") # Update the entry

    retrievedvalue = config.configFull.general.next_pass_type

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert "UPDATEDVALUE" == retrievedvalue




