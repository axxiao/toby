"""
The queue by ZeroMQ
This is the connector which will be the core message queue within the same machine

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-05-27"
__version__ = "0.1"

    Version:
        0.1 : implemented zeroMQ publish/ subscribe device

"""
from threading import Thread

import zmq

from .queue import QueueBaseConnector as Base_connector
from .tools import trace_error


class QueueDevice(Thread, Base_connector):
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
                 logger_name=None):
        Thread.__init__(self)
        Base_connector.__init__(self, logger_name=logger_name)
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
            self.logger.debug('In port ' + str(self.port_in) + ' is up at ' + address)

            # Socket facing services
            self.backend = self.context.socket(self.mode_map[self.mode[1]])
            self.logger.debug('Trying to bind Out port at ' + address)
            address = "tcp://*:" + str(self.port_out)
            self.backend.bind(address)
            self.logger.debug('Out port ' + str(self.port_out) + ' is up at ' + address)

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


class QueueConnector(Base_connector):
    """
    The base class for all connectors
    """

    def __init__(self, type, host='tcp://127.0.0.1', port=12116, mode='connect', logger_name='Q_Connector'):
        Base_connector.__init__(self, host=host, port=port, logger_name=logger_name)
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


class QueuePub(QueueConnector):
    def __init__(self, host='tcp://127.0.0.1', port=12116, logger_name='Q_pub', code='utf-8'):
        QueueConnector.__init__(self, zmq.PUB, host=host, port=port, logger_name=logger_name)
        self.code = code

    def pre_connect(self):
        pass

    def pub(self, topic, in_msg):
        if type(in_msg).__name__ == 'dict':
            msg = json.dumps(in_msg)
        else:
            msg = in_msg
        self.send_multipart([topic.encode(self.code), msg.encode(self.code)])
        self.logger.debug(' Published to [' + topic + ']: ' + str(msg))


class QueueSub(QueueConnector):
    def __init__(self, topics, host='tcp://127.0.0.1', port=12117, logger_name='Q_pub', timeout=-1, code='utf-8'):
        QueueConnector.__init__(self, zmq.SUB, host=host, port=port, logger_name=logger_name)
        self.topics = topics
        self.code = code
        self.timeout = timeout
        self.set_timeout(timeout)
        self.topics = []
        self.topics = self.sub_topics(topics)
        self.logger.info('Subscribed:' + str(self.topics))
        self.last_topic = None

    def pre_connect(self):
        pass

    def set_timeout(self, timeout):
        self.timeout = timeout
        if self.timeout > 0:
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)

    def sub_topics(self, topics=None, cleanup=True):
        """
        :param topics: [Default to None] if to subscribe different topics
        :param cleanup:[Default to True] to un-subscribe previous subscribed topics
        :return: the result of the topic
        """
        if not topics:
            topics = self.topics
        if type(topics) == str:
            topics = [topics]
        for top in topics:
            if top not in self.topics:
                self.socket.setsockopt(zmq.SUBSCRIBE, top.encode(self.code))
                self.logger.debug('Subscribed ' + top)
        if topics and cleanup:
            # un-subscribe previous
            for top in topics:
                if top not in self.topics:
                    self.socket.setsockopt(zmq.UNSUBSCRIBE, top.encode(self.code))
                    self.logger.debug('Un-subscribed ' + top)
        return topics

    def sub_raw(self):
        """
        Raw method of sub
        :return: topic & data
        """
        topic, data = self.socket.recv_multipart()
        self.last_topic = topic
        return topic, data

    def sub(self, topics=None):
        if topics and self.topics != topics:
            # listen to the new topics
            # tps=self.sub_topics(topics)
            self.topics = self.sub_topics(topics)
            self.logger.debug('Subscriber to:' + str(self.topics))
        topic, data = self.sub_raw()
        self.logger.debug('Received [' + topic.decode(self.code) + '] ' + data.decode(self.code))
        return data.decode(self.code)


class MessagePusher(QueueConnector):
    def __init__(self, host='tcp://127.0.0.1', port=12116, logger_name='Q_pub', code='utf-8'):
        QueueConnector.__init__(self, zmq.PUSH, host=host, port=port, mode='bind', logger_name=logger_name)
        self.code = code

    def pre_connect(self):
        pass


class MessagePuller(QueueConnector):
    def __init__(self, host='tcp://127.0.0.1', port=12116, logger_name='Q_pub', code='utf-8'):
        QueueConnector.__init__(self, zmq.PULL, host=host, port=port, logger_name=logger_name)
        self.code = code

    def pre_connect(self):
        pass