''' @file logging.py

 @brief Defines the create_logger function.

 @section description_logger Description
 Defines the create_logger function for creating custom loggers for each process.
 - create_logger


 @section libraries_logger Libraries/Modules
 - python logging library


 @section todo_logger TODO
 - None.

 @section author_logger Author(s)
 - Created by Louis Timperley on 02/08/2021.
 - Modified by Vilius Stonkus on 02/08/2021.
'''

import logging

def create_logger(name, filepath):
    """
        Creates a custom logger object using the python logging library

            Parameters:
                name(string): The number of images required in the set
                filepath(string): The altitude of the spacecraft (km)

            Returns:
                logger (loggerobject): A custom logger object

    """
    # Create a custom logger
    logger = logging.getLogger(name)
    # Change root level to DEBUG
    logger.setLevel(logging.DEBUG)
    # Create handlers
    debug_handler = logging.FileHandler(filepath)  # warning handler
    debug_handler.setLevel(logging.DEBUG)
    # Create formatters and add it to handlers
    debug_format = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    debug_handler.setFormatter(debug_format)
    # Add handlers to the logger
    logger.addHandler(debug_handler)


    return logger


"""For creating a CSV file that will log all values for the device """
import csv


class log_it():
    """Log it class is used to log data to a csv file, is designed to be called anywhere.
    The class has varible Data which is the data that you want to log, if it is a 3D iter_log then use a iterable
    this will store all the data at once and uses less power and memory
    ALternativly use log_append which just stores a new line of data
    to create a log file use create_log() and create_log_iter() respectivly WILL NOT WORK IF FILE ALREADY EXISTS
    Iter cannot be used with 1D arrays
    Can change the heeading titels to what needed

    """

    def __init__(self, filename=None, Data=None, OG_data=None):  # init function for setting varibles
        self.filename = filename
        self.OG_data = OG_data
        self.Data = Data

    def log_append(self):

        # Checks to see if list is 1D
        #for i in self.Data:
            #if type(i) == list:
            #    raise Exception("List is 2D")
            #else:
            #    pass
        # Open the csv file and uses the csv enviroment to read data
        with open(self.filename, "r", newline="\n") as f:
            reader = csv.reader(f, delimiter=",")
            self.OG_data = list(reader)
            # If there is no data in file raise error
            if self.OG_data == []:
                raise Exception("No data found please delete file and use create_log")
            f.close()
        # set original data to original data and new data
        self.OG_data.append(self.Data)

        # write the data to the file
        with open(self.filename, "w", newline="\n") as f:
            writer = csv.writer(f)
            for i in self.OG_data:
                writer.writerow(i)
            f.close()

    def iter_log_append(self):  # Use with large sum of data
        """This will be used to bulk add data so if there is large amounts of data to add as log_append
           requires the data to be pulled from the file this will add the new data with the old data"""
        # Check that array is 2D
        try:
            self.Data[0][0] != None
        except:
            raise Exception("Please enter a use append for 1D arrays")
        # Open file
        with open(self.filename, "r", newline="\n") as f:
            reader = csv.reader(f, delimiter=",")
            self.OG_data = list(reader)
            # Check there is data already in file and if not raise error
            if self.OG_data == []:
                raise Exception("No data found please delete file and use create_log")
            f.close()

        # set old data to old data and new data
        for i in self.Data:
            self.OG_data.append(i)

        # write the data to the file
        with open(self.filename, "w", newline="\n") as f:
            writer = csv.writer(f)
            for i in self.OG_data:
                writer.writerow(i)
            f.close()

    def create_log(self):
        # Check that data is 1D
        for i in self.Data:
            if type(i) == list:
                raise Exception("List is 2D")

        # Open the file by also making sure the file doesnt already exist "x" does this as it means to create and
        # inbuilt error
        with open(self.filename, "x") as f:
            f.close()

        self.OG_data = [['Date', 'T_TEMP','T_TEMP_FLAG', 'B_TEMP','T_TEMP_FLAG', 'A_TEMP','T_TEMP_FLAG', 'CPU_TEMP','T_TEMP_FLAG','T_CUR','T_TEMP_FLAG','B_CUR','T_TEMP_FLAG','A_CUR','T_TEMP_FLAG']]
        self.OG_data.append(self.Data)
        # write the data to the file
        with open(self.filename, "w", newline="\n") as f:
            writer = csv.writer(f)
            for i in self.OG_data:
                writer.writerow(i)
            f.close()

    def create_log_iter(self):
        # Checks to make sure that the data is 2D
        try:
            self.Data[0][0] != None
        except:
            raise Exception("Please enter a use append for 1D arrays")
        # Open the file by also making sure the file doesnt already exist "x" does this as it means to create and
        # inbuilt error
        with open(self.filename, "x") as f:
            f.close()
        # Set the original data to the default headers
        self.OG_data = [['Date', 'T_TEMP','T_TEMP_FLAG', 'B_TEMP','T_TEMP_FLAG', 'A_TEMP','T_TEMP_FLAG', 'CPU_TEMP','T_TEMP_FLAG','T_CUR','T_TEMP_FLAG','B_CUR','T_TEMP_FLAG','A_CUR','T_TEMP_FLAG']]
        # Add new data to old data using a for loop
        for i in self.Data:
            self.OG_data.append(i)
        # write the data to the file
        with open(self.filename, "w", newline="\n") as f:
            writer = csv.writer(f)
            for i in self.OG_data:
                writer.writerow(i)
            f.close()
