import unittest2 as unittest
from collective.linguadomains.tests import base, utils
from collective.linguadomains import validator
from zope.component.interfaces import ComponentLookupError


class UnitTestValidator(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        context = utils.FakeContext()
        request = utils.FakeRequest()
        self.viewlet = validator.URLValidator(context, request, None)
        self.viewlet._manager = utils.FakeManager(context, request)

    def test_render(self):
        self.assertTrue(self.viewlet.index() == u"")

    def test_language(self):
        self.assertEqual(self.viewlet.language(),
                         self.viewlet.context.Language())

    def test_get_manager(self):
        self.assertEqual(self.viewlet.get_manager(),
                         self.viewlet._manager)
        self.viewlet._manager = None
        self.assertRaises(ComponentLookupError, self.viewlet.get_manager)

    def test_donotcheck(self):
        self.viewlet.request._data['donotcheck'] = True
        self.assertEqual(self.viewlet.update(),
                         None)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
