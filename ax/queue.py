"""
The queue common adapter
This is the connector which will be the core message queue adapter

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-04"
__version__ = "0.2"

    Version:
        0.1 (02/07/2017 AX) : implemented basic definition, zmq
        0.2 (04/03/2018 AX) : changed from zmq to redis

"""
from .redis import PubSub


class Queue(PubSub):
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
        PubSub.__init__(self, logger_name=logger_name, host=host, port=port)

    def pubsub(self, to_topic, req_obj, from_topic, timeout=-1):
        """

        :param to_topic: the queue which req_obj should be sent to
        :param req_obj: the request object
        :param from_topic: the queue should listen to result
        :param timeout: timeout of listening (-1 is block forever)
        :return: returned object
        """
        self.pub(to_topic, req_obj)
        return self.sub(from_topic, timeout=timeout, wildcard=False)


