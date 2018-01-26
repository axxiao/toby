from .log import get_logger


class Connector:
    """
        The common base class for all connectors
    """

    def __init__(self, host='tcp://127.0.0.1', port=12116, logger_name=None):
        """
        The common objects

        :param host: the host name 
        :param port: the port name
        :param logger_name: logger name
        """
        self.host = host
        self.port = port
        self.logger_name = logger_name
        self.logger = get_logger(logger_name)
