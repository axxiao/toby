"""
The place for common used functions

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-03"
__version__ = "0.2"

    Version:
        0.1 (1/7/2017): implemented run_thread, run_thread, search_paragraph
        0.2 (3/3/2018): moved date related function to datetime, added retry

Functions List:

    get_ngrok_url - return ngrok information
    get_public_ip -  return current machine's public ip
    retry - [decorator] to try to run function x time
    search_paragraph - [generator] return paragraph between start/end keywords

"""
from functools import wraps
from .exception import MaxRetryReached
from .log import trace_error
import threading
import time
from requests import get


def retry(max_retry_times, logger=None, retry_interval=1.0, pass_retry_param_name=None):
    """
    Retry the function for certain, if still fail, raise MaxRetryReached Exception
    :param max_retry_times: how many times of retry
    :param [optional] logger: the logger to catch exceptions
    :param [optional] retry_interval: how many seconds to sleep before next retry
    :param [optional] pass_retry_param_name: the parameter name to pass into function
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cnt = 0
            while cnt < max_retry_times:
                cnt += 1
                try:
                    if pass_retry_param_name:
                        kwargs[pass_retry_param_name] = cnt
                    return func(*args, **kwargs)
                except:
                    if logger:
                        trace_error(logger)
                        logger.warning('Retry ' + func.__name__ + ' ' + str(cnt) + ' time(s)')
                        # print(cnt)
                    if cnt >= max_retry_times:
                        # Reach max Retry
                        if logger:
                            logger.error('Retry ' + func.__name__ + str(cnt) + ' reached max times')
                        raise MaxRetryReached(func.__name__ , cnt)
                    time.sleep(retry_interval)
        return wrapper
    return decorator


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


def run_thread(fun, *args, **kwargs):
    """
    Run function as background as thread
    
    :param fun: the function
    :param set_daemon_flg :[optional, default to false] if run thread in daemon mode
    :param args: position args
    :param kwargs: key word args
    :return: the thread instance
    """
    th = threading.Thread(target=fun, args=args, kwargs=kwargs)
    th.setDaemon(kwargs.get('set_daemon_flg',False))
    th.start()
    return th


def search_paragraph(orig_str, begin, end=None, strip=False):
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
