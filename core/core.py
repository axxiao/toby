"""
This is the core of the Toby

core is a task distributing centre, it listen to the queue and distribute the message to corresponding worker(s)

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-11"
__version__ = "0.1"

    Version:
        0.1 : implemented by using Redis queue + zmq pull-push mode to push task to workers

"""
from ax.queue import Queue


class Distributor:
    def __init__(self):
        pass