import unittest2 as unittest
from collective.cmcicpaiement.tests import base, utils


class UnitTestAllerForm(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(UnitTestAllerForm, self).setUp()
        from collective.cmcicpaiement import aller
        self.request.debug = False

        self.form = aller.AllerForm(self.context, self.request)
        self.form._settings = utils.EnvSettings()
        self.form.portal_state = utils.FakePortalState()
        self.form.portal_membership = utils.FakePortalMembership()
        self.form.update()

    def test_version(self):
        self.assertEqual(self.form.version, "3.0")

    def test_action_url(self):
        url = self.form.action_url
        self.assertEqual(url,
                         "https://paiement.creditmutuel.fr/test/paiement.cgi")

    def test_urls(self):
        self.assertEqual(self.form.url_retour,
                         'http://nohost.com/@@cmcic_retour?uuid=MYUUID')
        self.assertEqual(self.form.url_retour_err,
                         'http://nohost.com/@@cmcic_retour_err?uuid=MYUUID')
        self.assertEqual(self.form.url_retour_ok,
                         'http://nohost.com/@@cmcic_retour_ok?uuid=MYUUID')

    def test_MAC(self):
        mac = self.form.MAC
        self.assertTrue(mac is not None)

    def test_date(self):
        dt = None
        d = self.form.date
        from datetime import datetime
        try:
            dt = datetime.strptime(d, '%d/%m/%Y:%H:%M:%S')
        except ValueError:
            pass
        self.assertTrue(dt is not None)

    def test_montant(self):
        def getMontant():
            return self.form.montant
        self.assertRaises(NotImplementedError, getMontant)

    def test_reference(self):
        def getReference():
            return self.form.reference
        self.assertRaises(NotImplementedError, getReference)

    def test_text_libre(self):
        #TODO: whats up their ?
        pass

    def test_mail(self):
        self.assertEqual(self.form.mail, "fakemember@gmail.com")

    def test_option(self):
        #TODO: whats up their ?
        pass

    def test_aller_form(self):
        #CAN T BE TEST IN UNITTEST
        pass

    def test_TPE(self):
        self.assertEqual(self.form.TPE,
                         self.form._oTpe.sNumero)


class IntegrationTestAllerForm(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(IntegrationTestAllerForm, self).setUp()

    def test_version(self):
        pass

    def test_action_url(self):
        pass

    def test_urls(self):
        pass

    def test_MAC(self):
        pass

    def test_date(self):
        pass

    def test_montant(self):
        pass

    def test_reference(self):
        pass

    def test_text_libre(self):
        #TODO: whats up their ?
        pass

    def test_mail(self):
        pass

    def test_option(self):
        #TODO: whats up their ?
        pass

    def test_aller_form(self):
        #CAN T BE TEST IN UNITTEST
        pass

    def test_TPE(self):
        pass


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
