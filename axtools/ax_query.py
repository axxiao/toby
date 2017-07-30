"""
The query common adapter
This is the common objects for all kind of queries

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-07-02"
__version__ = "0.1"

    Version:
        0.1 : implemented basic definition

"""
import pandas


class ResultSet(pandas.DataFrame):

    def update(self, other, join='left', overwrite=True, filter_func=None, raise_conflict=False):
        pass

    def __init__(self):
        pass
