import unittest2 as unittest
from collective.cmcicpaiement.tests import base
from plone.browserlayer import utils


class TestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_browserlayer(self):
        from collective.cmcicpaiement.layer import ILayer
        layers = utils.registered_layers()
        self.assertIn(ILayer, layers)

    def test_registry(self):
        pass


class TestUninstall(base.IntegrationTestCase):
    """Test if the addon uninstall well"""

    def setUp(self):
        super(TestUninstall, self).setUp()
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=['collective.cmcicpaiement'])

    def test_uninstall_browserlayer(self):
        from collective.cmcicpaiement.layer import ILayer
        layers = utils.registered_layers()
        self.assertNotIn(ILayer, layers)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
