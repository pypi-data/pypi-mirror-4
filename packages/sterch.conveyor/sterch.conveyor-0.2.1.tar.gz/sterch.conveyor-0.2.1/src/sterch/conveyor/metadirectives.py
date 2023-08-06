### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

"""ZCML directives interfaces for the ZTK based sterch.conveyor package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from sterch.threading.metadirectives import IName
from zope.interface import Interface, invariant, Invalid
from zope.configuration.fields import GlobalObject
from zope.schema import TextLine, Int, Float
       
class IConveyorDirective(IName):
    """ <conveyor ...>  complex directive interface """
    delay = Float(title=u"Delay to wait stages in queue (sec., 5 by default)", min=0.0, required=False, default=5.0)
    
class IStageBase(IName):
    """ generic stage fields """
    activity = GlobalObject(title=u"Callable object to process tasks on the stage.",
                            constraint=lambda obj:hasattr(obj,'__call__'))
    quantity = Int(title=u"Number of workers for the stage.", min=0, required=True)
    delay = Float(title=u"Delay to wait tasks in queue (sec., 3 by default)", min=0.0, required=False, default=3.0)
    event = TextLine(title=u"IEvent utility name to stop workers.",
                     description=u"""Optional. If not defined event ill be created.
                                   Could be used for other tasks synchronization.""",
                     required=False)
            
class IInQueue(Interface):
    """ Input queue interface """
    in_queue = TextLine(title=u"IQueue utility name to be used as input tasks queue.", required=True) 
    
class IOutQueue(Interface):
    """ Output queue interface """
    out_queue = TextLine(title=u"IQueue utility name to be used as output tasks queue.", required=True)
    
class IInitStageDirective(IStageBase, IOutQueue):
    """ Initial stage. Requires output queue only to put new tasks. """
    
class IFinalStageDirective(IStageBase, IInQueue):
    """ Final stage. Requires input queue only to get tasks. """

class IStageDirective(IStageBase, IInQueue, IOutQueue):
    """ Regular stage. Requires both input and output queues. """      