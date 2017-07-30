"""
The queue of using redis
This is the connector which will be the redis message queue adapter

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-02"
__version__ = "0.1"

    Version:
        0.1 : implemented basic definition

"""
import redis
import pickle


class Q_Pub():

    r=redis.Redis(host='localhost', port=6379, db=0)
    p=r.pubsub()

    r.publish('ch1','b')
    p.get_message()