import functools, web
from middleware.logger import Log
from utils.logger import logger


def catch_exception(f):
    # Temporary solution.
    # Does not feel scalable.
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            response = Log.get_custom_error_message()
            logger.error(response)
            if (hasattr(f, 'callback')):
                f.callback()
            else:
                logger.error('No callback in {}'.format(f.__name__))
            if 'JSONDecodeError' == e.__class__.__name__:
                return web.BadRequest(message=response)
            return web.InternalError(message=response)
    return func

class ErrorCatcher(type):
    def __new__(cls, name, bases, dct):
        for m in dct:
            if hasattr(dct[m], '__call__'):
                dct[m] = catch_exception(dct[m])
        return type.__new__(cls, name, bases, dct)