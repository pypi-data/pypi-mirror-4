#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Thread idioms

A  collection of common pattern used to run code asyncronously
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"
__credits__ = ["Joaquim Rocha <jrocha@igalia.com>", ]

# Import Here any required modules for this module.
from Queue import Queue
from atexit import register
from threading import Thread, Lock, Condition
from time import sleep

__all__ = ['Worker', 'ThreadPool', 'Task', 'TaskException', ]

from .log import log
from .callback import Callback
from .singleton import Singleton


class TaskError(Exception):
    """An exception related to Task errors"""


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, queue):
        Thread.__init__(self)
        self.daemon = True
        self._queue = queue
        self._task  = None
        self.totals = -1
        # start thread
        self.start()

    def __getattr__(self, name):
        return getattr(self._queue, name)

    def run(self):
        """Set worker to start to accept tasks"""
        while True:
            try:
                self._task = self._queue.get()[1]
                self._task.run()
                self.totals += 1
            except Exception:
                self.stop()
                raise
            finally:
                self._task = None
                self._queue.task_done()

    def stop(self):
        """Cancel current task execution"""
        if self._task is not None:
            self._task.cancel()


class ThreadPool(Singleton):
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads=3):
        def __get_cpus():
            """Detects the number of CPUs on a system"""
            import os
            if not hasattr(os, "sysconf"):
                if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
                    # Linux & Unix:
                    return int(os.sysconf("SC_NPROCESSORS_ONLN"))
                else:  # OSX
                    return int(os.popen2("sysctl -n hw.ncpu")[1].read())
            return 1

        self._tasks = PriorityQueue(max(__get_cpus(), 3, num_threads))
        self._workers = [Worker(self._tasks)  for _ in range(num_threads)]
        # HACK. Sleep application to raise any last-minute exceptions
        register(lambda: sleep(0.01))

        super(ThreadPool, self).__init__()

    def add_task(self, task, priority=99):
        """Add a task to the queue"""
        self._tasks.put((priority, task,))

    def wait_all(self):
        """Wait for completion of all the tasks in the queue"""
        self._tasks.join()

    @property
    def workers(self):
        """Returs a list of workers defined in the ThreadPool"""
        return self._workers


class Task(object):
    """A Wrapper for a method code that must be called in background"""

    def __init__(self, func, cancellable=True):
        self._cbs = {
            'errback'   : [],
            'callback'  : [],
            'inprogress': [],
            'cleanup'   : [],
            }
        self._func        = func
        self._finished    = False
        self._canceled    = False
        self._cancellable = cancellable

        # wait stuff
        self._tdone = Condition(Lock())

    def __getattr__(self, name):
        try:
            opr, cb_type = name.split('_')[:2]
            # pylint: disable-msg=W0108
            if cb_type in self._cbs:
                if opr in ('prepend',):
                    return lambda x: self._cbs[cb_type].insert(0, Callback(x))
                if opr in ('append', 'register', ' connect'):
                    return lambda x: self._cbs[cb_type].append(Callback(x))
                if opr in ('remove', 'unregister', 'disconnect'):
                    return lambda x: self._cbs[cb_type].remove(Callback(x))
        except (ValueError, IndexError):
            pass
        raise AttributeError(
            "'%s' instance has no attribute '%s'" %
            (self.__class__.__name__, name))

    def run(self):
        """Execute task"""

        # pylint:disable-msg=R0903
        class TaskWrapper(object):
            """Wrapper around tasks"""

            def __init__(self, wrapper):
                self.__wrapper = wrapper

            def __getitem__(self, value):
                return self.kwargs[value]

            def __setattr__(self, name, value):
                if name in ('canceled', 'finished',):
                    self.__wrapper.__dict__['_' + name] = value
                super(TaskWrapper, self).__setattr__(name, value)

            def __getattr__(self, name):
                if hasattr(self, 'kwargs'):
                    return self.kwargs.get(name)
                raise AttributeError(
                    "'%s' instance has no attribute '%s'" %
                    (self.__class__.__name__, name))

        with self._tdone:
            results = None
            wrapper = TaskWrapper(self)
            callbacks = iter(self._cbs['callback'])
            failbacks = iter(self._cbs['errback'])
            try:
                while True:
                    try:
                        while self.is_running():
                            # run main task
                            # pylint: disable-msg=W0201
                            wrapper.finished = True
                            results = self._func(wrapper)
                            log.core.debug(results)
                            # if not finished yet, run inprogress callbacks
                            if self.is_running():
                                for handler in self._cbs['inprogress']:
                                    results = handler(results, wrapper)
                        # run now. Use an iter so callbacks are
                        # executed just ONE time
                        for handler in callbacks:
                            results = handler(results, wrapper)
                        # all ok. Exit loop
                        break
                    #pylint: disable-msg=W0703
                    except Exception, ex:
                        # Process fails. Only allow one execution for
                        # each callback
                        for failback in failbacks:
                            if failback(ex, wrapper):
                                break
                        else:
                            # if fails to process exception in errbacks, then
                            # propagate error
                            raise
                # run cleanups
                for cleanup in self._cbs['cleanup']:
                    cleanup(wrapper)
            finally:
                # An exception may arise on cleanups (RARE). Just let
                # thread in a consistent state
                self._tdone.notify_all()

    def start(self, pool=None):
        """
        Puts task into ThreadPool tot be executed when a tread in available
        """
        pool = pool or ThreadPool.get_instance()
        pool.add_task(self)

    def finish(self):
        """Flag to indicate that this task has finished"""
        self._finished = True

    def is_finished(self):
        """Check if task wa is finished"""
        return self._finished

    def is_running(self):
        """Check if current task is still running"""
        return not self._finished and not self._canceled

    def cancel(self):
        """Flag to indicate that this task execution has been cancelled"""
        if self._canceled:
            raise TaskError("Unable to cancel an already canceled task")
        if not self._cancellable:
            raise TaskError("Unable to cancel an uncacellable task")
        self._canceled = True

    def is_cancelled(self):
        """Check if task was cancelled"""
        return self._canceled

    def is_cancellable(self):
        """Check if task is cancellable"""
        return self._cancellable

    def register_all(self, **kwargs):
        """Sugar method to register all callbacks in just one call"""
        for detail, callbacks in kwargs.iteritems():
            for callback in callbacks:
                getattr(self, 'register_' + detail)(callback)

    def wait(self, remain=None):
        """Wait for task to """
        self._tdone.acquire()
        while self.is_running():
            self._tdone.wait(remain)
        self._tdone.release()


#pylint: disable-msg=W0622,W0221
class PriorityQueue(Queue):
    """
    Variant of Queue that retrieves open entries in priority order
    (lowest first).  Entries are typically tuples of the form:
    (priority number, data).
    """
    import heapq

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item, heappush=heapq.heappush):
        heappush(self.queue, item)

    def _get(self, heappop=heapq.heappop):
        return heappop(self.queue)
