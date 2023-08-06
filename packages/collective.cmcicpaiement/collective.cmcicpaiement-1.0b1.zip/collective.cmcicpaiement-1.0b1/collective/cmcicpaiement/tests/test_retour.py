import unittest2 as unittest
from collective.cmcicpaiement.tests import base, utils


class UnitTestRetourView(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(UnitTestRetourView, self).setUp()
        from collective.cmcicpaiement import retour
        self.request.debug = False

        self.view = retour.RetourView(self.context, self.request)
        self.view._settings = utils.EnvSettings()
        self.view.portal_state = utils.FakePortalState()
        self.view.portal_membership = utils.FakePortalMembership()
        self.view.update()

    def test_update(self):
        pass

    def test_notify(self):
        pass

    def test_sudo(self):
        pass


class IntegrationTestRetourForm(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(IntegrationTestRetourForm, self).setUp()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
