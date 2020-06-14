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
from .base import get_context
from ax.wrapper.sqlalchemy import Connection as DatabaseConnection


def get_db_connection(user_name, password, *args, **kwargs):
    """
    Context managed get db connection function
    :param user_name: user name
    :param password: password
    :param args: additional arguments for DatabaseConnection
    :param kwargs: additional key-word arguments for DatabaseConnection
    :return: context object
    """
    return get_context(DatabaseConnection, user_name, password, *args, **kwargs)
