"""
The wrapper for Postgres through SQLAchemy

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-11-03"
__version__ = "0.1"

    Version:
        0.1 (03/11/2018 AX) : init
        

"""
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
import pandas
from ax.log import get_logger


class Connection:
    """
    Base Class for all SQL Alchemy Connection
    """
    def __init__(self, user, password, logger_name='Toby.DB', db_type='postgresql+psycopg2', host='localhost',
                 port=5432, db='toby', encoding='utf8'):
        self._connection = None
        self._uri = None
        self._encoding = encoding
        self.logger = get_logger(logger_name)
        self.connect(db_type, user, password, host, port, db, encoding)
    
    def connect(self, db_type, user, password, host='localhost', port=5432, db='toby', encoding='utf8'):
        self._uri = '{}://{}:{}@{}:{}/{}'
        if not self._connection or self._connection.closed:
            self._connection = create_engine(self._uri.format(db_type, quote_plus(user), quote_plus(password), host,
                                                              port, db), client_encoding=encoding).connect()

    def disconnect(self,):
        self._connection.close()

    def reconnect(self,):
        if self._connection.closed:
            self._connection = create_engine(self._uri, client_encoding=self._encoding).connect()

    def query(self, sql, **options):
        return pandas.read_sql(text(sql), self._connection, **options)
        
    def execute(self, sql):
        self.logger.info('Executing:' + sql)
        self._connection.execute(text(sql))
        self.logger.info('Done')
