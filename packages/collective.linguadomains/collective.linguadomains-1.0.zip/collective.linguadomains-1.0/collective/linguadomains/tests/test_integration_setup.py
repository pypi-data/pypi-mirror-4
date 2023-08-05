import unittest2 as unittest
from collective.linguadomains.tests import base


class IntegrationTestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_controlpanel(self):
        panels = self.portal.portal_controlpanel.listActions()
        panel_ids = [panel.id for panel in panels]
        self.assertIn('collective.linguadomains', panel_ids)

    def test_registry(self):
        registry = self.portal.portal_registry
        base = 'collective.linguadomains.controlpanel.ISettingsSchema'
        activated = registry.records.get('%s.activated' % base)
        self.assertTrue(activated is not None)
        self.assertTrue(activated.value)  # check default value
        mapping = registry.records.get('%s.mapping' % base)
        self.assertTrue(mapping is not None)
        self.assertTrue(mapping.value == [])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
