import transaction
import unittest2 as unittest
from collective.linguadomains import testing
from plone.app import testing as ptesting


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        ptesting.setRoles(self.portal, ptesting.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        ptesting.setRoles(self.portal, ptesting.TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']


class FunctionalTestCase(IntegrationTestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        #we must commit the transaction
        transaction.commit()
