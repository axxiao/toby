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
        0.4 (22/04/2019 AX) : Restructured to be songle place for all connections

"""
from ax.wrapper.sqlalchemy import Connection as DatabaseConnection
