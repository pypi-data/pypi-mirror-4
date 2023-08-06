# -*- coding: utf-8 -*-

import unittest
from zope.component import getUtility

from redturtle.smartlink.tests.base import TestCase
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig, ILinkNormalizerUtility

class TextViewFixFakeInternalLinks(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.setRoles(('Manager', ))
        self.utility = getUtility(ILinkNormalizerUtility)
        self.smartlink_config = getUtility(ISmartlinkConfig, name="smartlink_config")
        self.smartlink_config.backendlink.append(u'http://nohost/plone')
        self.smartlink_config.frontendlink.append(u'http://nohost')
        self.view = self.portal.restrictedTraverse('@@fix-fake-internal-links')
        self.folder.invokeFactory(type_name='Link', id='the-link', title='Link to something')
        link = self.folder['the-link']
        self.link = link
        self.folder.invokeFactory(type_name='Document', id='internal-document', title='Internal doc')
        self.doc = self.folder['internal-document']
    
    def test_findInternalLinksWithAbsoluteURL(self):
        self.assertEqual(self.view.findInternalByURL(self.doc.absolute_url()).absolute_url(),
                         self.doc.absolute_url())

    def test_findInternalLinksWithUID(self):
        self.assertEqual(self.view.findInternalByURL("resolveuid/%s" % self.doc.UID()).absolute_url(),
                         self.doc.absolute_url())
        self.assertEqual(self.view.findInternalByURL("/resolveuid/%s" % self.doc.UID()).absolute_url(),
                         self.doc.absolute_url())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TextViewFixFakeInternalLinks))
    return suite