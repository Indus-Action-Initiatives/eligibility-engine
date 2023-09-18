import functools
from middleware.logger import Log


def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            response = Log.get_custom_error_message()
            print(response)
            if (hasattr(f, 'callback')):
                f.callback()
            else:
                print('No callback in {}'.format(f.__name__))
            return response
    return func

class ErrorCatcher(type):
    def __new__(cls, name, bases, dct):
        for m in dct:
            if hasattr(dct[m], '__call__'):
                dct[m] = catch_exception(dct[m])
        return type.__new__(cls, name, bases, dct)