### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

"""Metadirectives implementations for the ZTK based sterch.threading package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL" 

from interfaces import IConveyor, IFirstWorker, ILastWorker, IRegularWorker
from zope.component import createObject, getUtility
from zope.component.interfaces import IFactory 
from zope.component.zcml import handler
from zope.configuration.exceptions import ConfigurationError

class ConveyorDirective(object):
    """ Conveyor directive handler """
    
    def __init__(self, _context, name=None, delay=5.0):
        self._context = _context
        self.name = name
        self.delay = delay
        self.init_stage_vars = False
        self.final_stage_vars = False
        self.stages = []
        self.all_in_queues = []
        
    def init_stage(self, _context, **kwargs):
        """ init_stage subdirective processing """
        kwargs['event'] = kwargs['event'] if kwargs.get('event') else createObject('threading.Event')
        kwargs['delay'] = kwargs['delay'] if kwargs.get('delay') else 0
        self.init_stage_vars = kwargs
        
        
    def final_stage(self, _context, **kwargs):
        """ final_stage subdirective processing """
        kwargs['event'] = kwargs['event'] if kwargs.get('event') else createObject('threading.Event')
        kwargs['delay'] = kwargs['delay'] if kwargs.get('delay') else 0
        self.final_stage_vars = kwargs
        self.all_in_queues.append(kwargs['in_queue'])
        
    def stage(self, _context, **kwargs):
        """ stage subdirective procesing """
        kwargs['event'] = kwargs['event'] if kwargs.get('event') else createObject('threading.Event')
        kwargs['delay'] = kwargs['delay'] if kwargs.get('delay') else 0
        self.stages.append(kwargs)
        self.all_in_queues.append(kwargs['in_queue'])
        
    def __call__(self):
        """ whole directive processing  """
        if not self.init_stage_vars: raise ConfigurationError(u"No initial stage defined")
        if not self.final_stage_vars: raise ConfigurationError(u"No final stage defined")
        # trying to build conveyor chain
        ordered_stages = [self.init_stage_vars]
        curq = self.init_stage_vars['out_queue']
        in_queues = []
        out_queues = [curq]
        while self.stages:
            if curq not in self.all_in_queues: raise ConfigurationError(u"Output queue %s is never used as input" % curq)
            s = self.stages.pop()
            if s['in_queue'] in in_queues: raise ConfigurationError(u"Input queue could be used only in one stage.")
            if s['out_queue'] in out_queues: raise ConfigurationError(u"Output queue could be used only in one stage.")
            if s['in_queue'] in in_queues: raise ConfigurationError(u"Input queue could be used only in one stage.")
            if s['out_queue'] in out_queues: raise ConfigurationError(u"Output queue could be used only in one stage.")
            if s.get('marker') == curq : raise ConfigurationError("Final stage unreachable")
            if s['in_queue'] == curq:
                ordered_stages.append(s)
                curq = s['out_queue']
                in_queues.append(s['in_queue'])
                out_queues.append(s['out_queue'])
            else:
                s['marker'] = curq
                self.stages = [s,] + self.stages
        if self.stages: raise ConfigurationError(u"There are dummy stages within the conveyor")
        if ordered_stages[-1]['out_queue'] != self.final_stage_vars['in_queue']:
            raise ConfigurationError(u"Conveyor must be finished with final_stage.")            
        ordered_stages.append(self.final_stage_vars)
        # removing markers
        for s in ordered_stages: 
            if 'marker' in s: del s['marker']
        # constructing the conveyor
        __stages = []
        # 1st stage
        s = ordered_stages[0]
        __stages.append(createObject('sterch.conveyor.FirstStage', **s))
        # middle stages
        for s in ordered_stages[1:-1]:
            __stages.append(createObject('sterch.conveyor.RegularStage', **s))
        #last stage
        s = ordered_stages[-1]
        __stages.append(createObject('sterch.conveyor.LastStage', **s))
        conveyor = createObject('sterch.conveyor.Conveyor', self.name, __stages, delay=self.delay)
        self._context.action(
            discriminator = ('utility', IConveyor, self.name),
            callable = handler,
            args = ('registerUtility', conveyor, IConveyor, self.name)
        )