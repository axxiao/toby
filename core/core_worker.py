"""
The base worker which get task from core

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-11"
__version__ = "0.1"

    Version:
        0.1 : implemented by using zmq pull-push mode to pull task from core

"""
import sys
from celery import Celery

worker = Celery()

class Worker:
    def __init__(self):

        pass


if __name__ == "__main__":
    # get the input args
    args = sys.argv[1:]
