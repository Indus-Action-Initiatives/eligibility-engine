import functools
import web
import datetime;

DEBUG = True

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            ct = datetime.datetime.now()
            response = "{}: Caught an exception in {} : {}".format(ct, f.__qualname__, str(e))
            print(response)
            if DEBUG:
                return web.debugerror()
            return response
            
    return func

class ErrorCatcher(type):
    def __new__(cls, name, bases, dct):
        for m in dct:
            if hasattr(dct[m], '__call__'):
                dct[m] = catch_exception(dct[m])
        return type.__new__(cls, name, bases, dct)