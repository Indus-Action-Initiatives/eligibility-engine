import sys, traceback, datetime
from wsgilog import WsgiLog
from utils.logger import logger

log_file = 'log'

class Log(WsgiLog):
    def __init__(self, application):
        WsgiLog.__init__(
            self,
            application,
            logformat = '%(message)s',
            tofile = True,
            toprint = True,
            file = log_file,
        )

    @staticmethod
    def get_custom_error_message():
        exc_type, exc_value, exc_tb = sys.exc_info()
        stack_summary = traceback.extract_tb(exc_tb)
        end = stack_summary[-1]
        err_type = type(exc_value).__name__
        err_msg = str(exc_value)

        message = "Caught an exception {} in {}.{}[{}]: {}\nThe responsible code is: {}".format(err_type, end.filename, end.name, end.lineno, err_msg, end.line)
        logger.error(message)

