''' @file tasks.py

 @brief Defines the base class and functions related to performing tasks using the scheduler service.

 @section description_tasks Description
 Defines the task functions for executing all the various tasks spawned by the scheduler service, using the python
 subprocess library. The tasks.json file is used to record what tasks are to be performed each pass.
 - Tasks (base class)
 - get_tasks
 - get_tasks_total
 - pass_tasks_ids
 - capture_timings
 - array_to_string
 - post_pass_capture_timings
 - start_task


 @section libraries_tasks Libraries/Modules
 - python json library
 - python subprocess library
 - python numpy library
 - python datetime library
 - python os library
 - shared config library


 @section todo_tasks TODO
 - None.

 @section author_tasks Author(s)
 - Created by Vilius Stonkus on 02/08/2021.
 - Modified by Louis Timperley on 02/08/2021.
'''

import json
import subprocess
import numpy as np
import datetime
import os
from shared.config import *

class Tasks:
    """ The Tasks base class

    Class for controlling execution of the various tasks during an imaging pass, using the scheduler service

    ...

    Attributes
    ----------
    tasks : list
        list of tasks from the tasks.json file
    tasks_total : ing
        total number of tasks defined in the tasks.json file

    Methods
    -------
    get_tasks():
        Reads the tasks.json file and returns its content in a json object
    get_tasks_total():
        Calculates the total number of both pass and post-pass tasks
    pass_tasks_ids():
        Creates an array of pass tasks IDs
    capture_timings(n, orbitalAltitude,passStartTime,passEndTime, camera):
        Calculates the capture times of a set of images with equal angles between each capture
    array_to_string(array):
        Converts a list of string to a single string
    start_task(pass_started, task, config, logger):
        Starts a pass or post-pass task as a background subprocess

    """
    tasks_done = []
    tasks_in_progress = []
    arguments = " "

    def __init__(self):
        """
            Initialises the Tasks class, reads the tasks.json file and stores its content

            Parameters:
                self (Tasks) - default class from the Python convention

            Returns:
                void
        """
        
        self.tasks = self.get_tasks()
        self.tasks_total = self.get_tasks_total()
    
    def get_tasks(self):
        """
            Reads the tasks.json file and returns its content in a json object

            Parameters:
                self (Tasks) - default class from the Python convention

            Returns:
                data_json (object) - tasks and their parameters in a json object
        """

        f = open("/home/debian/Scheduler/tasks.json", "r")
        data_json = json.load(f)    
        f.close()

        return data_json
    
    def get_tasks_total(self):
        """
            Calculates the total number of both pass and post-pass tasks

            Parameters:
                self (Tasks) - default class from the Python convention

            Returns:
                total (int) - total number of tasks in tasks.json file
        """

        total = 0
        for task_pass in self.tasks["tasks"]["pass"]:
            total+=1
        for task_post_pass in self.tasks["tasks"]["post_pass"]:
            total+=1

        return total
    
    def pass_tasks_ids(self,passtype):
        """
            Creates an array of pass tasks IDs

            Parameters:
                self (Tasks) - default class from the Python convention
                passtype (string): a string describing what type of the pass is to be performed


            Returns:
                ids (list: int) - a list of ids of pass Tasks
        """

        ids = []

        if passtype == "PRIMARY":
            for task_pass in self.tasks["tasks"]["pass"]:
                ids.append(task_pass["id"])
        elif passtype == "CALIBRATION":
            for task_pass in self.tasks["tasks"]["calibration"]:
                ids.append(task_pass["id"])
        return ids


    def capture_timings(self, n, orbitalAltitude,passStartTime,passEndTime, finalTimeOffset):
        """
            Calculates the capture times of a set of images with equal angles between each capture

                Parameters:
                                n(Int): The number of images required in the set
                                orbitalAltitude(float): The altitude of the spacecraft (km)
                                passStartTime(float): Required time of the first image capture
                                passEndTime(float): Required time of the last image capture
                                finalTimeOffset(float): an offset to change the pass end time by, to ensure no images
                                are taken after the end of the pass

                Returns:
                    tc (list): A list of all the image capture times, as timestamps

        """

        #---------------------------------------First determining effective horizon mask--------------------------------
        passEndTime = passEndTime - finalTimeOffset

        Re = 6.3781 * pow(10, 6)  # radius of earth
        a = Re + orbitalAltitude * pow(10, 3)  # semi major axis
        mu = 3.986004418 * pow(10, 14)  # earth's gravitational parameter
        V = pow(mu / a, 0.5)  # orbital speed

        pathLength = (passEndTime - passStartTime) * V
        pathLengthProjected = 2 * a * np.sin(pathLength / (a * 2))
        orbitalAltitudeProjected = a * np.cos(pathLength / (a * 2))-Re
        Alpha = np.arctan(orbitalAltitudeProjected / (pathLengthProjected/2) ) #effective value of Horizon Mask
        firstAngleatEarthCenter = np.pi-(Alpha+np.pi/2)-np.arcsin(Re*np.sin(Alpha+np.pi/2)/a) # angle between s/c
        # and target measured from the center of the earth

        if Alpha < 30/180*np.pi:
            print("WARNING Image Pass Appears To Exceed Horizon Mask of 30 Degrees")

        #-----------------------Now calculating values of theta (angle along orbital path)------------------------------
        delta = np.linspace(Alpha, np.pi - Alpha, num=n)# angle from target local horizon
        theta = firstAngleatEarthCenter - (np.pi-(delta+np.pi/2)-np.arcsin(Re*np.sin(delta+np.pi/2)/a))
        capTimes = theta*a/V + passStartTime

        return(capTimes)

    def array_to_string(self, array):
        """
            Converts a list of string to a single string

            Parameters:
                self (Tasks): default class from the Python convention
                array (list: string): a list of strings 

            Returns:
                string (string) - a single string
        """

        string = ""
        for i in range(np.size(array)):
            string += " " + str(array[i])
        
        return string

    def post_pass_capture_timings(self,currentTime, numb, interval):
        """
            Creates a string representing the timings for a post pass task (Arducam high-res capturing task)

            Parameters:
                self (Tasks): default class from the Python convention
                currentTime (float): Current timestamp at time of function call
                numb (int): a number of timings expected
                interval (int): a time interval between separate timings

            Returns:
                string (string) - a single string with timings separated by a space
        """

        initialDelay = 5
        startTiming = currentTime + datetime.timedelta(0, initialDelay).total_seconds()
        endTiming = currentTime + datetime.timedelta(0, initialDelay).total_seconds() + \
                    datetime.timedelta(0, (numb-1)*interval).total_seconds()

        timings = np.linspace(startTiming, endTiming, numb)

        timingsStr = self.array_to_string(timings)

        return timingsStr
        

    def start_task(self,currentTime, pass_started, task, config: Config, logger,passtype):
        """
            Starts a pass or post-pass task as a background subprocess

            Parameters:
                self (Tasks): default class from the Python convention
                currentTime (float): Current timestamp at time of function call
                pass_started (bool): indicates whether the pass is ongoing (true) or not (false)
                task (object): a task object with its parameters
                config (class): a config class, representing the content of the config.json file
                logger (class): a class for logging
                passtype (string): a string describing what type of the pass is to be performed

            Returns:
                process (class) - a subprocess.Popen class, representing the parameters of the current subprocess
        """

        task_id = task["id"]
        task_path = task["file_path"]
        self.arguments = " "
        process = None

        if task_id not in self.tasks_done:
            for proc, task_ in self.tasks_in_progress:
                if task_id == task_["id"]: 
                    return

            logger.info("Preparing to start the task {"+str(task_id)+"}")

            if pass_started:
                #initial values for testing
                duration = config.configFull.general.pass_end_timestamp - config.configFull.general.pass_start_timestamp # duration of pass in seconds
                orbital_altitude = config.configFull.general.altitude # km
                first_image_time = currentTime + config.configFull.general.pre_pass_init # time of first image
                last_image_time = currentTime + config.configFull.general.pre_pass_init + duration # time of second image

                # start primary imaging operations if a primary pass is to be performed
                if passtype == "PRIMARY":
                    tau_capture_times = self.capture_timings(config.configFull.cameras.tau.imgs_per_pass,
                                                             orbital_altitude,
                                                             first_image_time,
                                                             last_image_time,
                                                             config.configFull.cameras.tau.finaltimeoffset)
                    basler_capture_times = self.capture_timings(config.configFull.cameras.basler.imgs_per_pass,
                                                                orbital_altitude,
                                                                first_image_time,
                                                                last_image_time,
                                                                config.configFull.cameras.basler.finaltimeoffset)

                    # extra --times argument: assigns capture start times
                    if task_id == 1:
                        self.arguments += "--times" + self.array_to_string(basler_capture_times)
                    if task_id == 2:
                        self.arguments += "--times" + self.array_to_string(tau_capture_times)
                elif passtype == "CALIBRATION":
                    tau_capture_times = self.capture_timings(config.configFull.cameras.tau.imgs_per_calibration,
                                                             orbital_altitude,
                                                             first_image_time,
                                                             last_image_time,
                                                             config.configFull.cameras.tau.finaltimeoffset)
                    # extra --times argument: assigns capture start times
                    if task_id == 10:
                        self.arguments += "--times" + self.array_to_string(tau_capture_times)
                else:
                    logger.info("unable to detect pass operations type")

            # add additional arguments
            self.arguments += self.task_argument_string(task_id, config)

            try:
                # Execute the process by a file path
                process = subprocess.Popen(("python3 " + task_path + self.arguments),
                            shell= True,
                            stdin= None,
                            stdout= None,
                            stderr= subprocess.STDOUT,
                            preexec_fn=os.setsid)
                
                logger.info("Process {id: "+str(task_id)+"} has started...")

                self.tasks_in_progress.append((process, task))
                
                logger.info("Tasks in progress:")
                for proc, task_ in self.tasks_in_progress:
                    logger.info(f"ID: {str(task_['id'])}, PID: {str(proc.pid)}")

            except (OSError, subprocess.CalledProcessError) as exception:
                logger.error("Subprocess error: {"+str(exception)+"}")
        
        return process

    def task_argument_string(self, task_id, config: Config):
        arguments = " "

        if task_id == 1:
            baslerProperties: BaslerProperties = config.configFull.cameras.basler.properties

            arguments += " --gain " + str(baslerProperties.gain.value)
            arguments += " --triggertype " + str(baslerProperties.trigger_type.value)
            arguments += " --exposuremode " + str(baslerProperties.exposure_mode.value)
            arguments += " --exposureauto " + str(baslerProperties.exposure_auto.value)
            arguments += " --exposuretime " + str(baslerProperties.exposure_time.value)
            arguments += " --black " + str(baslerProperties.black_level.value)
            arguments += " --white " + str(baslerProperties.white_balance.value)
            arguments += " --saturation " + str(baslerProperties.saturation.value)
            arguments += " --pixelformat " + str(baslerProperties.pixel_format.value)
        if task_id == 2:
            tauProperties: TauProperties = config.configFull.cameras.tau.properties

            arguments += " --gainmode " + str(tauProperties.gain_mode.value)
            arguments += " --agctype " + str(tauProperties.agc_type.value)
            arguments += " --contrast " + str(tauProperties.contrast.value)
            arguments += " --brightness " + str(tauProperties.brightness.value)

        return arguments