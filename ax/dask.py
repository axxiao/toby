"""
The place for logging process

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-15"
__version__ = "0.1"

    Version:
        0.1 : implemented basic Dask Client

"""
from uuid import uuid4
from .exception import NoAvailableWorker
from .base import Connector
from .tools import reload_module
from dask.distributed import Client, wait, fire_and_forget
from distributed.utils import sync



class DaskClient(Client, Connector):
    def __init__(self, host='tcp://127.0.0.1', port=8786, name='Dask.Client', logger_name='Toby.Dask',dedicate_workers=None):
        Connector.__init__(self, host=host, port=port, logger_name=logger_name)
        Client.__init__(self, address=host+':'+str(port), name=name)
        self.dedicate_workers = dedicate_workers
        self.only_on_dedicate_workers = True
        self.save_data = self.set_metadata
        self.get_data = self.get_metadata
        self.all_workers = []

    def set_dedicate_workers(self, workers, only_on_dedicate_workers=False, error_if_not_found=True):
        """
        Set the functions only run on certain workers
        :param workers: the list of workers can run thr function. Note, if worker starts with nprocs=X, the worker name
         will have a number [0 to X-1] at the end in format of [worker name]-x, e.g. worker_name-0
        :param only_on_dedicate_workers: allow the other workers to help
        :return: None
        """
        self.all_workers = self.get_workers_info()['workers']
        vis_workers = dict()
        for wrk in self.all_workers:
            w = self.all_workers[wrk]
            vis_workers[w['name']] = wrk
        valid_workers = []
        for w in workers if type(workers) != str else [workers]:
            # valid if the name is ok
            for x in vis_workers.keys():
                if x[:len(w)] == w:
                    valid_workers.append(x)
        self.dedicate_workers = None if valid_workers == [] else valid_workers
        self.only_on_dedicate_workers = only_on_dedicate_workers
        if error_if_not_found and self.dedicate_workers is None:
            raise NoAvailableWorker(workers)

    def load_library_from_file(self, filename, module_name, timeout=600):
        self.upload_file(filename)
        wait(self.run_task_on_echo_worker(reload_module, module_name, logger=self.logger), timeout=timeout)

    def run_task(self, func, *args, task_timeout=60, **kwargs):
        """
        Run the function on the worker and get return value

        :param func: function to be run
        :param args: arguments
        :param task_timeout: the timeout period for return, default to 1 minute
        :param kwargs: keyword-arguments
        :return: function result
        """
        #if 'worker_num' in kwargs:
        #    kwargs['resources']={'wname': kwargs.pop('worker_num')}
        #return wait(self.submit(func, *args, **kwargs))[0].pop().result()
        kwargs['return_type'] = kwargs.get('return_type', 'value')
        kwargs['force_rerun'] = kwargs.get('force_rerun', False)
        return wait(self.async_task(func, *args, **kwargs), timeout=task_timeout)[0].pop().result()

    def get_workers_list(self):
        """
        Get the list of workers
        :return: list of workers
        """
        return list(self.ncores().keys())

    def get_workers_info(self):
        """
        Return list of info for all workers
        :return: Dict of all workers
        """
        return sync(self.loop, self.scheduler.identity)

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
            res.append(self.submit(func, *args, **kwargs, key=str(uuid4()), workers=worker))
            self.logger.info('Submitted '+func.__name__+' on worker '+worker)
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
        if self.dedicate_workers is not None and 'workers' not in kwargs:
            kwargs['workers'] = self.dedicate_workers
            if 'allow_other_workers' not in kwargs:
                kwargs['allow_other_workers'] = not self.only_on_dedicate_workers

        f = self.submit(func, key=str(uuid4()) if force_rerun else None, *args, **kwargs)
        if return_type == 'key':
            rtn = f.key
            fire_and_forget(f)
        else:
            rtn = f
        return rtn
