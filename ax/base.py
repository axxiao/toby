"""
The common object functions
__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-04-22"
__version__ = "0.5"
"""
from .log import get_logger
from contextlib import contextmanager


@contextmanager
def get_context(resource_class, *args, **kwds):
    # Code to acquire resource, e.g.:
    resource = resource_class(*args, **kwds)
    try:
        yield resource
    finally:
        # release
        if hasattr(resource, 'disconnect'):
            resource.disconnect()
        elif hasattr(resource, 'close'):
            resource.close()


class Connector:
    """
        The common base class for all connectors
    """

    def __init__(self, host='tcp://127.0.0.1', port=11612, logger_name=None):
        """
        The common objects

        :param host: the host name 
        :param port: the port name
        :param logger_name: logger name
        """
        self.host = host
        self.port = port
        self.logger_name = logger_name
        self.logger = get_logger(logger_name)
