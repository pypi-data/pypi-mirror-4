import unittest2 as unittest
from collective.cmcicpaiement.tests import base, utils


class TestCMCIC_Hmac(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(TestCMCIC_Hmac, self).setUp()
        from collective.cmcicpaiement import sceau
        self.oTpe = sceau.CMCIC_Tpe()
        self.mac = sceau.CMCIC_Hmac(self.oTpe)
        self.settings = utils.EnvSettings()
        self.oTpe._sCle = self.settings.security_key
        self.oTpe.sCodeSociete = self.settings.societe

    def test_getUsableKey(self):
        self.assertEqual(
            self.mac._getUsableKey(self.oTpe),
            '\xbe\xbd#\x81":K\xdd,v{?\x87\xe0\xb1\\CL"{'
        )

    def test_format_data(self):
        pass
        # TODO: add tests

    def test_computeHMACSHA1(self):
        pass

    def test_hmac_sha1(self):
        pass

    def test_bIsValidHmac(self):
        pass


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
