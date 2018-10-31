"""
The main class to handle all connection related classes, 
e.g. Cache, DB

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-11-03"
__version__ = "0.1"

    Version:
        0.1 (02/07/2017 AX) : implemented basic definition, zmq
        0.2 (04/03/2018 AX) : changed from zmq to redis
        0.3 (25/08/2018 AX) : combined queue & cache together
        

"""
from ax.wrapper.redis import Cache, Queue
from ax.common import Connector as Base_Connector


class Connector(Base_Connector):
    """
        The common base class for queue
    """

    def __init__(self, host='127.0.0.1', port=6379, logger_name='Toby.Connector'):
        """
        The common objects

        :param host: the host name 
        :param port: the port name
        :param logger_name: logger name
        """
        Base_Connector.__init__(self, host=host, port=port, logger_name=logger_name)
        self.connections = dict()
        self.connect()
        
    def connect(self):
        cache = Cache(logger_name=self.logger_name, host=self.host, port=self.port)
        self.add('cache', cache)
        self.add('queue', Queue(logger_name=self.logger_name, host=self.host, port=self.port,
                                redis_instance=cache.get_instance()))
    
    
    def has_connection(self, name):
        """
        Check if connection is in this connector
        :param name: the neame of connection
        :return: True if has the connection else False
        """
        return name in selff.__dict__
        
    
    def add(self, name, conn):
        """
        Add new connection as attribute into connector
        """
        # self.connections[name]=conn
        if isinstance(conn,Base_Connector):
            setattr(self, name, conn)
        else:
            raise TypeError('Parameter conn expect instance/ child of ax.common.Connector')

