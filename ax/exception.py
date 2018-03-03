

class BaseError(Exception):
    """Exception Base Class

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, code, message):
        self.expression = code
        self.message = message


class Timeout(BaseError):
    """Raised when timeout

        Attributes:
            fun
        """

    def __init__(self, desc=''):
        BaseError.__init__(self, 'TIMEOUT',desc)


class MaxRetryReached(BaseError):
    """Raised when an Max retry reached

    Attributes:
        fun
    """

    def __init__(self, fun_name, retry_times):
        BaseError.__init__(self, 'MAX_RETRY_'+str(retry_times)+fun_name.upper(),
                           'Max retry number reached after tried'+str(retry_times)+' times')
