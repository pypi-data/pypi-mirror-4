# jsb/tasks.py
#
#

## jsb imports 

from ggz.utils.trace import calledfrom
from ggz.lib.plugins import plugs

## basic imports

import logging
import sys

## TaskManager class

class TaskManager(object):

    def __init__(self):
        self.handlers = {}
        self.plugins = {}

    def size(self): return len(self.handlers)

    def add(self, taskname, func):
        """ add a task. """
        logging.debug("tasks - added task %s - %s" % (taskname, func))
        self.handlers[taskname] = func
        plugin = self.plugins[taskname] = calledfrom(sys._getframe())
        plugs.load_mod(plugin)
        return True

    def unload(self, taskname):
        """ unload a task. """
        logging.debug("tasks - unloading task %s" % taskname)
        try:
            del self.handlers[taskname]
            del self.plugins[taskname]
            return True
        except KeyError: return False

    def dispatch(self, taskname, *args, **kwargs):
        """ dispatch a task. """
        try: plugin = self.plugins[taskname]
        except KeyError:
            logging.debug('tasks - no plugin for %s found' % taskname)
            return
        logging.debug('loading %s for taskmanager' % plugin)
        #plugs.load(plugin)
        try: handler = self.handlers[taskname]
        except KeyError:
            logging.debug('tasks - no handler for %s found' % taskname)
            return
        logging.warn("dispatching task %s - %s" % (taskname, str(handler)))
        return handler(*args, **kwargs)

## global task manager

taskmanager = TaskManager()
