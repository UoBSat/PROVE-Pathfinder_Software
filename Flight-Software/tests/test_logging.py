''' @file test_logging.py

@brief Defines test for the create_logger function.

@section description_test_logging Description
Defines the unit test for the create_logger function and checks its enabled logging levels and creates a test log
- test_create_logger


@section libraries_logger Libraries/Modules
- python pytest library
- python sys library
- python os library


@section todo_logger TODO
- None.

@section author_logger Author(s)
- Created by Louis Timperley on 12/08/2021.
'''

import pytest
import logging
import sys
import os
sys.path.append('/home/debian')
from shared.logging import create_logger

def test_create_logger(caplog):
    """
        Tests the creat_logger function that should creater a logger object with a specific name that loggs to a
        specific directory

        Parameters:
            caplog (fixture): a fixture provided by pytest to capture logs generated in a test

        Returns:
            void
    """

    logger = create_logger("test_create_logger", "testlog.log")
    caplog.set_level(logging.INFO)

    infoEnabled =  logger.isEnabledFor(20) # test that the logger is enabled for the info level
    assert infoEnabled is True

    warnEnabled = logger.isEnabledFor(30) # test that the logger is enabled for the warning level
    assert warnEnabled is True

    errEnabled = logger.isEnabledFor(40) # test that the logger is enabled for the error level
    assert errEnabled is True

    loggerlevel = logger.getEffectiveLevel() # test that the logger is of level debug

    assert loggerlevel == 10

    logger.info("testing logger") # create a log
    assert caplog.records[0].message == "testing logger"

    os.remove("testlog.log")