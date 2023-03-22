''' @file test_scheduler.py

@brief Defines test for the scheduler service.

@section description_test_scheduler Description
Defines the unit tests for the scheduler service functions
- test_if_pass_started
- test_if_pass_finished
- test_pass_fully_completed
- test_check_subprocesses_status
- test_kill_subprocess

@section libraries_scheduler Libraries/Modules
- python pytest library
- python sys library
- python json library

@section todo_scheduler TODO
- None.

@section author_scheduler Author(s)
- Created by Louis Timperley on 20/08/2021.
'''
import pytest
import subprocess
import signal
import time
import os
import logging
import json
import sys
sys.path.append('/home/debian')
from shared.config import Config
from shared.tasks import Tasks
from shared.logging import create_logger
import Scheduler.scheduler

def test_if_pass_started():
    """
        tests the if_pass_started function by rewriting writing the config file then using hardcoded values of the
        current time to check the returned boolean from the the function

            Parameters:
                void

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

    config = Config()

    # now check with if_pass_started function
    currentTime = 1727292823 # time after the start of the pass
    result = Scheduler.scheduler.if_pass_started(currentTime,config)

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json',r'/home/debian/Scheduler/config.json')

    assert result is True

    currentTime = 1727292813 # time before the start of the pass
    result = Scheduler.scheduler.if_pass_started(currentTime,config)

    assert result is False

def test_if_pass_finished():
    """
        tests the if_pass_finished function by rewriting writing the config file then using hardcoded values of the
        current time to check the returned boolean from the the function

            Parameters:
                void

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

    config = Config()

    # now check with if_pass_finished function
    currentTime = 1727292972 # time after the end of the pass
    result = Scheduler.scheduler.if_pass_finished(currentTime,config)

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert result is True

    currentTime = 1727292963 # time before the end of the pass
    result = Scheduler.scheduler.if_pass_finished(currentTime,config)

    assert result is False

def test_pass_fully_completed():
    """
        tests the pass_fully_completed function by rewriting writing the config file then using hardcoded values of the
        current time to check the returned boolean from the the function

            Parameters:
                void

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

    config = Config()

    # now check with if_pass_fully_completed function
    currentTime = 1727293968 # time after the end of the pass plus task completion time
    result = Scheduler.scheduler.if_pass_fully_completed(currentTime,config)

    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert result is True

    currentTime = 1727292980# time before the end of the pass plus task completion time
    result = Scheduler.scheduler.if_pass_fully_completed(currentTime,config)

    assert result is False

def test_check_subprocesses_status(caplog):
    """
           Tests the check_subprocesses_status function by starting a process then recording the logs generated by the
           check_subprocesses_status function. It ensures the function correctly logs when all tasks are complete and
           when a task has completed on its own is correctly moved to the task_done list. It also checks that the
           function only logs log that all tasks have completed once

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
                            "id": 7,
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

    tasks = Tasks()

    # need to start a subprocess
    pass_started = True
    task1 = tasks.tasks['tasks']['pass'][0]  # should start an arducam capture task (id is 1)
    config = Config()
    logger = create_logger("test_check_subprocesses_status", "testlog.log")
    caplog.set_level(logging.INFO)

    # first testing the check_subprocesses_status function correctly logs completion of all tasks
    totalTasksOriginal = tasks.tasks_total
    tasks.tasks_total = 1  # artificially reduce total tasks to one

    # Execute the process by a file path
    task_path = task1["file_path"]
    task_id = task1["id"]
    testProcess1 = subprocess.Popen(("python3 " + task_path),
                                    shell=True,
                                    stdin=None,
                                    stdout=None,
                                    stderr=subprocess.STDOUT,
                                    preexec_fn=os.setsid)

    logger.info("Process {id: " + str(task_id) + "} has started...")
    tasks.tasks_in_progress.append((testProcess1, task1))

    # now kill the process
    logger.warning(f"STOPPING process ID: {task_id}, PID: {testProcess1.pid}")
    os.killpg(os.getpgid(testProcess1.pid), signal.SIGKILL)

    tasks_in_progress_copy = [(process, task_) for (process, task_) in tasks.tasks_in_progress if
                              task_['id'] != task_id]
    tasks.tasks_in_progress = tasks_in_progress_copy

    # Append the process to an array so that it wasnt repeated
    tasks.tasks_done.append(task_id)

    logger.info("Tasks done:")
    for task in tasks.tasks_done:
        logger.info(str(task))

    complete_flag = False
    complete_flag = Scheduler.scheduler.check_subprocesses_status(logger,tasks,complete_flag)

    os.remove("testlog.log")
    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')
    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')


    assert caplog.records[4].message == "All tasks done!"
    assert caplog.records[6].message == "1"  # same id as one the one just completed

    # now check the the all task done! log is not repeated
    complete_flag = Scheduler.scheduler.check_subprocesses_status(logger, tasks, complete_flag)

    assert len(caplog.records) == 8  # number of logs generated prior to second call of check_subprocess_status

    # now check the the all task done! log is not repeated
    complete_flag = Scheduler.scheduler.check_subprocesses_status(logger, tasks, complete_flag)

    assert len(caplog.records) == 8 # number of logs generated prior to second call of check_subprocess_status

    # Now testing that the check_subprocesses_status function correctly logs that a process has terminated/completed but
    # has not been included to the list of completed tasks, then appends it to the done list and removes it form the in
    # progress list

    # return total tasks to orignial value
    tasks.tasks_total = totalTasksOriginal

    task2 = tasks.tasks['tasks']['post_pass'][1]  # should start a test process (id is 7)
    task_path = task2["file_path"]
    task_id = task2["id"]
    testProcess2 = subprocess.Popen(("python3 " + task_path),
                                    shell=True,
                                    stdin=None,
                                    stdout=None,
                                    stderr=subprocess.STDOUT,
                                    preexec_fn=os.setsid)

    logger.info("Process {id: " + str(task_id) + "} has started...")
    tasks.tasks_in_progress.append((testProcess2, task2))

    logger.info("Tasks in progress:")
    for proc, task_ in tasks.tasks_in_progress:
        logger.info(f"ID: {str(task_['id'])}, PID: {str(proc.pid)}")

    # now kill the process but dont add it to the done list
    logger.warning(f"STOPPING process ID: {task_id}, PID: {testProcess2.pid}")
    os.killpg(os.getpgid(testProcess2.pid), signal.SIGKILL)
    time.sleep(1)

    complete_flag = False
    Scheduler.scheduler.check_subprocesses_status(logger, tasks, complete_flag)

    assert caplog.records[12].message == "Process ID: 7, PID: " + str(testProcess2.pid) + " has finished"
    assert caplog.records[15].message == "7"



def test_kill_subprocess(caplog):
    """
           Tests the kill_subprocess function by starting a process then recording the logs generated by the
           kill_subprocess function. It ensures the function correctly stops the specified task

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
                            "id": 7,
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

    tasks = Tasks()

    # need to start a subprocess
    pass_started = True
    task1 = tasks.tasks['tasks']['post_pass'][1]  # should start a test process (id is 7)
    config = Config()
    logger = create_logger("test_kill_subprocess", "testlog.log")
    caplog.set_level(logging.INFO)

    currentTime = 1727292810
    task_path = task1["file_path"]
    task_id = task1["id"]
    testProcess1 = subprocess.Popen(("python3 " + task_path),
                                    shell=True,
                                    stdin=None,
                                    stdout=None,
                                    stderr=subprocess.STDOUT,
                                    preexec_fn=os.setsid)

    logger.info("Process {id: " + str(task_id) + "} has started...")
    tasks.tasks_in_progress.append((testProcess1, task1))


    Scheduler.scheduler.kill_subprocess(testProcess1, task1, tasks, logger)

    os.remove("testlog.log")
    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')
    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')

    assert caplog.records[1].message == "STOPPING process ID: 7, PID: " + str(testProcess1.pid)

def test_safe_mode(caplog):
    """
           Tests that when the safe mode flag is set to True, the schduler does not start any task and logs that it is
           in safe mode

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
                            "id": 7,
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

    tasks = Tasks()
    config = Config()

    # restart scheduler service (if not already running), this will trigger the scheduler to enter safe mode
    process = subprocess.Popen("sudo systemctl restart scheduler.service",
                               shell=True,
                               stdin=None,
                               stdout=None,
                               stderr=subprocess.STDOUT)

    time.sleep(10)

    # opening the file in read mode
    my_file = open("/media/SD1/logs.log", "r")

    # reading the file
    data = my_file.read()

    # replacing end splitting the text
    # when newline ('\n') is seen.
    data_into_list = data.split("\n")
    my_file.close()

    # rename normal version of tasks back to tasks.json and clean
    os.rename(r'/home/debian/Scheduler/taskstemp.json', r'/home/debian/Scheduler/tasks.json')
    # rename normal version of config back to config.json and clean
    os.rename(r'/home/debian/Scheduler/configtemp.json', r'/home/debian/Scheduler/config.json')



    assert "SCHEDULER IN SAFE MODE" in data_into_list[-2]
