import logging
import itertools
import functools
import threading

from .py3compat import Queue


def func_call_as_str(name, *args, **kwds):
    """
    Return arguments and keyword arguments as formatted string

    >>> func_call_as_str('f', 1, 2, a=1)
    'f(1, 2, a=1)'

    """
    return '{0}({1})'.format(
        name,
        ', '.join(itertools.chain(
            map('{0!r}'.format, args),
            map('{0[0]!s}={0[1]!r}'.format, sorted(kwds.items())))))


def autolog(level):
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    def wrapper(method):
        @functools.wraps(method)
        def new_method(self, *args, **kwds):
            funcname = ".".join([self.__class__.__name__, method.__name__])
            self.logger.log(level, "(AutoLog) Called: %s",
                            func_call_as_str(funcname, *args, **kwds))
            ret = method(self, *args, **kwds)
            self.logger.log(level, "(AutoLog) Returns: %s(...) = %r",
                            funcname, ret)
            return ret
        return new_method
    return wrapper


def newname(template):
    global _counter
    _counter = _counter + 1
    return template.format(_counter)
_counter = 0


def newthread(template="EPCThread-{0}", **kwds):
    """
    Instantiate :class:`threading.Thread` with an appropriate name.
    """
    if not isinstance(template, str):
        template = '{0}.{1}-{{0}}'.format(template.__module__,
                                          template.__class__.__name__)
    return threading.Thread(
        name=newname(template), **kwds)


class ThreadedIterator(object):

    def __init__(self, iterable):
        self._original_iterable = iterable
        self.queue = Queue.Queue()
        self.thread = newthread(self, target=self._target)
        self.thread.daemon = True
        self._sentinel = object()
        self.thread.start()

    def _target(self):
        for result in self._original_iterable:
            self.queue.put(result)
        self.stop()

    def stop(self):
        self.queue.put(self._sentinel)

    def __iter__(self):
        return self

    def __next__(self):
        got = self.queue.get()
        if got is self._sentinel:
            raise StopIteration
        return got
    next = __next__  # for PY2


def callwith(context_manager):
    """
    A decorator to wrap execution of function with a context manager.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            with context_manager:
                return func(*args, **kwds)
        return wrapper
    return decorator


def _define_thread_safe_methods(methodnames, lockname):
    def define(cls, name):
        def wrapper(self, *args, **kwds):
            with getattr(self, lockname):
                return method(self, *args, **kwds)
        method = getattr(cls, name)
        setattr(cls, name, wrapper)

    def decorator(cls):
        for name in methodnames:
            define(cls, name)
        return cls
    return decorator


@_define_thread_safe_methods(
    ['__getitem__', '__setitem__', '__delitem__', 'pop'], '_lock')
class LockingDict(dict):

    def __init__(self, *args, **kwds):
        super(LockingDict, self).__init__(*args, **kwds)
        self._lock = threading.Lock()
