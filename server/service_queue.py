import sys
sys.path.insert(0, "/home/toby/workspace/toby")
from axtools.ax_log import build_logger
from axtools.ax_queue_zmq import Q_Device,Q_Sub
from threading import Thread





class Monitor(Thread):
    def __init__(self, logger):
        Thread.__init__(self)
        self.logger = logger
        self.sub=Q_Sub('')

    def run(self):
        cnt = 0
        while True:
            in_msg=self.sub.sub()
            cnt += 1



if __name__ == "__main__":
    logger=build_logger('Toby.Queue')
    logger.info('Starting Queue Service')
    dev = Q_Device(logger_name='Toby.Queue', port_monitor=12110)
    dev.start()
    dev.join()