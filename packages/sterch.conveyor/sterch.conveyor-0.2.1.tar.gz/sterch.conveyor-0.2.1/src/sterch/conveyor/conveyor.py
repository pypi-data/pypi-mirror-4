### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Conveyor for the sterch.conveyor package """
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from assistance import LogMixin
from interfaces import IConveyor, IStage
from threading import Thread
from time import sleep 
from zope.cachedescriptors.property import CachedProperty
from zope.interface import implements

class Conveyor(Thread, LogMixin):
    """ Simple IConveyor implementation """
    implements(IConveyor)
    
    def __init__(self, name, stages, delay=5):
        """ delay --- delay in secs. between stages check
            stages --- ordered list of stages to process data """
        Thread.__init__(self)
        self.name = name
        self._delay = delay
        self._stages = [IStage(s) for s in stages]

    @CachedProperty
    def stages(self): return self._stages
    
    @CachedProperty
    def delay(self): return self._delay
    
    def run(self):
        """ main conveyor activity """
        # start all stages
        print "Starting all stages."
        map(lambda s:s.start(), self.stages)
        
        for stage in self.stages:
            # Wait for queue
            while stage.has_tasks():
                print "Waiting for stage %s. %s tasks queued." % (stage.name, stage.tasks_count())
                sleep(self.delay)
            stage.stop()
            print "Stage %s. All tasks were completed." % stage.name
            # wait for  workers
            while not stage.is_finished() :
                print "Stage %s. Waiting for workers. There are %s active workers." % (stage.name, stage.workers_count())
                sleep(self.delay)
            print "Stage %s. All workers were stopped." % stage.name
        print "Done."