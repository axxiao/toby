

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


class BotError(BaseError):
    def __init__(self, code,error_message):
        BaseError.__init__(self, code, error_message)


class NoAvailableWorker(BaseError):
    """Raised when timeout

        Attributes:
            fun
        """

    def __init__(self, worker=''):
        BaseError.__init__(self, 'NoAvailableWorker', str(worker))


class InvalidToken(BaseError):
    """Raised when timeout

        Attributes:
            fun
        """

    def __init__(self, request={}):
        BaseError.__init__(self, 'InvalidToken', str(request))


class MaxRetryReached(BaseError):
    """Raised when an Max retry reached

    Attributes:
        fun
    """

    def __init__(self, fun_name, retry_times):
        BaseError.__init__(self, 'MAX_RETRY_'+str(retry_times)+fun_name.upper(),
                           'Max retry number reached after tried'+str(retry_times)+' times')
