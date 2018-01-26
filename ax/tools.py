"""
The place for small tools

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-01"
__version__ = "0.1"

    Version:
        0.1 : implemented run_thread

"""

import os
import sys
import threading
import traceback
from datetime import datetime

import arrow
from requests import get

default_date_format = "%Y-%m-%d"
default_datetime_format = "%Y-%m-%dT%H:%M:%S.%f"


def get_ngrok_url(host='http://127.0.0.1:4040', tunnel_name='toby'):
    """
    Ngrok API
    :param host: 
    :param tunnel_name: 
    :return: the https address e.e.
    """
    r = None
    for url in get(host+'/api/tunnels').json()['tunnels']:
        if url['name'] == tunnel_name:
            r = url['public_url']
    return r


def get_utc_now():
    """
    The UTC time
    :return: the utc datetime now
    """
    return datetime.utcnow()


def get_local_now(dt=datetime.utcnow()):
    """
    Current local time
    
    Timezone is via system variable TIMEZONE
    :return: the current date time (datetime.datetime)
    """
    return arrow.get(dt).to(os.getenv('TIMEZONE', 'Australia/Melbourne')).datetime


def format_date(dt, date_format=default_date_format):
    return dt.format(date_format)


def format_datetime(dt, date_format=default_datetime_format):
    return dt.format(date_format)


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
    """
    Capture & log the error 
    
    :param logger: 
    :return: Formatted error message 
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    rtn = traceback.format_exception(exc_type, exc_value, exc_traceback)
    logger.error(rtn)
    return rtn


def search_part(orig_str, begin, end=None, strip=False):
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
        if not end:
            if len(patt) > 0:
                yield patt
        else:
            end_pos = patt.find(end)
            if end_pos > 0 or (strip == False and end_pos == 0):
                yield patt[:end_pos]


def get_public_ip():
    """
        Return the public ip of the requested machine

        Input: N/A

        Output: IP V4 string xxx.xxx.xxx.xxx
    """
    ip = get('https://api.ipify.org').text
    return ip
