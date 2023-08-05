import unittest2 as unittest
from collective.linguadomains.tests import base, utils
from collective.linguadomains import validator


class IntegrationTestValidator(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(IntegrationTestValidator, self).setUp()
        self.viewlet = validator.URLValidator(self.folder, self.request, None)
        base = 'collective.linguadomains.controlpanel.ISettingsSchema'
        self.portal.portal_registry['%s.mapping' % base] = utils.TEST_MAPPING
        self.portal.portal_registry['%s.activated' % base] = True

    def set_url(self, url, path=""):
        self.request.set('ACTUAL_URL', url + path)
        self.request.set('SERVER_URL', url)

    def test_not_configure_url(self):
        self.set_url("http://noexisting/plone", "/news")
        self.viewlet.update()
        self.assertTrue(self.request.RESPONSE.status == 200)

    def test_good_url(self):
        self.set_url('http://nohost-fr')
        self.folder.setLanguage('fr')
        self.viewlet.update()
        self.assertTrue(self.request.RESPONSE.status == 200)

    def test_should_redirect(self):
        self.set_url('http://nohost-fr')
        self.folder.setLanguage('nl')
        self.viewlet.update()
        self.assertTrue(self.request.RESPONSE.status == 302)

    def test_not_activated(self):
        base = 'collective.linguadomains.controlpanel.ISettingsSchema'
        self.portal.portal_registry['%s.activated' % base] = False
        self.set_url('http://nohost-fr')
        self.folder.setLanguage('nl')
        self.viewlet.update()
        self.assertTrue(self.request.RESPONSE.status == 200)

    def test_language_not_in_mapping(self):
        self.set_url('http://nohost-fr')
        self.folder.setLanguage('xx')
        self.viewlet.update()
        self.assertTrue(self.request.RESPONSE.status == 200)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
