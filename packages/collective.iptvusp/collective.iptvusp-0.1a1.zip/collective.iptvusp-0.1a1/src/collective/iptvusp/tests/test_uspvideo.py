# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation

from iptv.uspvideo import IUSPVideo
from collective.iptvusp.testing import INTEGRATION_TESTING


class CoverIntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('iptv.uspvideo', 'c1',
                                  template_layout='Layout A')
        self.c1 = self.folder['c1']

    def test_adding(self):
        self.assertTrue(IUSPVideo.providedBy(self.c1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='iptv.uspvideo')
        self.assertNotEqual(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='iptv.uspvideo')
        schema = fti.lookupSchema()
        self.assertEqual(IUSPVideo, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='iptv.uspvideo')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IUSPVideo.providedBy(new_object))

    def test_exclude_from_navigation_behavior(self):
        self.assertTrue(IExcludeFromNavigation.providedBy(self.c1))
