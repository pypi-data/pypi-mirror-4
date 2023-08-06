import transaction
import unittest2 as unittest
from zope import interface
from collective.cmcicpaiement import testing
from collective.cmcicpaiement.tests import utils


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        from ZPublisher.tests.testPublish import Request
        from zope.annotation.interfaces import IAttributeAnnotatable
        from collective.cmcicpaiement.layer import ILayer

        super(UnitTestCase, self).setUp()
        self.context = utils.FakeContext()
        self.request = Request()
        interface.alsoProvides(self.request, (IAttributeAnnotatable, ILayer))


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']


class FunctionalTestCase(IntegrationTestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        #we must commit the transaction
        transaction.commit()
