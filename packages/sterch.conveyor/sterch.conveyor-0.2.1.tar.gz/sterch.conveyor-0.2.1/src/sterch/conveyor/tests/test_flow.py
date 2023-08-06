### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Tests for IP address field
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import zcml

from activities import get_jobs_counter, reset_jobs, gl_N, get_results
try:
    from queue import Empty
except ImportError:
    from Queue import Empty
from setup import TestSetup
from sterch.conveyor.interfaces import IConveyor
from sterch.threading.interfaces import IEvent
from unittest import TestCase, makeSuite, main
from zope.component import queryUtility, getUtility, getUtilitiesFor
from zope.configuration.xmlconfig import XMLConfig

EXECUTION_TIME_LIMIT = 60

class Test(TestSetup):
    """Test the various zcml configurations"""
    
    def _clear_events(self):
        map(lambda n,e:e.clear(), getUtilitiesFor(IEvent))
    
    def _check_valid_config(self, config, uname, task_field='result'):
        XMLConfig(config, zcml)()
        c = queryUtility(IConveyor, name=uname)
        self.assertTrue(c is not None)
        reset_jobs()
        c.start()
        c.join(EXECUTION_TIME_LIMIT)
        self.assertFalse(c.isAlive())
        q = get_results()
        self.assertEqual(q.qsize(), gl_N)
        self.assertEqual(get_jobs_counter(), gl_N)
        try:
            while True:
                task = q.get(False)
                self.assertEqual(task['value'], task[task_field])
        except Empty:
            pass
 
    def test_correct_zcml_no_events(self):
        self._check_valid_config('valid_no_events.zcml', u"Test #1")

    def test_correct_zcml_with_events(self):
        self._clear_events()
        self._check_valid_config('valid_with_events.zcml', u"Test #2")
        # check events
        for name, event in getUtilitiesFor(IEvent):
            self.assertTrue(event.isSet())
            
    def test_2stages_only_no_events(self):
        self._check_valid_config('valid_2stages_no_events.zcml', u"Test #3", task_field='value')
    
    def test_2stages_only_with_events(self):
        self._clear_events()
        self._check_valid_config('valid_2stages_with_events.zcml', u"Test #4", task_field='value')
        for name in (u'Event #1', u'Event #2',):
            self.assertTrue(getUtility(IEvent, name=name).isSet())
        
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')