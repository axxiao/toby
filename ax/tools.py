"""
The place for common used functions

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-03"
__version__ = "0.2"

    Version:
        0.1 (1/7/2017): implemented run_thread, run_thread, search_paragraph
        0.2 (3/3/2018): moved date related function to datetime, added retry
        0.3 (25/4/2019): encrypt/ decrypt

Functions List:

    get_ngrok_url - return ngrok information
    get_public_ip -  return current machine's public ip
    retry - [decorator] to try to run function x time
    search_paragraph - [generator] return paragraph between start/end keywords

"""
from functools import wraps
from .exception import MaxRetryReached
from .log import trace_error
import ax.datetime as ax_datetime
import threading
import time
from requests import get
import inspect
import sys
import importlib
import uuid
import os
from cryptography.fernet import Fernet


# the fernet for encrypt/ decrypt
_fernet = Fernet(os.getenv('TOBY_ENCRYPT_KEY') or Fernet.generate_key().decode()).encode()


def encrypt(value):
    """
    Encrypt the input value
    :param value: input value
    :return: encrypted output
    """
    return _fernet.encrypt(value.encode() if type(value) != bytes else value)


def decrypt(value, output_decode_flag=True):
    """
    Decrypt
    :param value: the encrypted value
    :param output_decode_flag: default to True; the flag of if to decode output
    :return: the decrypted output
    """
    o = _fernet.decrypt(value)
    return o.decode() if output_decode_flag else o


def get_uuid():
    return uuid.uuid4().hex


def list_functions(module):
    """
    List top-level function name & function
    :param module: the module
    :return: dict of all functions
    """
    return dict(inspect.getmembers(module, inspect.isfunction))


def load_standard_functions():
    """
    Commonly used functions for safe eval
    :return:
    """
    funcs = {'len': len, 'filter': filter}
    funcs = {**list_functions(ax_datetime), **funcs}
    return funcs


standard_functions = load_standard_functions()


def safe_eval(expression, variables={}, standard_functions=standard_functions):
    """
    Safe eval, only allow give functions/ expression
    :param expression: the expression for eval
    :param variables: all variables to be used in the eval
    :param standard_functions: list of standard functions, default to common functions
    :return: expressioneval result
    """
    params = {**variables, **standard_functions}
    params['__builtins__'] = {}
    return eval(expression, params)


def load_module(module, logger=None, force_reload=True):
    """
    Load/ Import module
    :param module: Module full name e.g. ax.datetime
    :param logger: [optional] for logging info
    :param force_reload: [Default to True] flag to control if reload existing module
    :return: the module
    """
    if module in sys.modules:
        if force_reload:
            if logger:
                logger.info('Existing module, reloading ' + module)
            return importlib.reload(sys.modules[module])
        else:
            if logger:
                logger.info('Use existing module' + module)
            return sys.modules[module]
    else:
        logger.info('New module, loading ' + module)
    return importlib.import_module(module)


def load_function(module, func, logger=None, force_reload=True):
    """
    Load/ Import function
    :param module: Module full name e.g. ax.datetime
    :param func: the function of the module
    :param logger: [optional] for logging info
    :param force_reload: [Default to True] flag to control if reload existing module
    :return: the function
    """
    mod = load_module(module, logger=logger, force_reload=force_reload)
    if logger:
        logger.info('Getting function '+func)
    return mod.__dict__[func]


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
                        raise MaxRetryReached(func.__name__, cnt)
                    time.sleep(retry_interval)
        return wrapper
    return decorator


def run_thread(fun, *args, **kwargs):
    """
    Run function as background as thread
    
    :param fun: the function
    :param args: position args
    :param kwargs: key word args
        set_daemon_flg :[optional, default to false] if run thread in daemon mode
    :return: the thread instance
    """
    th = threading.Thread(target=fun, args=args, kwargs=kwargs)
    th.setDaemon(kwargs.get('set_daemon_flg', False))
    th.start()
    return th


def search_paragraph(orig_str, begin, end=None, strip=False):
    """
    The generator function to return all information that in between start/end key words

    Input:
        orig_str: the string to be searched
        begin: the keyword for beginning (exclusive)
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
