### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Base test classes for sterch.conveyor
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import zcml

from setup import TestSetup
from unittest import TestCase, makeSuite, main
from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.exceptions import ConfigurationError

class Test(TestSetup):
    """Test the various zcml configurations"""
    
    def test_loop(self):
        self.assertRaises(ConfigurationError, XMLConfig, *('loop.zcml', zcml)) 

    def test_simple_loop(self):
        self.assertRaises(ConfigurationError, XMLConfig, *('simple_loop.zcml', zcml)) 
        
    def test_no_init_stage(self):
        self.assertRaises(ConfigurationError, XMLConfig, *('no_init_stage.zcml', zcml)) 
                
    def test_no_final_stage(self):
        self.assertRaises(ConfigurationError, XMLConfig, *('no_final_stage.zcml', zcml)) 
        
    def test_final_stage_unreachable(self):
        self.assertRaises(ConfigurationError, XMLConfig, *('final_stage_unreachable.zcml', zcml)) 
        
    def test_dummy_stages(self):
        self.assertRaises(ConfigurationError, XMLConfig,* ('dummy_stages.zcml', zcml)) 

def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')        