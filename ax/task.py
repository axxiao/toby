"""
This is the main interface for all tasks
"""
from .dask import DaskClient


class TaskRunner(DaskClient):
    def __init__(self, host='127.0.0.1', port=12116, logger_name='TaskRunner'):
        DaskClient.__init__(self, host=host, port=port, logger_name=logger_name)


shared_runner = TaskRunner()


def run_task(func, *args, **kwargs):
    return shared_runner.run_task(func, *args, **kwargs)


def reload_library(library_file_name, module_name):
    shared_runner.load_library_from_file(library_file_name, module_name)


