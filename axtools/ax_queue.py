"""
The queue common adapter
This is the connector which will be the core message queue adapter

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-02"
__version__ = "0.1"

    Version:
        0.1 : implemented basic definition

"""
from .ax_tools import run_thread
from .ax_log import get_logger


class Q_Base_connector():
    """
        The common base class for all connectors
    """

    def __init__(self, host='tcp://127.0.0.1', port=12116, logger_name=None):
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

def start_queue_server(server_type, server_host="127.0.0.1", server_ports={"in_port":12116,"out_port":12117}):


    pass


def get_queue_pub():
    pass


def get_queue_sub():
    pass