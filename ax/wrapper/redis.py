"""
The redis components for Cache/ Queue

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-03"
__version__ = "0.2"

    Version:
        0.1 (10/12/2017): implemented basic definition
        0.2 (03/03/2018): added timeout to pubsub


Classes:
    Cache - To access redis cache
    PubSub - To access redis pub/sub queues
"""
import os
import pickle
import redis
from ax.exception import Timeout
from ax.datetime import current_sys_time
from ax.common import Connector


class Base(Connector):
    """
    Base Class for all redis components
    """
    def __init__(self, logger_name, host='localhost', port=12116, db=11):
        Connector.__init__(self, host=host, port=port, logger_name=logger_name)
        self.db = db
        self._redis = None

    def connect(self, rds=redis.StrictRedis, **kwargs):
        if 'passwword' not in kwargs:
            pwd = os.environ.get('TOBY_REDIS_PASSWD',None)
            if pwd:
                kwargs['password'] = pwd
        self._redis = rds(host=self.host, port=self.port, db=self.db, **kwargs)


class Cache(Base):
    """
    Cahce based on redis
    """
    def __init__(self, logger_name='Cache', host='localhost', port=12116, db=11, redis_instance=None, **kwargs):
        Base.__init__(self, logger_name=logger_name, host=host, port=port, db=db)
        if redis_instance is None:
            self.connect(rds=redis.StrictRedis, **kwargs)
        else:
            # allow passing in redis instance
            self._redis = redis_instance
        # enable expire function
        self.expire = self._redis.expire
        # self._char_to_type = {b"s": str, b"i": int, b"f": float}
        # self._type_to_char = {self._char_to_type[c]: c for c in self._char_to_type}
        
        
    def get_instance(self):
        """
        return the redis connection for reuse
        """
        return self._redis
        

    def put(self, key, subkey=None, val=None, expire=-1):
        """
        Save an object to cache, pickle if not str/int/float 
        
        :param key: The key 
        :param subkey: the sub key if has, None if not
        :param val: the object to be save
        :param expire: expire time -1 for not exipre
        :return: the redis save result
        """
        o = pickle.dumps(val)
        if not subkey:
            r = self._redis.set(key, o)
        else:
            r = self._redis.hset(key, subkey, o)
        if expire > 0:
            self._redis.expire(key, expire)
        return r
    

    def count(self, key, subkey=None, step=1):
        """
        Increase/Decrease a value in key & subkey if any
        
        :param key: the key
        :param subkey: the subkey if has
        :param step: step to increase
        :return: N/A
        """
        if subkey:
            self._redis.hincrby(key, subkey, amount=step)
        else:
            self._redis.incrby(key, amount=step)

            
    def get(self, key, subkey=None):
        """
        Fetch from the cache by key/ subkey
        
        :param key: the Key
        :param subkey: the sub key if has
        :return: the fetched object None if not exist
        """
        r = self._redis.hget(key, subkey) if subkey else self._redis.get(key)
        if r:
            rtn = pickle.loads(r)
        else:
            rtn = None
        return rtn
    
    
    def scan(self, match='*', start=0, count=None):
        """
        Scan all keys with match pattern
        :param match: the Key match pattern
        :param start: [Optional] the start point of return if specified
        :param count: [Optional] how many records to return if specified
        :return: the scan result
        """
        return self._redis.scan(cursor=start,match=match,count=count)
    
    
    def sub_scan(self, key, match='*', start=0, count=None):
        """
        Scan all keys with match pattern
        :param key: the Key
        :param match: the subKey match pattern
        :param start: [Optional] the start point of return if specified
        :param count: [Optional] how many records to return if specified
        :return: the scan result
        """
        return self._redis.hscan(key, cursor=start,match=match,count=count)
    
    
    def delete(self, key, *subkey):
        """
        Fetch from the cache by key/ subkey
        
        :param key: the Key
        :param *subkey: the sub key(s), if not specified, delete the whole key
        :return: the fetched object None if not exist
        """
        if subkey:
            rtn = self._redis.hdel(key,*subkey)
        else:
            rtn = self._redis.delete(key)
        return rtn
        

class Queue(Base):
    """
    Queue based redis
        Pub/Sub
        Push/ Pop
    """
    def __init__(self, logger_name='Queue', host='localhost', port=12116, db=11, timeout=-1, redis_instance=None, **kwargs):
        Base.__init__(self, logger_name=logger_name, host=host, port=port, db=db)
        kwargs = dict()
        self.channels = None
        self.last_channel = None
        self.timeout = timeout
        if timeout > 0:
            kwargs['socket_timeout'] = timeout
        if redis_instance is None:
            self.connect(rds=redis.Redis, **kwargs)
        else:
            # allow passing in redis instance
            self._redis = redis_instance
        self._redis_pubsub = self._redis.pubsub(ignore_subscribe_messages=True)

    
    

    
    @staticmethod
    def _pack_msg(msg):
        m = pickle.dumps(msg)
        return m

    def _unpack_msg(self, queue_inp):
        m = None
        if queue_inp is not None:
            m = pickle.loads(queue_inp['data']) if queue_inp.get('data', None) is not None else None
            self.last_channel = queue_inp['channel'].decode()
        return m
    
    """
    Push/ Pop
    """
    def push(self, queue_name, message):
        self._redis.rpush(queue_name, self._pack_msg(message))

    def pop(self, queue_name):
        out = self._redis.lpop(queue_name)
        return None if out is None else self._unpack_msg(out)
    
    
    """
    Pub/ Sub
    """
    def pub(self, channel, message):
        self._redis.publish(channel, self._pack_msg(message))

    def sub(self, *channels, timeout=-1, wildcard=True):
        """
        Subscribe and return result 
        
        :param channels: the channels to listen 
        :param timeout: if <0 use block mode, else, timeout in provided seconds
        :param wildcard: is wildcard to be used in channels (subscribe/ psubscribe)
        :return: 
        """
        if channels != self.channels:
            self.unsub()
            if wildcard:
                self._redis_pubsub.psubscribe(*channels)
            else:
                self._redis_pubsub.subscribe(*channels)
            self.channels = channels
            self.logger.debug('Subscribed to queue:'+str(channels))
        if timeout < 0 and self.timeout < 0:
            # Block until receive
            for msg in self._redis_pubsub.listen():
                rtn = msg
                break
            # rtn = self._redis_pubsub.listen()
        else:
            timeout_ts = current_sys_time()+timeout
            rtn = None
            while rtn is None and timeout_ts > current_sys_time():
                rtn = self._redis_pubsub.get_message(ignore_subscribe_messages=True, timeout=timeout)
            if rtn is None:
                raise Timeout('Timeout while listening to queue:'+str(self.channels))

        return self._unpack_msg(rtn)

    
    def unsub(self):
        self._redis_pubsub.punsubscribe()
        self._redis_pubsub.unsubscribe()
        

    def pubsub(self, to_topic, req_obj, from_topic, timeout=-1):
        """

        :param to_topic: the queue which req_obj should be sent to
        :param req_obj: the request object
        :param from_topic: the queue should listen to result
        :param timeout: timeout of listening (-1 is block forever)
        :return: returned object
        """
        self.pub(to_topic, req_obj)
        return self.sub(from_topic, timeout=timeout, wildcard=False)
