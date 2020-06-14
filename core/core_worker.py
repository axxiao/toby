"""
The base worker which get task from core

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-03-11"
__version__ = "0.1"

    Version:
        0.1 2018-03-11: implemented by using zmq pull-push mode to pull task from core
        0.2 2018-09-02: changed backend to Dask distributed, based on master/distributed/cli/dask_worker.py
                            https://github.com/dask/distributed/blob/master/distributed/cli/dask_worker.py

"""
from __future__ import print_function, division, absolute_import

import atexit
import logging
import os
from sys import exit

import click
from distributed import Nanny, Worker
from distributed.config import config
from distributed.utils import get_ip_interface, parse_timedelta
from distributed.worker import _ncores
from distributed.security import Security
from distributed.cli.utils import (check_python_3, uri_from_host_port,
                                   install_signal_handlers)
from distributed.comm import get_address_host_port
from distributed.preloading import validate_preload_argv
from distributed.proctitle import (enable_proctitle_on_children,
                                   enable_proctitle_on_current)

from toolz import valmap
from tornado.ioloop import IOLoop, TimeoutError
from tornado import gen
"""
By AX
"""
from distributed import Worker
from distributed.threadpoolexecutor import ThreadPoolExecutor
# from distributed.worker import _ncores
from ax.connection import Connector
from ax.log import get_logger
from ax.tools import load_function


class TobyBaseExecutor(ThreadPoolExecutor):
    """
    The base Executor for all Toby workers

    By default, worker has toby_task_flag = True, it will include 2 objects
    - toby_logger : the logger
    - toby_cache : the Cache object instance
    """

    def __init__(self, *args, **kwargs):
        ThreadPoolExecutor.__init__(self, *args, **kwargs)
        self.cache = None
        self.logger = None
        self.logger_name = kwargs.get('logger_name', 'Toby.Workflow.BaseExecutor')
        self.kwargs = dict()
        self.kwargs['toby_connector'] = Connector(logger_name=self.logger_name)
        self.kwargs['toby_logger'] = get_logger(self.logger_name)
        self.kwargs['toby_executor'] = super(TobyBaseExecutor, self)
        self.setup()

    def setup(self):
        # to include all pre-defined kwargs
        # To be overridden by the upper class
        pass

    def submit(self, fn, *args, **kwargs):
        # pass items to base executor's submit function
        # actual function itself is args[0] args is args[1], kwargs is args[2]
        # fn is always apply functions/ apply_function_actor
        if kwargs.get('toby_task_flag', False):
            func_kwargs = args[2]
            func_args = list(args)
            func_args[2] = {**func_kwargs, **self.kwargs}
        return super(TobyBaseExecutor, self).submit(fn, *tuple(func_args), **kwargs)


class TobyBaseWorker(Worker):
    """
    The Base worker for all Toby workers, by default, use TobyBaseExecutor
    """

    def __init__(self, *args, executor=TobyBaseExecutor, **kwargs):
        """
        Init the worker
        :param args: the arguments for the worker
        :param executor:
        :param kwargs: the key-word arguments for the worker
        """
        Worker.__init__(self, *args, executor=executor(kwargs.get('ncores') or _ncores), **kwargs)


class TobyStandardWorker(TobyBaseWorker):
    """
    The standard Toby Worker
    """

    def __init__(self, *args, **kwargs):
        """Sample code, in case of to create additional """

        class Executor(TobyBaseExecutor):

            def setup(self):
                self.kwargs['sample_object_instance'] = None

        TobyBaseWorker.__init__(self, *args, executor=Executor, **kwargs)


"""
End of by AX
"""
logger = logging.getLogger('distributed.dask_worker')


pem_file_option_type = click.Path(exists=True, resolve_path=True)


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('scheduler', type=str, required=False)
@click.option('--tls-ca-file', type=pem_file_option_type, default=None,
              help="CA cert(s) file for TLS (in PEM format)")
@click.option('--tls-cert', type=pem_file_option_type, default=None,
              help="certificate file for TLS (in PEM format)")
@click.option('--tls-key', type=pem_file_option_type, default=None,
              help="private key file for TLS (in PEM format)")
@click.option('--worker-port', type=int, default=0,
              help="Serving computation port, defaults to random")
@click.option('--nanny-port', type=int, default=0,
              help="Serving nanny port, defaults to random")
@click.option('--bokeh-port', type=int, default=0,
              help="Bokeh port, defaults to random port")
@click.option('--bokeh/--no-bokeh', 'bokeh', default=True, show_default=True,
              required=False, help="Launch Bokeh Web UI")
@click.option('--listen-address', type=str, default=None,
        help="The address to which the worker binds. "
             "Example: tcp://0.0.0.0:9000")
@click.option('--contact-address', type=str, default=None,
        help="The address the worker advertises to the scheduler for "
             "communication with it and other workers. "
             "Example: tcp://127.0.0.1:9000")
@click.option('--host', type=str, default=None,
              help="Serving host. Should be an ip address that is"
                   " visible to the scheduler and other workers. "
                   "See --listen-address and --contact-address if you "
                   "need different listen and contact addresses. "
                   "See --interface.")
@click.option('--interface', type=str, default=None,
              help="Network interface like 'eth0' or 'ib0'")
@click.option('--nthreads', type=int, default=0,
              help="Number of threads per process.")
@click.option('--nprocs', type=int, default=1,
              help="Number of worker processes to launch.  Defaults to one.")
@click.option('--name', type=str, default='',
              help="A unique name for this worker like 'worker-1'. "
                   "If used with --nprocs then the process number "
                   "will be appended like name-0, name-1, name-2, ...")
@click.option('--memory-limit', default='auto',
              help="Bytes of memory per process that the worker can use. "
                   "This can be an integer (bytes), "
                   "float (fraction of total system memory), "
                   "string (like 5GB or 5000M), "
                   "'auto', or zero for no memory management")
@click.option('--reconnect/--no-reconnect', default=True,
              help="Reconnect to scheduler if disconnected")
@click.option('--nanny/--no-nanny', default=True,
              help="Start workers in nanny process for management")
@click.option('--pid-file', type=str, default='',
              help="File to write the process PID")
@click.option('--local-directory', default='', type=str,
              help="Directory to place worker files")
@click.option('--resources', type=str, default='',
              help='Resources for task constraints like "GPU=2 MEM=10e9"')
@click.option('--scheduler-file', type=str, default='',
              help='Filename to JSON encoded scheduler information. '
                   'Use with dask-scheduler --scheduler-file')
@click.option('--death-timeout', type=str, default=None,
              help="Seconds to wait for a scheduler before closing")
@click.option('--bokeh-prefix', type=str, default=None,
              help="Prefix for the bokeh app")
@click.option('--preload', type=str, multiple=True, is_eager=True,
              help='Module that should be loaded by each worker process '
                   'like "foo.bar" or "/path/to/foo.py"')
# ax: added worker_class
@click.option('--worker-class', type=str, default='core.core_worker.TobyStandardWorker',
              help="The full path to worker class, by default: core.core_worker.TobyStandardWorker")
@click.argument('preload_argv', nargs=-1,
                type=click.UNPROCESSED, callback=validate_preload_argv)
def main(scheduler, host, worker_port, listen_address, contact_address,
         nanny_port, nthreads, nprocs, nanny, name,
         memory_limit, pid_file, reconnect, resources, bokeh,
         bokeh_port, local_directory, scheduler_file, interface,
         death_timeout, preload, preload_argv, bokeh_prefix, tls_ca_file,
         tls_cert, tls_key, worker_class):
    # ax: added worker_class
    enable_proctitle_on_current()
    enable_proctitle_on_children()

    sec = Security(tls_ca_file=tls_ca_file,
                   tls_worker_cert=tls_cert,
                   tls_worker_key=tls_key,
                   )

    if nprocs > 1 and worker_port != 0:
        logger.error("Failed to launch worker.  You cannot use the --port argument when nprocs > 1.")
        exit(1)

    if nprocs > 1 and not nanny:
        logger.error("Failed to launch worker.  You cannot use the --no-nanny argument when nprocs > 1.")
        exit(1)

    if contact_address and not listen_address:
        logger.error("Failed to launch worker. "
                     "Must specify --listen-address when --contact-address is given")
        exit(1)

    if nprocs > 1 and listen_address:
        logger.error("Failed to launch worker. "
                     "You cannot specify --listen-address when nprocs > 1.")
        exit(1)

    if (worker_port or host) and listen_address:
        logger.error("Failed to launch worker. "
                     "You cannot specify --listen-address when --worker-port or --host is given.")
        exit(1)

    try:
        if listen_address:
            (host, worker_port) = get_address_host_port(listen_address, strict=True)

        if contact_address:
            # we only need this to verify it is getting parsed
            (_, _) = get_address_host_port(contact_address, strict=True)
        else:
            # if contact address is not present we use the listen_address for contact
            contact_address = listen_address
    except ValueError as e:
        logger.error("Failed to launch worker. " + str(e))
        exit(1)

    if nanny:
        port = nanny_port
    else:
        port = worker_port

    if not nthreads:
        nthreads = _ncores // nprocs

    if pid_file:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))

        def del_pid_file():
            if os.path.exists(pid_file):
                os.remove(pid_file)
        atexit.register(del_pid_file)

    services = {}

    if bokeh:
        try:
            from distributed.bokeh.worker import BokehWorker
        except ImportError:
            pass
        else:
            if bokeh_prefix:
                result = (BokehWorker, {'prefix': bokeh_prefix})
            else:
                result = BokehWorker
            services[('bokeh', bokeh_port)] = result

    if resources:
        resources = resources.replace(',', ' ').split()
        resources = dict(pair.split('=') for pair in resources)
        resources = valmap(float, resources)
    else:
        resources = None

    loop = IOLoop.current()

    if nanny:
        kwargs = {'worker_port': worker_port, 'listen_address': listen_address}
        t = Nanny
    else:
        kwargs = {}
        if nanny_port:
            kwargs['service_ports'] = {'nanny': nanny_port}
        t = Worker

    if not scheduler and not scheduler_file and 'scheduler-address' not in config:
        raise ValueError("Need to provide scheduler address like\n"
                         "dask-worker SCHEDULER_ADDRESS:8786")

    if interface:
        if host:
            raise ValueError("Can not specify both interface and host")
        else:
            host = get_ip_interface(interface)

    if host or port:
        addr = uri_from_host_port(host, port, 0)
    else:
        # Choose appropriate address for scheduler
        addr = None

    if death_timeout is not None:
        death_timeout = parse_timedelta(death_timeout, 's')

    WK = load_function(worker_class, logger, True)

    nannies = [t(scheduler, scheduler_file=scheduler_file, ncores=nthreads,
                 services=services, loop=loop, resources=resources,
                 memory_limit=memory_limit, reconnect=reconnect,
                 local_dir=local_directory, death_timeout=death_timeout,
                 preload=preload, preload_argv=preload_argv,
                 security=sec, contact_address=contact_address,
                 name=name if nprocs == 1 or not name else name + '-' + str(i),
                 # ax
                 worker_class=worker_class,
                 **kwargs)
               for i in range(nprocs)]

    @gen.coroutine
    def close_all():
        # Unregister all workers from scheduler
        if nanny:
            yield [n._close(timeout=2) for n in nannies]

    def on_signal(signum):
        logger.info("Exiting on signal %d", signum)
        close_all()

    @gen.coroutine
    def run():
        yield [n._start(addr) for n in nannies]
        while all(n.status != 'closed' for n in nannies):
            yield gen.sleep(0.2)

    install_signal_handlers(loop, cleanup=on_signal)

    try:
        loop.run_sync(run)
    except (KeyboardInterrupt, TimeoutError):
        pass
    finally:
        logger.info("End worker")


def go():
    check_python_3()
    main()


if __name__ == '__main__':
    go()
