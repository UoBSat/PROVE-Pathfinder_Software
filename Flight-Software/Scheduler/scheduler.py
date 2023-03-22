''' @file scheduler.py

 @brief Defines the scheduler service.

 @section description_scheduler Description
 Defines the scheduler service that runs each of the individual tasks to be performed each pass. The config.json file
 is used to store this information and the tasks.json file is used to record what tasks are to be performed
 - bus_read
 - if_pass_started
 - if_pass_finished
 - if_pass_fully_completed
 - check_subprocesses_status
 - kill_subprocess
 - main (scheduler)


 @section libraries_scheduler Libraries/Modules
 - python subprocess library
 - python time library
 - python datetime library
 - python sys library
 - python os library
 - python signal library


 @section todo_scheduler TODO
 - None.

 @section author_scheduler Author(s)
 - Created by Vilius Stonkus on 02/08/2021.
 - Modified by Louis Timperley on 02/08/2021.
'''
import Adafruit_BBIO.GPIO as GPIO
import subprocess
import time
import datetime
import sys
import os
import signal
sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger
from shared.tasks import Tasks

def bus_read():
    """
    Description

        Parameters:
            void

        Returns:
            True/False (boolean) - 
    """
    
    # read the information from the bus
    # TODO: if no info received, return False, else return info

    return False

def if_pass_started(current_date, config: Config):
    """
    Checks whether the pass is ongoing

        Parameters:
            currentTime (float): Current timestamp at time of function call
            config (object): Object containing configuration information

        Returns:
            True/False (boolean) - represents the state of the pass. True if the pass is ongoing, False otherwise
    """

    if config.configFull.general.pass_start_timestamp is not None and config.configFull.general.pass_end_timestamp is not None:
        if (current_date + config.configFull.general.pre_pass_init) >= config.configFull.general.pass_start_timestamp:
            if (current_date + config.configFull.general.pre_pass_init) <= config.configFull.general.pass_end_timestamp:
                return True

    return False

def if_pass_finished(current_date, config: Config):
    """
    Checks whether the pass has finished

        Parameters:
            currentTime (float): Current timestamp at time of function call
            config (object): Object containing configuration information

        Returns:
            True/False (boolean) - represents the state of the pass. True if the pass has finished, False otherwise
    """

    if config.configFull.general.pass_start_timestamp is not None and config.configFull.general.pass_end_timestamp is not None:
        if current_date > config.configFull.general.pass_end_timestamp:
            return True

    return False

def if_pass_fully_completed(current_date, config: Config):
    """
    Checks if pass subprocesses have reached their extra time allowed after the pass, and thus, the pass was fully completed

        Parameters:
            currentTime (float): Current timestamp at time of function call
            config (object): Object containing configuration information

        Returns:
            True/False (boolean) - represents the state of the complete pass. True if the pass has reached its extra time, False otherwise
    """

    if config.configFull.general.pass_start_timestamp is not None and config.configFull.general.pass_end_timestamp is not None:
        if (current_date + config.configFull.general.pre_pass_init) > config.configFull.general.pass_end_timestamp + config.configFull.general.pass_completion_time:
            return True

    return False

def check_subprocesses_status(logger, tasks, complete_flag):
    """
    Checks the status of all subprocesess that are currently in progress and detects whether the process has terminated

        Parameters:
            logger (object): Object containing information on how to write logs
            tasks (object): Object containing tasks information
            complete_flag (bool): Boolean, only true if the scheduler has previously logged completion of all tasks

        Returns:
            complete_flag (bool): Boolean, only true if the scheduler has previously logged completion of all tasks
    """

    for process, task_ in tasks.tasks_in_progress:
        task_id = task_["id"]
        task_delay = task_["delay"]
        poll_proc = process.poll()


        # if process has terminated and has not been included to the list of completed tasks
        if poll_proc is not None and task_id not in tasks.tasks_done:

            # subproc has terminated
            logger.info(f"Process ID: {str(task_id)}, PID: {str(process.pid)} has finished")

            tasks.tasks_in_progress.remove((process, task_))

            # Append the process to an array so that it wasnt repeated
            tasks.tasks_done.append(task_id)

            logger.info("Tasks done:")
            for task in tasks.tasks_done:
                logger.info(str(task))

            # Execute the delay
            logger.info("Waiting "+str(task_delay)+" secs before the next task...")
            time.sleep(task_delay)

    # consider the state of the complete_flag and whether it needs changing to false
    if len(tasks.tasks_in_progress) != 0:
        complete_flag = False

    # log completion of all tasks
    if len(tasks.tasks_done) == tasks.tasks_total and complete_flag is False:
        logger.info("All tasks done!")
        logger.info("Tasks done:")
        for task in tasks.tasks_done:
            logger.info(str(task))
        logger.info("Stopping...")
        complete_flag = True
        
    return complete_flag

def kill_subprocess(process, task, tasks,logger):
    """
    Kills the subprocess

        Parameters:
            process (object) - a subprocess.Popen object
            task (object) - a json object containing the properties of the task
            logger (object): Object containing information on how to write logs
            tasks (object): Object containing tasks information

        Returns:
            void
    """

    task_id = task["id"]
    task_delay = task["delay"]
    logger.warning(f"STOPPING process ID: {task_id}, PID: {process.pid}")
    os.killpg(os.getpgid(process.pid), signal.SIGKILL)

    tasks_in_progress_copy = [(process, task_) for (process, task_) in tasks.tasks_in_progress if task_['id'] != task_id]
    tasks.tasks_in_progress = tasks_in_progress_copy

    # Append the process to an array so that it wasnt repeated
    tasks.tasks_done.append(task_id)

    logger.info("Tasks done:")
    for task in tasks.tasks_done:
        logger.info(str(task))

    # Execute the delay
    logger.info("Waiting "+str(task_delay)+" secs before the next task...")
    time.sleep(task_delay)

def primary_pass_operations(pass_ongoing, complete_flag, config: Config, tasks, logger):
    """
    contains all the logic to perform all the tasks associated with a primary imaging pass

        Parameters:
            pass_ongoing (boolean) - a flag denoting if the pass has started yet
            complete_flag (boolean) - a flag denoting if the pass is complete
            config (object): Object containing configuration information
            tasks (object): Object containing tasks information
            logger (object): Object containing information on how to write logs

        Returns:
            complete_flag (boolean) - a flag denoting if the pass is complete
            pass_ongoing (boolean) - a flag denoting if the pass has started yet
    """
    PassType = "PRIMARY"
    # check if pass started/finished
    current_date = datetime.datetime.now().timestamp()
    pass_started = if_pass_started(current_date, config)
    pass_finished = if_pass_finished(current_date, config)

    # check if pass subprocesses have reached their extra time allowed after the pass
    current_date = datetime.datetime.now().timestamp()
    pass_fully_completed = if_pass_fully_completed(current_date, config)

    if pass_started and not pass_ongoing:
        tasks.tasks_done = []
        pass_ongoing = True
    if not pass_started and pass_ongoing:
        pass_ongoing = False

    # Check the status of subprocesses
    complete_flag = check_subprocesses_status(logger, tasks, complete_flag)

    # Go through all tasks
    for task in tasks.tasks["tasks"]:
        if pass_ongoing:
            # Start pass tasks simultaneously
            for task_pass in tasks.tasks['tasks']['pass']:
                currentTime = datetime.datetime.now().timestamp()
                proc = tasks.start_task(currentTime, pass_ongoing, task_pass, config, logger,PassType)
        elif not pass_ongoing and pass_finished and pass_fully_completed:
            # Stop any unfinished pass tasks
            if tasks.tasks_in_progress:
                tasksIds = tasks.pass_tasks_ids(PassType)
                for process, task_ in tasks.tasks_in_progress:
                    if task_["id"] in tasksIds:
                        kill_subprocess(process, task_, tasks, logger)

            # Start post-pass tasks non-simultaneously (wait for one to complete)
            for task_post_pass in tasks.tasks['tasks']['post_pass']:
                currentTime = datetime.datetime.now().timestamp()
                proc = tasks.start_task(currentTime, pass_ongoing, task_post_pass, config, logger,PassType)

                if proc is not None:
                    try:
                        proc.communicate(timeout=config.configFull.general.post_pass_timeout)
                    except subprocess.TimeoutExpired as e:
                        # Stop post-pass subprocess due to timeout
                        logger.warning(e)
                        kill_subprocess(proc, task_post_pass, tasks, logger)

                    # Wait for a proc to complete and check the status of all subprocesses
                    complete_flag = check_subprocesses_status(logger, tasks, complete_flag)
    return pass_ongoing,complete_flag,config,tasks,logger

def calibration_pass_operations(pass_ongoing, complete_flag, config: Config, tasks, logger):
    """
    contains all the logic to perform all the tasks associated with a calibration pass

        Parameters:
            pass_ongoing (boolean) - a flag denoting if the pass has started yet
            complete_flag (boolean) - a flag denoting if the pass is complete
            config (object): Object containing configuration information
            tasks (object): Object containing tasks information
            logger (object): Object containing information on how to write logs

        Returns:
            complete_flag (boolean) - a flag denoting if the pass is complete
            pass_ongoing (boolean) - a flag denoting if the pass has started yet
    """
    PassType = "CALIBRATION"
    # check if pass started/finished
    current_date = datetime.datetime.now().timestamp()
    pass_started = if_pass_started(current_date, config)
    pass_finished = if_pass_finished(current_date, config)

    # check if pass subprocesses have reached their extra time allowed after the pass
    current_date = datetime.datetime.now().timestamp()
    pass_fully_completed = if_pass_fully_completed(current_date, config)

    if pass_started and not pass_ongoing:
        tasks.tasks_done = []
        pass_ongoing = True
    if not pass_started and pass_ongoing:
        pass_ongoing = False

    # Check the status of subprocesses
    complete_flag = check_subprocesses_status(logger, tasks, complete_flag)

    # Go through all tasks
    for task in tasks.tasks["tasks"]:
        if pass_ongoing:
            # Start pass tasks simultaneously
            for task_pass in tasks.tasks['tasks']['calibration']:
                currentTime = datetime.datetime.now().timestamp()
                proc = tasks.start_task(currentTime, pass_ongoing, task_pass, config, logger,PassType)
        elif not pass_ongoing and pass_finished and pass_fully_completed:
            # Stop any unfinished pass tasks
            if tasks.tasks_in_progress:
                tasksIds = tasks.pass_tasks_ids(PassType)
                for process, task_ in tasks.tasks_in_progress:
                    if task_["id"] in tasksIds:
                        kill_subprocess(process, task_, tasks, logger)

            # Start post-pass tasks non-simultaneously (wait for one to complete)
            for task_post_pass in tasks.tasks['tasks']['post_calibration']:
                currentTime = datetime.datetime.now().timestamp()
                proc = tasks.start_task(currentTime, pass_ongoing, task_post_pass, config, logger,PassType)

                if proc is not None:
                    try:
                        proc.communicate(timeout=config.general.post_pass_timeout)
                    except subprocess.TimeoutExpired as e:
                        # Stop post-pass subprocess due to timeout
                        logger.warning(e)
                        kill_subprocess(proc, task_post_pass, tasks, logger)

                    # Wait for a proc to complete and check the status of all subprocesses
                    complete_flag = check_subprocesses_status(logger, tasks, complete_flag)
    return pass_ongoing, complete_flag, config, tasks, logger


def main():
    """
    Runs the scheduler loop, starts, kills and monitors task subprocesses, logs their outputs

        Parameters:
            void

        Returns:
            void
    """
    # Create a custom logger
    logger = create_logger("Scheduler", "/media/SD1/logs.log")

    # pull down camera power pins
    logger.info("Pulling camera power pins low")
    GPIO.setup("P8_8", GPIO.OUT)
    GPIO.output("P8_8", GPIO.LOW)
    GPIO.setup("P8_12", GPIO.OUT)
    GPIO.output("P8_12", GPIO.LOW)
    # Cleanup GPIO pins
    GPIO.cleanup()

    tasks = Tasks()
    config = Config()

    logger.info("STARTING THE SCHEDULER")


    Pass_Ongoing = False
    Complete_Flag = False
    safe_logged = False

    logger.info(f"performing {config.configFull.general.next_pass_type} pass")

    while True:

        # read the bus for new updates
        bus = bus_read()
        if bus:
            # Stop all ongoing processes if new pass data is coming from bus
            if tasks.tasks_in_progress:
                for process, task_ in tasks.tasks_in_progress:
                    kill_subprocess(process, task_, tasks,logger)

            # TODO: check what type of information received
            #       if info on next pass received, edit config.json
            return

        # check type of next pass
        try:
            if config.configFull.general.safe_mode is False:
                safe_logged = False
                if config.configFull.general.next_pass_type == "PRIMARY":
                    Pass_Ongoing, Complete_Flag, config, tasks, logger = primary_pass_operations(Pass_Ongoing,Complete_Flag,
                                                                                                 config,tasks,logger)
                elif config.configFull.general.next_pass_type == "CALIBRATION":
                      Pass_Ongoing, Complete_Flag, config, tasks, logger = calibration_pass_operations(Pass_Ongoing,
                                                                                                 Complete_Flag,
                                                                                                 config, tasks, logger)
            else:
                if safe_logged is False:
                    logger.warning("SCHEDULER IN SAFE MODE")
                    safe_logged = True
        except:
            logger.exception("Incorrect next pass type")


        time.sleep(1)
if __name__ == "__main__":
    main()