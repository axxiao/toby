"""
The main class to handle all memory related operations, e.g. save object, fetch object

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-04"
__version__ = "0.2"

    Version:
        0.1 (02/07/2017 AX) : implemented basic definition, zmq
        0.2 (04/03/2018 AX) : changed from zmq to redis
        0.3 (25/08/2018 AX) : combined queue & cache together

"""
from ax.wrapper.redis import Cache, PubSub


class Info(Cache):
    """
        The common base class for queue
    """

    def __init__(self, host='127.0.0.1', port=12116, logger_name='Toby.Queue'):
        """
        The common objects

        :param host: the host name 
        :param port: the port name
        :param logger_name: logger name
        """
        Cache.__init__(self, logger_name=logger_name, host=host, port=port)
        self.queue = PubSub()



