### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" data processing stage
"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from assistance import InQueueMixin
from group import Group
from interfaces import IGroup, IRegularStage, IFirstStage, ILastStage
from zope.interface import implements
from zope.component import getUtility
from zope.component.interfaces import IFactory

class StageBase(object):
    """ Base data processing stage.
        This class DOES NOT implemet IStage.
        There is no way to implement has_tasks
    """
        
    def __init__(self, name, group):
        """  
            name --- stage name
            group --- worker's group
        """
        self._name = name
        self.group = group   
               
    @property
    def name(self):
        """ name must be read only according to IStage """
        return self._name
    
    def start(self):
        """ Start stage """
        self.group.start()
        
    def stop(self):
        """ Tries to stop stage """
        self.group.stop()
        
    def is_finished(self):
        """ Checks does group of workers finish its activity """
        self.group.filter_dead_workers()
        return len(self.group) == 0
    
    def has_tasks(self):
        """ Must be implemented in descendants """
        raise NotImplementedError("Not implemented yet.")
    
    def tasks_count(self):
        """ Must be implemented in descendants """
        raise NotImplementedError("Not implemented yet.")
    
    def workers_count(self):
       return self.group.live_count() 
    
class FirstStage(StageBase):
    """ First data processing stage. 
        Initial tasks generation.
    """
    implements(IFirstStage)
    
    def __init__(self, name, quantity, out_queue, event, delay, activity):
        """ 
            name --- stage name
            quantity --- number of workers to process stage
            out_queue --- queue to put tasks
            event --- event to stop all workers
            delay --- processing delay
            activity --- callable represents stage activity 
        """
        w_factory = getUtility(IFactory, name="sterch.conveyor.FirstWorker") 
        g_factory = getUtility(IFactory, name="sterch.conveyor.Group")
        w_args = (out_queue, event, delay, activity)
        group = g_factory(quantity, w_factory, *w_args)
        StageBase.__init__(self, name, group)
        
    def has_tasks(self):
        """ Initial stage has no unfinished tasks."""
        return False
    
    def tasks_count(self):
        """ Initial stage has no unfinished tasks."""
        return 0
    
class LastStage(InQueueMixin, StageBase):
    """ Last data processing stage. 
        Results generation.
    """
    implements(ILastStage)
    
    def __init__(self, name, quantity, in_queue, event, delay, activity):
        """ 
            name --- stage name
            quantity --- number of workers to process stage
            in_queue --- queue to get tasks
            event --- event to stop all workers
            delay --- processing delay
            activity --- callable represents stage activity 
        """
        self._in_queue = in_queue
        w_factory = getUtility(IFactory, name="sterch.conveyor.LastWorker") 
        g_factory = getUtility(IFactory, name="sterch.conveyor.Group")
        w_args = (in_queue, event, delay, activity)
        group = g_factory(quantity, w_factory, *w_args)
        StageBase.__init__(self, name, group)

class RegularStage(InQueueMixin, StageBase):
    """ Regular data processing stage. 
        Take tasks from input queue and put next tasks to output queue.
    """
    implements(IRegularStage)
    def __init__(self, name, quantity, in_queue, out_queue, event, delay, activity):
        """ 
            name --- stage name
            quantity --- number of workers to process stage
            in_queue --- queue to get tasks
            out_queue --- queue to put next tasks
            event --- event to stop all workers
            delay --- processing delay
            activity --- callable represents stage activity 
        """
        self._in_queue = in_queue
        w_factory = getUtility(IFactory, name="sterch.conveyor.RegularWorker") 
        g_factory = getUtility(IFactory, name="sterch.conveyor.Group")
        w_args = (in_queue, out_queue, event, delay, activity)
        group = g_factory(quantity, w_factory, *w_args)
        StageBase.__init__(self, name, group)