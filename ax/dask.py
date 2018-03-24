"""
The place for logging process

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-15"
__version__ = "0.1"

    Version:
        0.1 : implemented basic Dask Client

"""
from uuid import uuid4
from .base import Connector
from dask.distributed import Client, wait, fire_and_forget


class DaskClient(Client, Connector):
    def __init__(self, host='tcp://127.0.0.1', port=8786, name='Dask.Client', logger_name='Toby.Dask'):
        Connector.__init__(self, host=host, port=port, logger_name=logger_name)
        Client.__init__(self,address=host+':'+str(port), name=name)

    def run_task(self, func, *args,  **kwargs):
        """
        Run the function on the worker and get return value

        :param func: function to be run
        :param args: arguments
        :param kwargs: keyword-arguments
        :return: function result
        """
        #if 'worker_num' in kwargs:
        #    kwargs['resources']={'wname': kwargs.pop('worker_num')}

        return wait(self.submit(func, *args, **kwargs))[0].pop().result()

    def get_workers_list(self):
        """
        Get the list of workers
        :return: list of workers
        """
        return list(self.ncores().keys())

    def run_task_on_echo_worker(self, func, *args,  **kwargs):
        """
        Run a task on *each* worker, useful for tasks e.g. reload library
        :param func: the function to run
        :param args: arguments
        :param kwargs: keyword-arguments
        :return: list of future status
        """
        res = []
        for worker in self.get_workers_list():
            res.append(self.submit(func, *args, **kwargs, key=str(uuid4()),workers=worker))
        return res

    def get_status(self, future_key):
        """
        Get the status by future key

        :param future_key: the key value of the future
        :return: status, unknown if key could not be found
        """
        f_staus = self.futures.get(future_key, None)
        return f_staus.status if f_staus is not None else 'unknown'

    def async_task(self, func, *args, return_type='key', force_rerun=True, **kwargs):
        """
        Run the function on the worker in async mode

        :param func: function to be run
        :param args: keyword-arguments
        :param return_type: [default to 'key'] return the key of future or the future
        :param force_rerun: [default to True] if true, generate a unique key to make sure run the code without cache
        :param kwargs: keyword-arguments
        :return: the key value if return_type='key' (default) else teh future
        """
        #if 'worker_num' in kwargs:
        #    kwargs['resources'] = {'wname': kwargs.pop('worker_num')}
        f = self.submit(func, key=str(uuid4()) if force_rerun else None, *args, **kwargs)
        if return_type == 'key':
            rtn = f.key
            fire_and_forget(f)
        else:
            rtn = f
        return rtn
