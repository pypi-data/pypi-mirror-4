### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Base test classes for sterch.conveyor
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import sterch.queue
import sterch.threading
import zope.component, zope.security
from unittest import TestCase, makeSuite, main
from zope.component.testing import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig 

class TestSetup(PlacelessSetup, TestCase):
    """Test the various zcml configurations"""
    
    def setUp(self):
        super(TestSetup, self).setUp()
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', zope.security)()
        XMLConfig('meta.zcml', sterch.threading)()
        XMLConfig('meta.zcml', sterch.queue)()
        XMLConfig('meta.zcml', sterch.conveyor)()
        XMLConfig('configure.zcml', sterch.threading)()
        XMLConfig('configure.zcml', sterch.queue)()
        XMLConfig('configure.zcml', sterch.conveyor)()