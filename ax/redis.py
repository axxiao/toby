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
from .exception import Timeout
from .datetime import current_sys_time
from .base import Connector


class Base(Connector):
    """
    Base Class for all redis components
    """
    def __init__(self, logger_name, host='localhost', port=12116, db=11):
        Connector.__init__(self, host=host, port=port, logger_name=logger_name)
        self.db = db
        self.redis = None

    def connect(self, rds=redis.Redis, **kwargs):
        if 'passwword' not in kwargs:
            pwd=os.environ.get('REDIS_PASSWD',None)
            if pwd:
                kwargs['password'] = pwd
        self.redis = rds(host=self.host, port=self.port, db=self.db, **kwargs)


class Cache(Base):
    def __init__(self, logger_name='Cache', host='localhost', port=12116, db=11, **kwargs):
        Base.__init__(self, logger_name=logger_name, host=host, port=port, db=db)
        self.connect(rds=redis.Redis, **kwargs)

    def save(self, key, subkey=None, val=None, expire=-1):
        """
        Save an object to cache, pickle if not str/int/float 
        
        :param key: The key 
        :param subkey: the sub key if has, None if not
        :param val: the object to be save
        :param expire: expire time -1 for not exipre
        :return: the redis save result
        """
        o = val if type(val) in [str, int, float,  None] else pickle.dumps(val)
        if not subkey:
            r = self.redis.set(key, o)
        else:
            r = self.redis.hset(key, subkey, o)
        if expire > 0:
            self.redis.expire(key, expire)
        return r

    def update(self, key, subkey=None, step=1):
        """
        Increase/Decrease a value in key & subkey if any
        
        :param key: the key
        :param subkey: the subkey if has
        :param step: step to increase
        :return: N/A
        """
        if subkey:
            self.redis.hincrby(key, subkey, amount=step)
        else:
            self.redis.incrby(key, amount=step)

    def fetch(self, key, subkey=None, fetch_type=object):
        """
        Fetch from the cache by key/ subkey
        
        :param key: the Key
        :param subkey: the sub key if has
        :param fetch_type: the type of object, e.g. int str, default will try to unpickle object;
        :return: the fetched object None if not exist
        """
        r = self.redis.hget(key, subkey) if subkey else self.redis.get(key)
        if r:
            rtn = pickle.loads(r) if fetch_type == object else fetch_type(r.decode())
        else:
            rtn = None
        return rtn


class PubSub(Base):
    def __init__(self, logger_name='Queue', host='localhost', port=12116, db=11, timeout=-1, **kwargs):
        Base.__init__(self, logger_name=logger_name, host=host, port=port, db=db)
        kwargs = dict()
        self.channels = None
        self.last_channel = None
        self.timeout = timeout
        if timeout > 0:
            kwargs['socket_timeout'] = timeout
        self.connect(redis.StrictRedis, **kwargs)
        self.redis_pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

    def pub(self, channel, message):
        self.redis.publish(channel, self._pack_msg(message))

    def _pack_msg(self, msg):
        m = pickle.dumps(msg)
        return m

    def _unpack_msg(self, queue_inp):
        m = None
        if queue_inp is not None:
            m=pickle.loads(queue_inp['data']) if queue_inp.get('data', None) is not None else None
            self.last_channel = queue_inp['channel'].decode()
        return m

    def sub(self, *channels, timeout=-1, wildcard=True):
        """
        Subscribe and return result 
        
        :param channels: the channels to listen 
        :param timeout: if <0 use block mode, eles, timeout in provided seconds
        :param wildcard: is wildcard to be used in channels (subscribe/ psubscribe)
        :return: 
        """
        if channels != self.channels:
            self.unsub()
            if wildcard:
                self.redis_pubsub.psubscribe(*channels)
            else:
                self.redis_pubsub.subscribe(*channels)
            self.channels = channels
            self.logger.debug('Subscribed to queue:'+str(channels))
        if timeout < 0:
            #Block until receive
            #for msg in self.redis_pubsub.listen():
            #    rtn = msg
            #    break
            rtn = next(self.redis_pubsub.listen())
        else:
            timeout_ts = current_sys_time()+timeout
            rtn = None
            while rtn is None and timeout_ts > current_sys_time():
                rtn = self.redis_pubsub.get_message(ignore_subscribe_messages=True, timeout=timeout)
            if rtn is None:
                raise Timeout('Timeout while listening to queue:'+str(self.channels))

        return self._unpack_msg(rtn)

    def unsub(self):
        self.redis_pubsub.unsubscribe()
