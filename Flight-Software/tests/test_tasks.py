''' @file test_tasks.py

@brief Defines test for the tasks class methods.

@section description_test_tasks Description
Defines the unit tests for the tasks class methods
- test_get_tasks
- test_get_tasks_total
- test_pass_tasks_ids
- test_capture_timgings
- test_array_to_string
- test_post_pass_capture_timings
- test_start_task


@section libraries_tasks Libraries/Modules
- python pytest library
- python sys library
- python json library

@section todo_tasks TODO
- None.

@section author_tasks Author(s)
- Created by Louis Timperley on 13/08/2021.
'''

import pytest
import json
import os
import logging
import numpy as np
from numpy.linalg import norm
import sys
import datetime
sys.path.append('/home/debian')
from shared.tasks import Tasks
from shared.config import Config
from shared.logging import create_logger

def test_get_tasks():
    """
           Tests the initialisation of the tasks object, i.e. the get_tasks function, by comparing the string version of
           tasks.tasks to the string directly retrieved from tasks.json

           Parameters:
               none

           Returns:
               void
    """
    # first need to write the test tasks file
    # generate test tasks json
    tasks = {
        "tasks":
        {
            "pass":
            [
                {
                    "id": 1,
                    "name": "Start Basler Capture",
                    "file_path": "/home/debian/Tasks/basler/basler.py",
                    "delay": 0
                },
                {
                    "id": 2,
                    "name": "Start Tau Capture",
                    "file_path": "/home/debian/Tasks/tau2/tau.py",
                    "delay": 0
                }
            ],
            "post_pass":
            [
                {
                    "id": 4,
                    "name": "Transfer pass images to SD card",
                    "file_path": "/home/debian/Tasks/Transfer-to-storage/transfer_images_SD.py",
                    "delay": 0
                },
            ]
        }
    }
    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/tasks.json', r'/home/debian/Scheduler/taskstemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/tasks.json', 'w') as jsonFile:
        json.dump(tasks, jsonFile)

    tasks = Tasks() # create and initialise tasks object


    assert tasks.tasks["tasks"]["pass"] ==             [
                {
                    "id": 1,
                    "name": "Start Basler Capture",
                    "file_path": "/home/debian/Tasks/basler/basler.py",
                    "delay": 0
                },
                {
                    "id": 2,
                    "name": "Start Tau Capture",
                    "file_path": "/home/debian/Tasks/tau2/tau.py",
                    "delay": 0
                }
            ]
    assert tasks.tasks["tasks"]["post_pass"] == [
                {
                    "id": 4,
                    "name": "Transfer pass images to SD card",
                    "file_path": "/home/debian/Tasks/Transfer-to-storage/transfer_images_SD.py",
                    "delay": 0
                },
            ]

    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')


def test_get_tasks_total():
    """
           Tests the initialisation of the tasks object, i.e. the get_tasks_total function, by comparing the number of
           tasks found in the tasks.json file to the result of the get_tasks_total function

           Parameters:
               none

           Returns:
               void
    """
    # first need to write the test tasks file
    # generate test tasks json
    tasks = {
        "tasks":
            {
                "pass":
                    [
                        {
                            "id": 1,
                            "name": "Start Basler Capture",
                            "file_path": "/home/debian/Tasks/basler/basler.py",
                            "delay": 0
                        },
                        {
                            "id": 2,
                            "name": "Start Tau Capture",
                            "file_path": "/home/debian/Tasks/tau2/tau.py",
                            "delay": 0
                        }
                    ],
                "post_pass":
                    [
                        {
                            "id": 4,
                            "name": "Transfer pass images to SD card",
                            "file_path": "/home/debian/Tasks/Transfer-to-storage/transfer_images_SD.py",
                            "delay": 0
                        },
                    ]
            }
    }
    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/tasks.json', r'/home/debian/Scheduler/taskstemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/tasks.json', 'w') as jsonFile:
        json.dump(tasks, jsonFile)

    # now use the tasks class
    tasks = Tasks() # create and initialise tasks object

    assert tasks.tasks_total == 3

    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')


def test_pass_tasks_ids():
    """
           Tests the pass_tasks_ids function, by directly defining the json file and comparing to the
           result from the pass_tasks_ids function

           Parameters:
               none

           Returns:
               void
    """
    # first need to write the test tasks file
    # generate test tasks json
    tasks = {
        "tasks":
            {
                "pass":
                    [
                        {
                            "id": 1,
                            "name": "Start Basler Capture",
                            "file_path": "/home/debian/Tasks/basler/basler.py",
                            "delay": 0
                        },
                        {
                            "id": 2,
                            "name": "Start Tau Capture",
                            "file_path": "/home/debian/Tasks/tau2/tau.py",
                            "delay": 0
                        }
                    ],
                "post_pass":
                    [
                        {
                            "id": 4,
                            "name": "Transfer pass images to SD card",
                            "file_path": "/home/debian/Tasks/Transfer-to-storage/transfer_images_SD.py",
                            "delay": 0
                        },
                    ]
            }
    }
    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/tasks.json', r'/home/debian/Scheduler/taskstemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/tasks.json', 'w') as jsonFile:
        json.dump(tasks, jsonFile)

    # now use the tasks class
    tasks = Tasks()  # create and initialise tasks object
    PassType = "PRIMARY"
    ids = tasks.pass_tasks_ids(PassType) # return result from pass_tasks_ids


    # and compare to result from class version
    assert ids == [1,2] #only meant to return pass task ids

    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')

def test_capture_timings():
    """
           Tests the capture_timings function, is various simplied cases then in a more complex case by retrieving
           timings returned from the capture_timings function. It then tests that the captures calculated for this case
           are in fact at equal angle increments around the target.
           Parameters:
               none

           Returns:
               void
    """

    # CASE A
    # test the two capture case, where the time between the captures is equal to the duration of that pass (with no
    # final offset)
    numberOfImages = 2
    orbitalAltitude = 500
    startTime = 0
    endTime = 200
    finalOffset = 0

    tasksA = Tasks()  # create and initialise tasks object
    CapA = tasksA.capture_timings(numberOfImages, orbitalAltitude, startTime, endTime, finalOffset)

    assert CapA[0] == 0
    assert CapA[1] == pytest.approx(200)

    # CASE B
    # test the two capture case, where the time between the captures is equal to the duration of that pass minus a
    # defined offset
    numberOfImages = 2
    orbitalAltitude = 500
    startTime = 0
    endTime = 200
    finalOffset = 5

    tasksB = Tasks()  # create and initialise tasks object
    CapB = tasksB.capture_timings(numberOfImages, orbitalAltitude, startTime, endTime, finalOffset)

    assert CapB[0] == 0
    assert CapB[1] == pytest.approx(195)

    # CASE C
    # test the three capture case, where the time between the captures is equal to half the duration of that pass (with
    # no final offset)
    numberOfImages = 3
    orbitalAltitude = 500
    startTime = 0
    endTime = 200
    finalOffset = 0

    tasksC = Tasks()  # create and initialise tasks object
    CapC = tasksC.capture_timings(numberOfImages, orbitalAltitude, startTime, endTime, finalOffset)

    assert CapC[0] == 0
    assert CapC[1] == pytest.approx(100)
    assert CapC[2] == pytest.approx(200)

    # CASE D
    # test the three capture case, where the time between the captures is equal to half the duration of that pass minus
    # a defined offset
    numberOfImages = 3
    orbitalAltitude = 500
    startTime = 0
    endTime = 200
    finalOffset = 10

    tasksD = Tasks()  # create and initialise tasks object
    CapD = tasksD.capture_timings(numberOfImages, orbitalAltitude, startTime, endTime, finalOffset)

    assert CapD[0] == 0
    assert CapD[1] == pytest.approx(95)
    assert CapD[2] == pytest.approx(190)

    #CASE E
    # finally testing a more complex case, with 10 images(even case), 500km altitude and 200 second duration,
    # with no final offset, and checking all angles between captures are correct. This therefore still checks the output
    # of the capture_timings function, but uses entirely different maths and lines of code to get there
    numberOfImages = 10
    orbitalAltitude = 500
    startTime = 0
    endTime = 200
    finalOffset = 0

    tasksE = Tasks()  # create and initialise tasks object
    capsE = tasksE.capture_timings(numberOfImages,orbitalAltitude,startTime,endTime,finalOffset)

    Re = 6.3781 * pow(10, 6)  # radius of earth
    a = Re + orbitalAltitude * pow(10, 3)  # semi major axis
    mu = 3.986004418 * pow(10, 14)  # earth's gravitational parameter
    V = pow(mu / a, 0.5)  # orbital speed

    pathLength = (endTime - startTime) * V
    pathLengthProjected = 2 * a * np.sin(pathLength / (a * 2))
    orbitalAltitudeProjected = a * np.cos(pathLength / (a * 2)) - Re
    TotalAngleThroughPass = 2*np.arctan((pathLengthProjected / 2) /orbitalAltitudeProjected)# measured from target
    correctAngle = TotalAngleThroughPass/(numberOfImages-1)# measured from target

    Alpha = np.arctan(orbitalAltitudeProjected / (pathLengthProjected/2) )
    totalAngleFromXAxis1 = np.arcsin(Re * np.sin(np.pi/2 + Alpha) / a) + Alpha# sine rule and angles in a triangle

    X1 = - a * np.cos(totalAngleFromXAxis1) # x position at starting capture
    Y1 = a * np.sin(totalAngleFromXAxis1) # y position at starting capture

    for i in range(len(capsE)-1): # test the angle between each capture
        totalAngleFromXAxis2  = (capsE[i+1] - capsE[i]) * V / a + totalAngleFromXAxis1

        X2 = - a * np.cos(totalAngleFromXAxis2)  # x position at second capture
        Y2 = a * np.sin(totalAngleFromXAxis2)  # y position at second capture

        # construct vectors between each capture location and the target
        V1 = np.array([0 - X1, Y1 - Re])
        V2 = np.array([0 - X2, Y2 - Re])

        # now find the angle between each capture using dot vector multiplication
        cos =np.dot(V1, V2) / norm(V1) / norm(V2)
        AnglebetweenCaputres = np.arccos(np.clip(cos, -1.0, 1.0))

        #reassign initial values
        X1 = X2
        Y1 = Y2
        totalAngleFromXAxis1 = totalAngleFromXAxis2

    assert AnglebetweenCaputres == pytest.approx(correctAngle)


def test_array_to_string():
    """
           Tests the array_to_string function, by defining an array and comparing the string version of this to the
           result of the array_to_string function

           Parameters:
               none

           Returns:
               void
    """
    testarray = ["t","e","s","t","i","n","g","a","r","r","a","y","t","o","s","t","r","i","n","g"]

    tasks = Tasks()  # create and initialise tasks object
    result =  tasks.array_to_string(testarray)

    assert result == " t e s t i n g a r r a y t o s t r i n g"

def test_post_pass_capture_timings():
    """
           Tests the post_pass_capture_timings function, by defining the expected timings and comparing the string
           version of these to the result of the post_pass_capture_timings function

           Parameters:
               none

           Returns:
               void
    """

    tasks = Tasks()
    result = tasks.post_pass_capture_timings(5,5,10)

    assert result == " 10.0 20.0 30.0 40.0 50.0" #the function returns a string

def test_start_task(caplog):
    """
           Tests the start_task function, by defining the config and tasks json files, then starting tasks according to
           these files and checking they have started correctly by consulting the logs.

           Parameters:
               caplog (fixture): a fixture provided by pytest to capture logs generated in a test

           Returns:
               void
    """
    # first need to write the test tasks file
    # generate test tasks json
    tasks = {
        "tasks":
            {
                "pass":
                    [
                        {
                            "id": 1,
                            "name": "Start Basler Capture",
                            "file_path": "/home/debian/Tasks/basler/basler.py",
                            "delay": 0
                        },
                        {
                            "id": 2,
                            "name": "Start Tau Capture",
                            "file_path": "/home/debian/Tasks/tau2/tau.py",
                            "delay": 0
                        }
                    ],
                "post_pass":
                    [
                        {
                            "id": 4,
                            "name": "Transfer pass images to SD card",
                            "file_path": "/home/debian/Tasks/Transfer-to-storage/transfer_images_SD.py",
                            "delay": 0
                        },
                        {
                            "id": 8,
                            "name": "TEST PROCESS",
                            "file_path": "/home/debian/tests/test_process.py",
                            "delay": 0
                        }
                    ]
            }
    }
    # rename normal version of config to configtemp.json
    os.rename(r'/home/debian/Scheduler/tasks.json', r'/home/debian/Scheduler/taskstemp.json')

    # Write the object to file.
    with open('/home/debian/Scheduler/tasks.json', 'w') as jsonFile:
        json.dump(tasks, jsonFile)

    # also need to write the test config file
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

    # now use the tasks class
    tasks = Tasks()  # create and initialise tasks object

    pass_started = True
    task1 = tasks.tasks['tasks']['post_pass'][1] # should start a test process (id is 8 to not conflict with previous
    # test tasks)
    config = Config()
    logger = create_logger("test_start_task", "testlog.log")
    caplog.set_level(logging.INFO)

    currentTime = 1727292828 # time during pass
    testProcess = tasks.start_task(currentTime,pass_started, task1, config, logger,"PRIMARY")  # return result from pass_tasks_ids

    os.remove("testlog.log")
    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')
    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert caplog.records[1].message == "Process {id: 8} has started..."

