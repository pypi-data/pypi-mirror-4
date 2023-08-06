from __future__ import absolute_import
import sys
import logging
from time import time
from types import MethodType
from datetime import datetime

from kuyruk import importer
from kuyruk.queue import Queue
from kuyruk.channel import LazyChannel
from kuyruk.eventmixin import EventMixin

logger = logging.getLogger(__name__)


def profile(f):
    def inner(self, *args, **kwargs):
        start = time()
        result = f(self, *args, **kwargs)
        end = time()
        logger.info("%r finished in %i seconds." % (self, end - start))
        return result
    return inner


class Task(EventMixin):

    def __init__(self, f, kuyruk, queue='kuyruk',
                 local=False, eager=False, retry=0):
        super(Task, self).__init__()
        self.f = f
        self.kuyruk = kuyruk
        self.queue = queue
        self.local = local
        self.eager = eager
        self.retry = retry
        self.cls = None

    def __repr__(self):
        return "<Task of %r>" % self.name

    def __call__(self, *args, **kwargs):
        if self.eager or self.kuyruk.config.EAGER:
            self.run(args, kwargs)
        else:
            self.send_to_queue(args, kwargs)

        return TaskResult(self)

    def __get__(self, obj, objtype):
        """If the task is accessed from an instance via attribute syntax
        return a function for sending the task to queue, otherwise
        return the task itself.

        This is done for allowing a method to be converted to task without
        modifying the client code. When a function decorated inside a class
        there is no way of accessing that class at that time because methods
        are bounded at run time when they are accessed. The trick here is that
        we set self.cls when the Task is accessed first time via attribute
        syntax.

        """
        self.cls = objtype
        if obj:
            return MethodType(self.__call__, obj, objtype)
        return self

    def send_to_queue(self, args=(), kwargs={}):
        """
        Send this task to queue

        :param args: Arguments that will be passed to task on execution
        :param kwargs: Keyword arguments that will be passed to task on execution
        :return: None

        """
        task_description = {
            'module': self.module_name,
            'function': self.f.__name__,
            'class': self.class_name,
            'object_id': args[0].id if self.cls else None,
            'args': args[1:] if self.cls else args,
            'kwargs': kwargs,
            'timestamp': str(datetime.utcnow())
        }
        if self.retry:
            task_description['retry'] = self.retry

        channel = LazyChannel(
            self.kuyruk.config.RABBIT_HOST, self.kuyruk.config.RABBIT_PORT,
            self.kuyruk.config.RABBIT_USER, self.kuyruk.config.RABBIT_PASSWORD)
        with channel:
            queue = Queue(self.queue, channel, self.local)
            queue.send(task_description)

    @profile
    def run(self, args, kwargs):
        """Run the wrapped function and event handlers."""
        def run(functions, **extra):
            for f in functions:
                f(self, args, kwargs, **extra)

        try:
            run(self.kuyruk.before_task_functions)
            run(self.before_task_functions)
            return_value = self.f(*args, **kwargs)  # call wrapped function
        except Exception:
            exc_info = sys.exc_info()
            run(self.on_exception_functions, exc_info=exc_info)
            run(self.kuyruk.on_exception_functions, exc_info=exc_info)
            raise
        else:
            run(self.after_return_functions, return_value=return_value)
            run(self.kuyruk.after_return_functions, return_value=return_value)
        finally:
            run(self.after_task_functions)
            run(self.kuyruk.after_task_functions)

    @property
    def name(self):
        if self.class_name:
            return "%s:%s.%s" % (self.module_name, self.class_name,
                                 self.f.__name__)
        else:
            return "%s:%s" % (self.module_name, self.f.__name__)

    @property
    def module_name(self):
        name = self.f.__module__
        if name == '__main__':
            name = importer.get_main_module().name
        return name

    @property
    def class_name(self):
        if self.cls:
            return self.cls.__name__


class TaskResult(object):

    def __init__(self, task):
        self.task = task

    def __getattr__(self, item):
        raise Exception(item)

    def __getitem__(self, item):
        raise Exception(item)

    def __setitem__(self, key, value):
        raise Exception(key, value)

    def __repr__(self):
        return "<TaskResult of %r>" % self.task.name

    def __str__(self):
        return self.__repr__()
