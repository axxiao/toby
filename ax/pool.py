"""
The pool holds many request and start tasks according


__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-04-22"
__version__ = "0.5"

"""
from .base import Connector

class Pool(Connector):
    def __init__(self, logger_name, host='localhost', port=12116, db=11):
        Connector.__init__(self, host=host, port=port, logger_name=logger_name)
