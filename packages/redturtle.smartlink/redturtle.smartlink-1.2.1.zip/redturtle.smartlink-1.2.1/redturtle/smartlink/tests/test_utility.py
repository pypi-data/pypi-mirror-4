# -*- coding: utf-8 -*-

import unittest
from zope.component import getUtility

from redturtle.smartlink.tests.base import TestCase
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig, ILinkNormalizerUtility

class BasicTestSetup(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.setRoles(('Manager', ))
        self.utility = getUtility(ILinkNormalizerUtility)
        self.smartlink_config = getUtility(ISmartlinkConfig, name="smartlink_config")
    
    def test_nonASCIILink(self):
        # See http://plone.org/products/smart-link/issues/8/view
        self.smartlink_config.backendlink.append(u'http://nohost/plone')
        self.smartlink_config.frontendlink.append(u'http://nohost')
        self.assertEqual(self.utility.toFrontEnd('http://myhost.com/sostenibilit\xc3\xa0.pdf'),
                         'http://myhost.com/sostenibilit\xc3\xa0.pdf')
        self.smartlink_config.backendlink = []
        self.smartlink_config.frontendlink = []
        self.smartlink_config.frontend_main_link = u'http://nohost/plone'
        self.assertEqual(self.utility.toFrontEnd('http://myhost.com/sostenibilit\xc3\xa0.pdf'),
                         'http://myhost.com/sostenibilit\xc3\xa0.pdf')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestSetup))
    return suite