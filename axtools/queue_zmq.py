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
import sys
import time
from threading import Thread

'''
        The comon base class for all connectors
    '''
class Base_connector():
    def __init__(self, host='tcp://127.0.0.1', port=12116, logger=None):
        self.host = host
        self.port = port
        self.socket = None
        self.context = None
        if logger == None:
            self.logger = lambda: None
            self.logger.error = print
            self.logger.info = print
            self.logger.debug = print
            self.logger.warn = print
            self.logger.critical = print
        else:
            self.logger = logger


'''
    The device which exchanges messages between pub/sub
'''
class Q_device(Thread,Base_connector):
    '''
        The device whcih exchanges messages between pub/sub, router/dealer, push puller
        
        Input parameters:
            name : the name of device - default to Exchanger
            mode: the pair of in & out port, default to [zmq.SUB,zmq.PUB]
            port_in: in port number default to 12116
            port_out: output port number default to 1217
            port_mointor: monitor port, default to -1, if greater than 0, will open monitor port (PUB)
            logger: pass in logger otherwise will use print
        
        Sample code:
            ex=Q_device(name='Exchanger',mode=[zmq.SUB,zmq.PUB],port_in=12116,port_out=12117,port_monitor=-1,logger=None)
            ex.setDaemon(True)
            ex.start()
    '''
    def __init__(self,name='Exchanger',mode=[zmq.SUB,zmq.PUB],port_in=12116,port_out=12117,port_monitor=-1,logger=None):
        Thread.__init__(self)
        Base_connector.__init__(self,logger=logger)
        self.name=name
        self.port_in = port_in
        self.port_out=port_out
        self.port_monitor=port_monitor
        self.mode=mode
        self.mode_map={zmq.PUB:'Pub',zmq.SUB:'Sub',
                       zmq.ROUTER: 'Router', zmq.DEALER: 'Dealer',
                       zmq.PUSH: 'Push', zmq.PULL: 'Pull'
                       }

    def run(self):
        #try:
        self.context =None
        self.frontend = None
        self.backend = None
        self.monitor=None
        try:
            self.context = zmq.Context()
            # Socket facing clients
            self.logger.debug('Got context')
            self.frontend = self.context.socket(self.mode[0])
            addr="tcp://*:"+str(self.port_in)
            self.logger.debug('Tring to bind In port at '+addr)
            self.frontend.bind(addr)
            self.logger.debug('In port '+self.mode_map[self.mode[0]]+' is up at '+addr)

            # Socket facing services
            self.backend = self.context.socket(self.mode[1])
            self.logger.debug('Tring to bind Out port at ' + addr)
            addr="tcp://*:"+str(self.port_out)
            self.backend.bind(addr)
            self.logger.debug('Out port ' + self.mode_map[self.mode[1]] + ' is up at ' + addr)

            if self.port_monitor>0:
                self.monitor = self.context.socket(zmq.PUB)
                self.logger.debug('Tring to bind Monitor port at ' + addr)
                addr = "tcp://*:" + str(self.port_monitor)
                self.monitor.bind(addr)
                self.logger.debug('Monitor port PUB is up at ' + addr)

            self.logger.info(self.name+" is ONLINE")
            #zmq.device(zmq.FORWARDER, frontend, backend)
            zmq.proxy(self.frontend,self.backend,self.monitor)
        except Exception as e:
            self.logger.error(self.name+" is having issues")
            self.logger.error(e.args)
        finally:
        #    pass
            self.logger.info(self.name+" is preparing to go offline")
            if self.frontend: self.frontend.close()
            if self.backend: self.backend.close()
            if self.backend: self.backend.close()
            if self.context: self.context.term()
            self.logger.info(self.name+" is OFFLINE")

