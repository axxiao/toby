import pytz
from datetime import datetime
from time import time as cur_time
from dateutil import parser, relativedelta


default_date_format = "%Y-%m-%d"
default_datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

tz_utc = pytz.timezone('utc')
current_sys_time = cur_time

"""
Parse datetime from string
e.g. 2018-1-3 18:20:33.234888 AEDT
"""
parse_from_string = parser.parse


def add_dateimte(orig_datetime, units='seconds=1'):
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
    pass
    #return arrow.get(dt).to(os.getenv('TIMEZONE', 'Australia/Melbourne')).datetime


def format_date(dt, date_format=default_date_format):
    return dt.format(date_format)


def format_datetime(dt, date_format=default_datetime_format):
    return dt.format(date_format)


