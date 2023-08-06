import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from collective.demositebadge.testing import \
    COLLECTIVE_DEMOSITEBADGE_INTEGRATION_TESTING


class TestInstallation(unittest.TestCase):

    layer = COLLECTIVE_DEMOSITEBADGE_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_js_registration(self):
        jsRegistry = getToolByName(self.portal, 'portal_javascripts')
        self.assertTrue('demo-site-badge.js' in jsRegistry.getResourceIds())

    def test_css_registration(self):
        cssRegistry = getToolByName(self.portal, 'portal_css')
        self.assertTrue('++resource++demo-site-badge.css' in \
                        cssRegistry.getResourceIds())

    def test_controlpanel_registration(self):
        present = False
        controlPanel = getToolByName(self.portal,'portal_controlpanel')
        panelsList = controlPanel.listActions()
        for panel in panelsList:
            if panel.appId == 'collective.demositebadge':
                present = True
        self.assertTrue(present)

    def test_registry(self):
        registry = getUtility(IRegistry)
        self.assertFalse(\
            registry['collective.demositebadge.interfaces.IBadgeSettings.check'])
        self.assertEqual(\
            registry['collective.demositebadge.interfaces.IBadgeSettings.text'],\
            u'Demo site')
