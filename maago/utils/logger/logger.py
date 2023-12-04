import datetime

def log(log_type='INFO', message=''):
    ct = datetime.datetime.now()
    print("[%s] [%s]: %s" % (log_type, ct, message))

def debug(s):
    log('DEBUG', s)

def info(s):
    log('INFO', s)

def error(s):
    log('ERROR', s)

def warn(s):
    log('WARNING', s)