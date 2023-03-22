import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.GPIO as GPIO
import time
import numpy
import sys
from os.path import exists
from datetime import datetime

sys.path.append('/home/debian')
from shared.logging import create_logger
from shared.logging import log_it
from shared.config import Config


def log_sensor(sensorName, pinID, thresholds: list, logger):
    """
        Writes the current value of a specified sensor and logs it with a level according to the config thresholds

        Parameters:
            sensorName (string) - Name of sensor to use when writing the log
            pinID (string) - ID of pin to read sensor signal from
            thresholds (list) - list of logger level thresholds to apply to the sensor reading: thresholds[0] is the
            warning threshold, thresholds[1] is the error threshold
            logger (object): Object containing information on how to write logs

        Returns:
            sensorValue (float) - sensor reading, NaN if no reading sucessfully read
            pinValue (float) - raw pin reading, NaN if no reading sucessfully read
            logflag (float) - number related to log level following standard practise: 20  is info level, 30  is warning
            level, 40  is error level, 0 if no reading sucessfully read

    """
    try:
        # read in pin value
        pinValue = ADC.read(pinID)
        # Now convert pin value to physical reading
        if sensorName == "T_TEMP" or sensorName == "B_TEMP" or sensorName == "A_TEMP" or sensorName == "CPU_TEMP":
            sensorValue = temp_conversion(pinValue)
        elif sensorName == "T_CUR" or sensorName == "B_CUR" or sensorName == "A_CUR":
            sensorValue = curr_conversion(pinValue)
        else:
            logger.error(f" sensor {sensorName} has no conversion to physical reading implemented")

        # log the value
        if pinValue < thresholds[0]:
            logflag = 20  # info level
        elif pinValue >= thresholds[0] and pinValue < thresholds[1]:
            logger.warning(f"{sensorName} = {sensorValue}")
            logflag = 30  # warning level
        else:
            logger.error(f"{sensorName} = {sensorValue}")
            logflag = 40  # error level

        return [sensorValue, pinValue, logflag]
    except Exception as e:
        logger.error("Unable to read sensor data from " + str(sensorName) + f": {e}")
        return [float('NaN'), float('NaN'), 0]


def mitigation_actions(t_TEMP, b_TEMP, a_TEMP, cpu_TEMP, t_CUR, b_CUR, a_CUR, config: Config, logger):
    """
        If any sensor readings are above error thresholds, take some corrective action, generally enter safe mode
        Parameters:
            t_TEMP (list) : tau temperature and related data
            b_TEMP (list) : baslertemperature and related data
            a_TEMP (list) : tau lens temperature and related data
            cpu_TEMP (list) : cpu temperature and related data
            t_CUR (list) : tau current and related data
            b_CUR (list) : basler current and related data
            a_CUR  (list) : unassigned current and related data
            config (object): Object containing scheduler configuration
            logger (object): Object containing information on how to write logs

        Returns
            void
    """
    # check latch up protector flag pins
    if GPIO.input("") == 'HIGH' or GPIO.input("") == 'HIGH' or GPIO.input("") == 'HIGH':
        logger.warning("latchup proector has triggered")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    # now check other sensor readings
    if t_TEMP[2] > config.configFull.sensors.T_TEMP.error_threshold:
        logger.warning("identified error level tau temperature")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    if b_TEMP[2] > config.configFull.sensors.B_TEMP.error_threshold:
        logger.warning("identified error level basler temperature")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    if a_TEMP[2] > config.configFull.sensors.A_TEMP.error_threshold:
        logger.warning("identified error level _ temperature")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    if cpu_TEMP[2] > config.configFull.sensors.CPU_TEMP.error_threshold:
        logger.warning("identified error level CPU temperature")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    if t_CUR[2] > config.configFull.sensors.T_CUR.error_threshold:
        logger.warning("identified error level tau current")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    if b_CUR[2] > config.configFull.sensors.B_CUR.error_threshold:
        logger.warning("identified error level basler current")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    if a_CUR[2] > config.configFull.sensors.A_CUR.error_threshold:
        logger.warning("identified error level _ current")
        logger.warning("ENTERING SAFE MODE")
        config.enter_safe_mode()
    return

def temp_conversion(pinvalue):
    """
        converts the raw pin reading to a physical temp sensor value

        Parameters:
            pinvalue (string) - raw pin value from sensor

        Returns:
            sensorValue (float) - temp sensor reading, NaN if no reading successfully read

    """
    tempsensorvoltage = pinvalue * 1.8

    resistance25c = 100000
    T1 = 273 + 25  # test temperature from spec
    controlresistor = 10000
    betaValue = 3976

    #sensorvalue = betaValue * T1 / (betaValue - T1 * numpy.log(resistance25c) - numpy.log(
    #    (1.8 * controlresistor / tempsensorvoltage) - controlresistor))
    sensorvalue = (betaValue*T1) / (T1*numpy.log(((1.8*controlresistor)/(tempsensorvoltage))-controlresistor) - T1*numpy.log(resistance25c) + betaValue)
    return sensorvalue


def curr_conversion(pinvalue):
    """
        converts the raw pin reading to a physical current sensor value

        Parameters:
            pinvalue (string) - raw pin value from sensor

        Returns:
            sensorValue (float) - current sensor reading, NaN if no reading successfully read

    """
    currsensorvoltage = pinvalue * 1.8

    zeroamps = 0.493
    ampscale = 0.4

    sensorvalue = currsensorvoltage * ampscale + zeroamps
    return sensorvalue


def main():
    """
    Main code for the Telemetry service.
    Steps:
        setup logger and ADC
        while loop
            log sensor readings
            take corrective action if nessecary
    """

    logger = create_logger("TelemetryService", "/media/SD1/logs.log")  # Create logger

    # check to see if telemetry csv file already exists
    if exists("/media/SD1/telemetry.csv") == False:
        with open("/media/SD1/telemetry.csv", "x") as f:
            f.write(
                "Date,T_TEMP,T_TEMP_FLAG, B_TEMP,T_TEMP_FLAG, A_TEMP,T_TEMP_FLAG, CPU_TEMP,T_TEMP_FLAG,T_CUR,T_TEMP_FLAG,B_CUR,T_TEMP_FLAG,A_CUR,T_TEMP_FLAG")
            f.close()

    ADC.setup()  # setup the ADC
    # setup latchup proector flag pins
    GPIO.setup("", GPIO.IN)
    GPIO.setup("", GPIO.IN)
    GPIO.setup("", GPIO.IN)

    config = Config()
    config.set_telemetry_cadence(60)  # set initial telemetry cadence on start up

    for i in range(5):  # will replace with while loop
        config = Config()

        # log sensor readings
        T_TEMP = log_sensor("T_TEMP", "P9_33", [config.configFull.sensors.T_TEMP.warn_threshold, config.configFull.sensors.T_TEMP.error_threshold], logger)
        B_TEMP = log_sensor("B_TEMP", "P9_36", [config.configFull.sensors.B_TEMP.warn_threshold, config.configFull.sensors.B_TEMP.error_threshold], logger)
        A_TEMP = log_sensor("A_TEMP", "P9_35", [config.configFull.sensors.A_TEMP.warn_threshold, config.configFull.sensors.A_TEMP.error_threshold], logger)
        CPU_TEMP = log_sensor("CPU_TEMP", "P9_38", [config.configFull.sensors.CPU_TEMP.warn_threshold, config.configFull.sensors.CPU_TEMP.error_threshold], logger)
        T_CUR = log_sensor("T_CUR", "P9_39", [config.configFull.sensors.T_CUR.warn_threshold, config.configFull.sensors.T_CUR.error_threshold], logger)
        B_CUR = log_sensor("B_CUR", "P9_40", [config.configFull.sensors.B_CUR.warn_threshold, config.configFull.sensors.B_CUR.error_threshold], logger)
        A_CUR = log_sensor("A_CUR", "P9_37", [config.configFull.sensors.A_CUR.warn_threshold, config.configFull.sensors.A_CUR.error_threshold], logger)

        telemetrydata = [datetime.now(), T_TEMP[0], T_TEMP[2], B_TEMP[0], B_TEMP[2], A_TEMP[0], A_TEMP[2], CPU_TEMP[0],
                         CPU_TEMP[2], T_CUR[0], T_CUR[2], B_CUR[0], B_CUR[2], A_CUR[0], A_CUR[2]]
        telemetrylogger = log_it(filename="/media/SD1/telemetry.csv", Data=telemetrydata).log_append()

        # perform corrective action if nessecary
        mitigation_actions(T_TEMP, B_TEMP, A_TEMP, CPU_TEMP, T_CUR, B_CUR, A_CUR,config,logger)

        # wait till next collection time
        if config.configFull.sensors.collection_cadence == 0:
            logger.warning("Telemetry collection stopped")
            return
        else:
            time.sleep(config.configFull.sensors.collection_cadence)


if __name__ == "__main__":
    # Main
    main()
