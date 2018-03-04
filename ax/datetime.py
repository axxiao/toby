"""
The commonly used datetime functions

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-04"
__version__ = "0.1"

    Version:
        0.1 (04/03/2018 AX) : separated from tools

"""
import pytz
import os
from datetime import datetime
from time import time as cur_time
from dateutil import parser, relativedelta


default_date_format = "%Y-%m-%d"
default_datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

tz_utc = pytz.timezone('utc')
tz_local = pytz.timezone(os.getenv('TIMEZONE', 'Australia/Melbourne'))

"""
return the system time in seconds.microseconds
"""
current_sys_time = cur_time


"""
Parse datetime from string
e.g. 2018-1-3 18:20:33.234888 AEDT
"""
parse_datetime_string = parser.parse


def add_datetime(orig_datetime, units='seconds=1'):
    """
    Add delta to datetime
    :param orig_datetime: the base datetime/ date
    :param units: the units to be added, e.g. month=1,day=-2,hour=3,minute=-7
    :return: added result
    """
    k = dict()
    for u in units.split(","):
        x = u.split('=')
        p = x[0].lower()
        k[p if p[-1] == 's' else p+'s'] = int(x[1])
    return orig_datetime + relativedelta.relativedelta(**k)


def utc_now():
    """
    The UTC time
    :return: the utc datetime now
    """
    return datetime.utcnow()


def now(zone=tz_local):
    """
    Current local time

    Timezone is via system variable TIMEZONE
    :return: the current date time (datetime.datetime)
    """
    return datetime.now(tz=zone)


def format_date(dt, date_format=default_date_format):
    return dt.format(date_format)


def format_datetime(dt, date_format=default_datetime_format):
    return dt.format(date_format)


