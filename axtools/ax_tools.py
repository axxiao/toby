"""
The place for small tools

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-01"
__version__ = "0.1"

    Version:
        0.1 : implemented run_thread

"""

import threading
import traceback,sys

default_date_format = "%Y-%m-%d"
default_datetime_format = "%Y-%m-%d"


def run_thread(fun, *args, **kwargs):
    """
    Run function as background as thread
    
    :param fun: the function 
    :param args: position args
    :param kwargs: key word args
    :return: the thread instance
    """
    th = threading.Thread(target=fun, args=args, kwargs=kwargs)
    th.setDaemon(True)
    th.start()
    return th


def trace_error(logger):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))