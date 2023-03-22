''' @file config.py

@brief Defines the base class and functions related to the configuration of the scheduler service.

@section description_tasks Description
Defines the class and functions for controlling various parameters relating to the operation of the scheduler and pass
operations. The config.json file is used to store this information
- Config (base class)
- get_config
- get_pass_duration
- write_timestamps
- recentpasstimestamp


@section libraries_logger Libraries/Modules
- python json library


@section todo_logger TODO
- None.

@section author_logger Author(s)
- Created by Vilius Stonkus on 02/08/2021.
- Modified by Louis Timperley on 02/08/2021.
'''

from email.policy import default
import json

class CameraProperty:
    """ 
    Describes the structure of a camera porperty
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, value, default):
        """
            Initialises the CameraProperty class, defines the variables

            Parameters:
                self (CameraProperty) - default class from the Python convention
                default (string/float/int) - default property value
                value (string/float/int) - pre-set camera property value

            Returns:
                void
        """

        self.value = value
        self.default = default

    @staticmethod
    def create_from_json(data):
        return CameraProperty(**data)

class BaslerProperties:
    """ 
    Describes the structure of Basler properties
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, gain, trigger_type, exposure_mode, exposure_auto, exposure_time, black_level, white_balance, pixel_format, saturation):
        """
            Initialises the BaslerProperties class, defines the variables

            Parameters:
                self (BaslerProperties) - default class from the Python convention
                gain (CameraProperty) - basler gain
                trigger_type (CameraProperty) - basler trigger type
                exposure_mode (CameraProperty) - basler exposure mode
                exposure_auto (CameraProperty) - basler exposure auto mode
                exposure_time (CameraProperty) - basler exposure time
                black_level (CameraProperty) - basler black level
                white_balance (CameraProperty) - basler white balance
                pixel_format (CameraProperty) - basler pixel format
                saturation (CameraProperty) - basler saturation

            Returns:
                void
        """

        self.gain = CameraProperty.create_from_json(gain)
        self.trigger_type = CameraProperty.create_from_json(trigger_type)
        self.exposure_mode = CameraProperty.create_from_json(exposure_mode)
        self.exposure_auto = CameraProperty.create_from_json(exposure_auto)
        self.exposure_time = CameraProperty.create_from_json(exposure_time)
        self.black_level = CameraProperty.create_from_json(black_level)
        self.white_balance = CameraProperty.create_from_json(white_balance)
        self.pixel_format = CameraProperty.create_from_json(pixel_format)
        self.saturation = CameraProperty.create_from_json(saturation)

    @staticmethod
    def create_from_json(data):
        return BaslerProperties(**data)

class TauProperties:
    """ 
    Describes the structure of Tau properties
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, gain_mode, agc_type, contrast, brightness):
        """
            Initialises the TauProperties class, defines the variables

            Parameters:
                self (TauProperties) - default class from the Python convention
                gain_mode (CameraProperty) - tau gain mode
                agc_type (CameraProperty) - tau AGC algorithm type
                contrast (CameraProperty) - contrast value used by once-bright, auto-bright, and manual AGC algorithms
                brightness (CameraProperty) -  brightness value used by the manual and auto-bright AGC algorithms

            Returns:
                void
        """

        self.gain_mode = CameraProperty.create_from_json(gain_mode)
        self.agc_type = CameraProperty.create_from_json(agc_type)
        self.contrast = CameraProperty.create_from_json(contrast)
        self.brightness = CameraProperty.create_from_json(brightness)

    @staticmethod
    def create_from_json(data):
        return TauProperties(**data)

class TemperatureSensor:
    """ 
    Describes the structure of a temperature sensor
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, warn_threshold, error_threshold):
        """
            Initialises the TemperatureSensor class, defines the variables

            Parameters:
                self (TemperatureSensor) - default class from the Python convention
                warn_threshold (int) - temperature sensor threshold level that raises a warning
                error_threshold (int) - temperature sensor threshold level that raises an error

            Returns:
                void
        """

        self.warn_threshold = warn_threshold
        self.error_threshold = error_threshold

    @staticmethod
    def create_from_json(data):
        return TemperatureSensor(**data)

class CamerasStruct:
    """ 
    Cameras structure class describing the structure of a JSON property 'cameras'
    ...
    """

    def __init__(self, basler, tau):
        """
            Initialises the CamerasStruct class, defines the cameras struct variables

            Parameters:
                self (CamerasStruct) - default class from the Python convention
                basler (BaslerConfig) - basler camera config class with all the parameters
                tau (TauConfig) - tau camera config class with all the parameters

            Returns:
                void
        """

        self.basler = BaslerConfig.create_from_json(basler)
        self.tau = TauConfig.create_from_json(tau)

class ConfigStruct:
    """ 
    Config struct class describing the structure of the overall JSON config
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class
    """

    def __init__(self, general, cameras, sensors):
        """
            Initialises the ConfigStruct class, defines the config variables

            Parameters:
                self (ConfigStruct) - default class from the Python convention
                general (GeneralConfig) - general config parameters from the JSON file
                cameras (CamerasStruct) - cameras config and their parameters from the JSON file
                sensors (SensorsConfig) - sensors config parameters from the JSON file

            Returns:
                void
        """

        self.general = GeneralConfig.create_from_json(general)
        self.cameras = CamerasStruct(cameras["basler"], cameras["tau"])
        self.sensors = SensorsConfig.create_from_json(sensors)

    @staticmethod
    def create_from_json(data):
        return ConfigStruct(**data)

class GeneralConfig:
    """ 
    General configurations class
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, next_pass_type, safe_mode, pass_start_timestamp, pass_end_timestamp, pre_pass_init, post_pass_timeout, altitude, pass_completion_time):
        """
            Initialises the GeneralConfig class, defines the general config variables

            Parameters:
                self (GeneralConfig) - default class from the Python convention
                next_pass_type (string) - string describing what type the next pass is, e.g. PRIMARY
                safe_mode (boolean) - flag describing whether or not the system is in safe mode, if so no tasks will be started
                pass_start_timestamp (float) - timestamp of start of pass
                pass_end_timestamp (float) - timestamp of end of pass
                pre_pass_init (float) - initialisation time before pass start
                post_pass_timeout (float) - time to wait after pass until post pass task time out
                altitude (float) - altitude of spacecraft at start time of pass in km
                pass_completion_time (float) - time at which all pass related operations are to be halted

            Returns:
                void
        """

        self.next_pass_type = next_pass_type
        self.safe_mode = safe_mode
        self.pass_start_timestamp = pass_start_timestamp
        self.pass_end_timestamp = pass_end_timestamp
        self.pre_pass_init = pre_pass_init
        self.post_pass_timeout = post_pass_timeout
        self.altitude = altitude
        self.pass_completion_time = pass_completion_time

    @staticmethod
    def create_from_json(data):
        return GeneralConfig(**data)

class BaslerConfig:
    """ 
    Basler configurations class
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, imgs_per_pass, finaltimeoffset, properties):
        """
            Initialises the BaslerConfig class, defines the basler config variables

            Parameters:
                self (BaslerConfig) - default class from the Python convention
                imgs_per_pass (int) - number of basler images to be taken
                finaltimeoffset (float) - time offset for final basler image
                properties (BaslerProperties) - basler configuration properties

            Returns:
                void
        """

        self.imgs_per_pass = imgs_per_pass
        self.finaltimeoffset = finaltimeoffset
        self.properties = BaslerProperties.create_from_json(properties)

    @staticmethod
    def create_from_json(data):
        return BaslerConfig(**data)

class TauConfig:
    """ 
    Tau configurations class
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, imgs_per_pass, imgs_per_calibration, finaltimeoffset, properties):
        """
            Initialises the TauConfig class, defines the tau config variables

            Parameters:
                self (TauConfig) - default class from the Python convention
                imgs_per_pass (int) - number of tau images to be taken
                imgs_per_calibration (int) - number of tau images to be taken per calibration
                finaltimeoffset (float) - time offset for final tau image
                properties (TauProperties) - tau configuration properties

            Returns:
                void
        """

        self.imgs_per_pass = imgs_per_pass
        self.imgs_per_calibration = imgs_per_calibration
        self.finaltimeoffset = finaltimeoffset
        self.properties = TauProperties.create_from_json(properties)

    @staticmethod
    def create_from_json(data):
        return TauConfig(**data)

class SensorsConfig:
    """ 
    Sensor configurations class
    ...

    Methods
    -------
    create_from_json(): 
        Converts a json dictionary to a class

    """

    def __init__(self, collection_cadence, T_TEMP, B_TEMP, A_TEMP, CPU_TEMP, T_CUR, B_CUR, A_CUR):
        """
            Initialises the SensorsConfig class, defines the sensors config variables

            Parameters:
                self (SensorsConfig) - default class from the Python convention
                collection_cadence (int) - telemetry cadence for the sensor data
                T_TEMP (TemperatureSensor) - T_TEMP
                B_TEMP (TemperatureSensor) - B_TEMP
                A_TEMP (TemperatureSensor) - A_TEMP
                CPU_TEMP (TemperatureSensor) - CPU_TEMP
                T_CUR (TemperatureSensor) - T_CUR
                B_CUR (TemperatureSensor) - B_CUR
                A_CUR (TemperatureSensor) - A_CUR

            Returns:
                void
        """

        self.collection_cadence = collection_cadence
        self.T_TEMP = TemperatureSensor.create_from_json(T_TEMP)
        self.B_TEMP = TemperatureSensor.create_from_json(B_TEMP)
        self.A_TEMP = TemperatureSensor.create_from_json(A_TEMP)
        self.CPU_TEMP = TemperatureSensor.create_from_json(CPU_TEMP)
        self.T_CUR = TemperatureSensor.create_from_json(T_CUR)
        self.B_CUR = TemperatureSensor.create_from_json(B_CUR)
        self.A_CUR = TemperatureSensor.create_from_json(A_CUR)

    @staticmethod
    def create_from_json(data):
        return SensorsConfig(**data)


class Config:
    """ 
    The Config base class

    Class for configuring the scheduler service and pass operations
    ...

    Methods
    -------
    get_config():
        Reads the config.json file and returns its content in a json object
    write_config():
        Writes the config.json file with the new content
    get_pass_duration():
        Returns a pass duration
    write_timestamps():
        Rewrites the config.json with new pass start and end timestamps
    recentpasstimestamp():
        Returns the most recent start pass timestamp
    set_telemetry_cadence():
        Sets the telemetry cadence for the sensor data
    reset():
        Resets/Updates the config
    set_operation_type():
        Sets the pass type

    """

    def __init__(self):
        """
            Initialises the Config class, reads the config.json file and stores its content; defines the config variables

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                void
        """

        self.configFull = self.get_config()
    
    def get_config(self):
        """
            Reads the config.json file and returns its content as an object

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                data_obj (ConfigStruct) - JSON config converted into a ConfigStruct class
        """

        f = open("/home/debian/Scheduler/config.json", "r")
        data_json = json.load(f)  
        data_obj = ConfigStruct.create_from_json(data_json)
        f.close()

        return data_obj

    def write_config(self, config: ConfigStruct):
        """
            Writes the config.json file with the new content

            Parameters:
                self (Config) - default class from the Python convention
                config (ConfigStruct) - new config object

            Returns:
                void
        """

        f = open("/home/debian/Scheduler/config.json", "w")
        f.write(json.dumps(config, default=lambda o: o.__dict__, indent=4))
        f.close()

        # reinitialize the class to update the config to the latest
        self.reset()
    
    def get_pass_duration(self):
        """
            Returns a pass duration

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                duration (int) - the duration of the pass
        """

        duration = self.configFull.general.pass_end_timestamp - self.configFull.general.pass_start_timestamp

        return duration

    def write_timestamps(self, startTime, finishTime):
        """
            Rewrites the config.json with safe mode flag set to true

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                void
        """

        self.configFull.general.pass_start_timestamp = startTime
        self.configFull.general.pass_end_timestamp = finishTime

        self.write_config(self.configFull)

    def enter_safe_mode(self):
        """
            Rewrites the config.json with new safe mode flag

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                void
        """

        self.configFull.general.safe_mode = True

        self.write_config(self.configFull)

    def exit_safe_mode(self):
        """
            Rewrites the config.json with new safe mode flag

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                void
        """

        self.configFull.general.safe_mode = False

        self.write_config(self.configFull)

    def recentpasstimestamp(self):
        """
            Returns the most recent start pass timestamp

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                timestamp (string) - a start pass timestamp
        """

        timestamp = str(self.configFull.general.pass_start_timestamp)

        return timestamp

    def set_telemetry_cadence(self, cadence):
        """
            Sets the telemetry cadence for the sensor data

            Parameters:
                self (Config) - default class from the Python convention
                cadence (int) - cadence

            Returns:
                void
        """

        self.configFull.sensors.collection_cadence = cadence

        self.write_config(self.configFull)

    def reset(self):
        """
            Resets/Updates the config

            Parameters:
                self (Config) - default class from the Python convention

            Returns:
                void
        """

        self.__init__()


    def set_operation_type(self, optype):
        """
            Sets the pass type

            Parameters:
                self (Config) - default class from the Python convention
                optype (string) - operation type (e.g. PRIMARY)

            Returns:
                void
        """

        self.configFull.general.next_pass_type = optype

        self.write_config(self.configFull)



