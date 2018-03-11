"""
The place for logging process

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-01"
__version__ = "0.1"

    Version:
        0.1 : implemented get logger from python logging

"""

import logging
import traceback
import sys


base_logger_name = "Toby"

'''
    Build logger objects for objects
    Input:
        name: the logger name
        log_level: the level of logging.X e.g. info/debug/error/critical/warning
    Output:
        The logger instance
        * the same instance should be gotten via logging.getLogger(name)
'''


def build_logger(name, in_log_level='info'):
    """
    Build logger objects for objects
    * Build once for each application
    
    :param name: the logger name
    :param in_log_level: the level of logging.X e.g. info/debug/error/critical/warning
    :return: The logger instance
    """
    global base_logger_name
    base_logger_name = name
    levels = {
        'info': logging.INFO, 'debug': logging.DEBUG, 'error': logging.ERROR,
        'critical': logging.CRITICAL, 'warning': logging.WARNING
    }
    logger = logging.getLogger(name)
    log_level = levels[in_log_level.lower()]
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def get_logger(name):
    """
    Get the logger instance 
    * will use sub logger from the base one
    
    :param name: The name of logger 
    :return: return the logger
    """
    return logging.getLogger(base_logger_name+'.'+name)


def trace_error(logger):
    """
    Capture & log the error

    :param logger:
    :return: Formatted error message
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    rtn = traceback.format_exception(exc_type, exc_value, exc_traceback)
    logger.error(rtn)
    return rtn
