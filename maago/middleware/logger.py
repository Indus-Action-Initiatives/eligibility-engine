import sys, logging
from wsgilog import WsgiLog

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