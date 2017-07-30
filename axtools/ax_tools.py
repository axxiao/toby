"""
The place for small tools

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-01"
__version__ = "0.1"

    Version:
        0.1 : implemented run_thread

"""

import threading
import traceback, sys, re
from requests import get

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


def mysearch(orig_str, begin, end=None, strip=False):
    """
    The generator function to return all information that in between start/end key words

    Input:
        orig_str: the string to be searched
        begin: the keyword for begining (exclusive)
        end [Optional]: the keyword for the end (exclusive), if not defined, get all the info before next begin
        strip [Optional]: default to False, which will not strip info if empty

    Output:
        List of all result (yield)
    """
    first = orig_str.find(begin)
    for patt in orig_str[first:].split(begin):
        if strip:
            patt = patt.strip()
        if end == None:
            if len(patt) > 0:
                yield patt
        else:
            end_pos = patt.find(end)
            if end_pos > 0 or (strip == False and end_pos == 0):
                yield patt[:end_pos]





def get_pulic_ip():
    """
        Return the public ip of the requested machine

        Input: N/A

        Output: IP V4 string xxx.xxx.xxx.xxx
    """
    ip = get('https://api.ipify.org').text
    return ip
