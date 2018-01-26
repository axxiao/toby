import sys
sys.path.insert(0, "/home/toby/workspace/toby")
from ax.log import build_logger
from ax.zmq import QueueDevice, QueueSub
from threading import Thread


class Monitor(Thread):
    def __init__(self, logger):
        Thread.__init__(self)
        self.logger = logger
        self.sub = QueueSub('')

    def run(self):
        cnt = 0
        while True:
            self.sub.sub()
            cnt += 1


if __name__ == "__main__":
    logger = build_logger('Toby.Queue')
    logger.info('Starting Queue Service')
    dev = QueueDevice(logger_name='Toby.Queue', port_monitor=12110)
    dev.start()
    dev.join()