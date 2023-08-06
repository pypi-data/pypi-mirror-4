### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Workers for sterch.conveyor package """

__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

import sys
import traceback
import types

from assistance import InQueueMixin, OutQueueMixin, EventMixin, LogMixin
from interfaces import IFirstWorker, ILastWorker, IRegularWorker
from Queue import Empty, Full
from threading import Thread
from time import sleep
from zope.component import getUtility
from zope.interface import implements

class FirstWorker(EventMixin, 
                  OutQueueMixin, 
                  LogMixin,
                  Thread):
    """ Initial worker """
    implements(IFirstWorker)
    
    def __init__(self, out_queue, event, delay, activity=None): 
        """    out_queue --- either object that provides IQueue or IQueue utility name
               event     --- either object that provides IEvent or IEvent utility name 
               delay     --- delay between activity cycles
               activity --- callable represents worker activity
        """
        Thread.__init__(self)
        self.daemon = True
        self._out_queue = out_queue
        self.delay = delay
        self._event = event
        if activity:
            self.activity = activity
                
    def activity(self):
        raise NotImplementedError("Must be defined")
    
    def run(self):
        """ Worker's workcycle """
        if self.event.isSet(): return
        try:
            all_tasks = self.activity()
            if all_tasks is not None:
                if not hasattr(all_tasks, '__iter__'):
                    raise ValueError("Activity result must be iterable or None")
                for task in all_tasks:
                    while True:
                        try:
                            self.out_queue.put(task, timeout=self.delay)
                            break
                        except Full, ex:
                            pass
        except Exception, ex:
            self.traceback(ex)

class LastWorker(EventMixin, 
                 InQueueMixin,
                 LogMixin,
                 Thread):
    """ Last worker """
    implements(ILastWorker)
    
    def __init__(self, in_queue, event, delay, activity=None): 
        """    in_queue --- either object that provides IQueue or IQueue utility name
               event     --- either object that provides IEvent or IEvent utility name 
               delay     --- delay between activity cycles
               activity --- callable represents worker activity
        """
        Thread.__init__(self)
        self.daemon = True
        self._in_queue = in_queue
        self.delay = delay
        self._event = event
        if activity:  self.activity = activity
    
    def activity(self):
        raise NotImplementedError("Must be defined")
    
    def run(self):
        """ Worker's workcycle """
        while True:
            if self.event.isSet(): return
            try:
                try:
                    task = self.in_queue.get(timeout=self.delay)
                    self.activity(task)                        
                except Empty, ex:
                    pass
            except Exception, ex:
                # Thread must stop if and only if event is set
                self.traceback(ex)


class Worker(EventMixin, 
             InQueueMixin,
             OutQueueMixin,
             LogMixin,
             Thread):
    """ Regular worker to process elements from input queue to output queue.
        Could be stopped be setting event. 
    """
    implements(IRegularWorker)
    
    def __init__(self, in_queue, out_queue, event, delay, activity=None):
        """ 
            in_queue --- input queue
            out_queue --- output queue
            timeout --- time to wait in inqueue is empty and check evtAllDone
            event --- event to stop thread activity
            activity --- callable represents worker activity. Must accept only one argument --- item.
                        Returned value will be placed to out_queue if not None.
        """
        Thread.__init__(self)
        self.daemon = True
        self._in_queue = in_queue
        self._out_queue = out_queue
        self.delay = delay
        self._event = event
        self.activity = activity
        if activity: self.activity = activity
        
    def activity(self, item):
        raise NotImplementedError("Must be implemented")
    
    def run(self):
        """ Worker cycle """
        while True:
            if self.event.isSet(): return
            try:
                try:
                    task = self.in_queue.get(timeout=self.delay)
                    all_tasks = self.activity(task)
                    if all_tasks is not None:
                        if not hasattr(all_tasks, '__iter__'):
                            raise ValueError("Activity result must be iterable or None")
                        for new_task in all_tasks:
                            while True:
                                try:
                                    self.out_queue.put(new_task, timeout=self.delay)
                                    break
                                except Full, ex:
                                    pass
                except Empty, ex:
                    pass
            except Exception, ex:
                # Thread must stop if and only if event is set
                self.traceback(ex)
                
RegularWorker = Worker