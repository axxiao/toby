"""
The queue by ZeroMQ
This is the connector which will be the core message queue within the same machine

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-05-27"
__version__ = "0.1"

    Version:
        0.1 : implemented zeroMQ publish/ subscribe device

"""
import zmq
from threading import Thread
from ax_tools import trace_error
from ax_queue import Q_Base_connector as Base_connector


class Q_Device(Thread, Base_connector):
    """
        The device which exchanges messages between pub/sub, router/dealer, push puller
        
        Input parameters:
            name : the name of device - default to Exchanger
            mode: the pair of in & out port, default to [zmq.SUB,zmq.PUB]
            port_in: in port number default to 12116
            port_out: output port number default to 1217
            port_mointor: monitor port, default to -1, if greater than 0, will open monitor port (PUB)
            logger: pass in logger otherwise will use print
        
        Sample code:
            ex=Q_device(name='Exchanger',mode=['sub','pub'],port_in=12116,port_out=12117,port_monitor=-1,logger=None)
            ex.setDaemon(True)
            ex.start()
    """

    def __init__(self, name='Exchanger', mode=['sub', 'pub'], port_in=12116, port_out=12117, port_monitor=-1,
                 logger=None):
        Thread.__init__(self)
        Base_connector.__init__(self, logger=logger)
        self.context = None
        self.monitor = None
        self.name = name
        self.port_in = port_in
        self.port_out = port_out
        self.port_monitor = port_monitor
        self.mode = mode
        self.mode_map = {'pub': zmq.PUB, 'sub': zmq.SUB,
                         'router': zmq.ROUTER, 'dealer': zmq.DEALER,
                         'psh': zmq.PUSH, 'pull': zmq.PULL
                         }
        self.frontend = None
        self.backend = None

    def run(self):
        # try:
        self.context = None
        self.frontend = None
        self.backend = None
        self.monitor = None
        try:
            self.context = zmq.Context()
            # Socket facing clients
            self.logger.debug('Got context')
            self.frontend = self.context.socket(self.mode_map[self.mode[0]])
            address = "tcp://*:" + str(self.port_in)
            self.logger.debug('Trying to bind In port at ' + address)
            self.frontend.bind(address)
            self.logger.debug('In port ' + self.mode_map[self.mode[0]] + ' is up at ' + address)

            # Socket facing services
            self.backend = self.context.socket(self.mode_map[self.mode[1]])
            self.logger.debug('Trying to bind Out port at ' + address)
            address = "tcp://*:" + str(self.port_out)
            self.backend.bind(address)
            self.logger.debug('Out port ' + self.mode_map[self.mode[1]] + ' is up at ' + address)

            if self.port_monitor > 0:
                self.monitor = self.context.socket(zmq.PUB)
                self.logger.debug('Trying to bind Monitor port at ' + address)
                address = "tcp://*:" + str(self.port_monitor)
                self.monitor.bind(address)
                self.logger.debug('Monitor port PUB is up at ' + address)

            self.logger.info(self.name + " is ONLINE")
            # zmq.device(zmq.FORWARDER, frontend, backend)
            zmq.proxy(self.frontend, self.backend, self.monitor)
        except:
            trace_error(self.logger)
        finally:
            #    pass
            self.logger.info(self.name + " is preparing to go offline")
            if self.frontend: self.frontend.close()
            if self.backend: self.backend.close()
            if self.backend: self.backend.close()
            if self.context: self.context.term()
            self.logger.info(self.name + " is OFFLINE")


class Q_Connector(Base_connector):
    """
    The base class for all connectors
    """

    def __init__(self, type, host='tcp://127.0.0.1', port=12116, mode='connect', logger_name='Q_Connector'):
        Base_connector(host=host, port=port, logger=logger_name)
        self.context = None
        self.socket = None
        self.type = type
        self.mode = mode
        self.connect()
        self.send = self.socket.send
        self.receive = self.socket.recv
        self.send_json = self.socket.send_json
        self.receive_json = self.socket.recv_json
        self.send_multipart = self.socket.send_multipart
        self.receive_multipart = self.socket.recv_multipart

    def pre_connect(self):
        raise TypeError('Function not been overwritten!!')
        pass

    def connect(self):
        self.pre_connect()
        self.context = zmq.Context()
        self.socket = self.context.socket(self.type)
        if self.mode == 'connect':
            addr = self.host + ":" + str(self.port)
            self.logger.debug('Connecting ' + addr)
            self.socket.connect(addr)
            self.logger.info('Connected')
        elif self.mode == 'bind':
            addr = self.host + ":" + str(self.port)
            self.logger.debug('Binding ' + addr)
            self.socket.bind(addr)
            self.logger.info('Binded')

    def disconnect(self):
        self.socket.close()


class Q_Pub(Q_Connector):
    def __init__(self, host='tcp://127.0.0.1', port=12116, logger_name='Q_pub'):
        Q_Connector(zmq.PUB, host=host, port=port, logger_name=logger_name)

    def pre_connect(self):
        pass


class Q_Sub(Q_Connector):
    def __init__(self, topics, host='tcp://127.0.0.1', port=12117, logger_name='Q_pub'):
        Q_Connector(zmq.SUB, host=host, port=port, logger_name=logger_name)
        self.topics = topics

    def pre_connect(self):
        pass
