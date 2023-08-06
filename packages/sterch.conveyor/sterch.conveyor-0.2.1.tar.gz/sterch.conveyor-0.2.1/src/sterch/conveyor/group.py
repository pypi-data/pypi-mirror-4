### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Worker's group
"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"


from interfaces import IGroup, IWorker
from sterch.threading.interfaces import IThread
from threading import Lock 
from UserList import UserList
from zope.interface import implements 

class Group(UserList):
    """ Thread-safe group of workers """

    def __init__(self, qty, factory, *args, **kwargs):
        """ Creates group of workers to make similar work.
            qty --- number of workers
            factory --- workers' factory
            *args, **kwargs --- args for an factory
        """
        super(Group, self).__init__()
        for i in xrange(0,qty):
            # this will guarantee that all list elements are workers
            self.append(IWorker(factory(*args, **kwargs)))
        self.locked = Lock()
    
    def start(self):
        """ start all workers """
        with self.locked:
            map(lambda t:IThread(t).start(), self)
    
    def stop(self):
        """ Fire event to stop all workers """
        with self.locked:
            map(lambda t:IWorker(t).event.set(), self)
            
    def is_finished(self):
        """ Check workers to be stopped """
        return self.live_count() == 0
    
    def filter_dead_workers(self):
        """ remove dead workers from the group """
        with self.locked:
            self.data = filter(lambda t: IThread(t).isAlive(), self)
    
    def live_count(self):
        """ returns number of live workers """
        with self.locked:
            return len(filter(lambda t: IThread(t).isAlive(), self))