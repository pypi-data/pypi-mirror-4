#
# Copyright John Reid 2008,2009
#


"""
Utility functions for simple logging operations.
"""


import logging, sys, functools


def basic_config(level=logging.INFO):
    """
    Set up simple logging to stderr.
    """
    logging.basicConfig(level=level)


def add_logging_to_file(filename, mode='w'):
    """
    Add logging to named file.
    """
    file_log = logging.FileHandler(filename, mode)
    logging.getLogger('').addHandler(file_log)


def log_to_file_and_stderr(filename, level=logging.INFO, mode='w'):
    """
    Set up simple logging to named file.
    """
    if len(logging.getLogger().handlers) < 2:
        basic_config(level)
        add_logging_to_file(filename, mode)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        for handler in logging.getLogger().handlers:
            handler.setFormatter(formatter)


def log_exception(level=logging.ERROR, logger=None):
    """
    Log the current exception.
    """
    if None == logger:
        logger = logging.getLogger('')
    logger.log(level, '%s: %s', sys.exc_info()[0].__name__, sys.exc_info()[1])



def log_exception_traceback(level=logging.ERROR, logger=None):
    """
    Log the traceback for the current exception.
    """
    import traceback, cStringIO
    tb = cStringIO.StringIO()
    traceback.print_tb(sys.exc_info()[2], file=tb)
    if None == logger:
        logger = logging.getLogger('')
    #logger.log(level, 'Caught exception whilst in function: %s()', fn.__name__)
    logger.log(level, 'Traceback:\n%s', tb.getvalue())


def create_log_exceptions_decorator(level=logging.ERROR, log_traceback=True, logger=None):
    """
    @return: Decorator to log exceptions raised inside a function.
    """
    if None == logger:
        logger = logging.getLogger('')

    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwds):
            try:
                return fn(*args, **kwds)
            except:
                if log_traceback:
                    log_exception_traceback(level, logger)
                log_exception(level, logger)
                raise
        return wrapped

    return decorator


if '__main__' == __name__:
    logging.basicConfig(level=logging.INFO)
    
    class A(object):
        @create_log_exceptions_decorator()
        def method(self):
            raise RuntimeError('error')

    @create_log_exceptions_decorator()
    def exception_raiser():
        "Test exception function."
        raise RuntimeError('Error occurred')

    print 'Fn name: %s' % exception_raiser.__name__
    print 'Fn docstring: %s' % exception_raiser.__doc__
    try:
        exception_raiser()
    except:
        logging.warning('exception_raiser() raised exception')
    try:
        A().method()
    except:
        logging.warning('A().method() raised exception')
