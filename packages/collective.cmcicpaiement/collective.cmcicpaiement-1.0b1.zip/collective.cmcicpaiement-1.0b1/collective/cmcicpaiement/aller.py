# -*- coding: utf-8 -*-
#zope
from zope import component
from zope import schema
from zope import interface
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

#cmf
from Products.CMFCore.utils import getToolByName

#plone
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID

#others
from collective.cmcicpaiement import sceau
from collective.cmcicpaiement import settings
from collective.cmcicpaiement.sceau import format_data


class IAllerDataSchema(interface.Interface):
    """Interface "Aller" define all the needed data to create the form"""

    version = schema.ASCIILine(title=u"version", default="3.0")

    TPE = schema.ASCIILine(
        title=u"TPE",
        description=u"Numero de TPE Virtuel du commercant. Length : 7 car"
    )

    montant = schema.ASCIILine(
        title=u"Montant",
        description=u"Montant TTC de la commande formatee"
    )

    reference = schema.ASCIILine(title=u"Reference ID", description=u"12 max")

    texte_libre = schema.Text(
        title=u"Some text",
        description=u"3200 caracters max"
    )

    mail = schema.ASCIILine(title=u"EMail address")

    lgue = schema.ASCIILine(title=u"Language")

    societe = schema.ASCIILine(title=u"Societe")

    url_retour = schema.URI(title=u"Visitor URL to come back")

    url_retour_ok = schema.URI(
        title=u"Visitor URL to come back",
        description=u"next to an accepted paiement"
    )

    url_retour_err = schema.URI(
        title=u"Visitor URL to come back",
        description=u"next to a failed paiement"
    )

    MAC = schema.ASCIILine(title=u"Sceau from the certification of data")

    options = schema.ASCIILine(
        title=u"URL encoded other options",
        description=u"Options must be in aliascb,forcesaisiecb"
    )


class IFractionnedAllerDataSchema(IAllerDataSchema):

    nbrech = schema.Int(title=u"How many echeances",
                        min=0, max=4)

    dateech1 = schema.Date(title=u"Date of the first echeance")

    montantech1 = schema.ASCIILine(title=u"Amount echeance 1")

    dateech2 = schema.Date(title=u"Date of the second echeance")

    montantech2 = schema.ASCIILine(title=u"Amount echeance 2")

    dateech3 = schema.Date(title=u"Date of the third echeance")

    montantech3 = schema.ASCIILine(title=u"Amount echeance 3")

    dateech4 = schema.Date(title=u"Date of the fourth echeance")

    montantech4 = schema.ASCIILine(title=u"Amount echeance 4")


class AllerForm(BrowserView):
    """Aller for implement the form to let the user go in paiement aller
    process"""
    interface.implements(IAllerDataSchema)
    aller_form_template = ViewPageTemplateFile('aller_form.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._oTpe = sceau.CMCIC_Tpe()
        self.portal_state = None
        self.portal_membership = None
        self._settings = None
        self.contact_source = None
        self.contact = None
        self._montant = None
        self._reference = None
        self.url_retour = None
        self.url_retour_ok = None
        self.url_retour_err = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        if self._settings is None:
            registry = component.queryUtility(IRegistry)
            if registry:
                self._settings = registry.forInterface(settings.Settings)
        if self.portal_state is None:
            self.portal_state = component.getMultiAdapter(
                (self.context, self.request),
                name="plone_portal_state"
            )
        if self.portal_membership is None:
            self.portal_membership = getToolByName(
                self.context,
                'portal_membership'
            )
#        self._MAC.set_key(self._settings.security_key)

        #update oTpe
        self._oTpe._sCle = self._settings.security_key
        self._oTpe.sCodeSociete = self._settings.societe
        bank_url = settings.URLS.get(self._settings.bank)
        self._oTpe.sUrlPaiement = bank_url["paiement"]

        site_url = self.portal_state.navigation_root_url()
        UUID = self.getUUID()

        if self.url_retour is None:
            self.url_retour = '%s/@@cmcic_retour?uuid=%s' % (site_url, UUID)
        if self.url_retour_ok is None:
            self.url_retour_ok = '%s/@@cmcic_retour_ok?uuid=%s' % (site_url,
                                                                   UUID)
        if self.url_retour_err is None:
            self.url_retour_err = '%s/@@cmcic_retour_err?uuid=%s' % (site_url,
                                                                     UUID)

        if self.contact_source is None:
            self.contact_source = self._settings.contact_source

        if self.contact is None:
            if self.contact_source == "member":
                self.contact = self.portal_state.member()
            elif self.contact_source == "creator":
                creator = self.Creators()[0]
                self.contact = self.portal_membership.getMemberById(creator)

    @property
    def version(self):
        return self._oTpe.sVersion

    @property
    def societe(self):
        return self._oTpe.sCodeSociete

    @property
    def TPE(self):
        return self._oTpe.sNumero

    @property
    def lgue(self):
        return self._oTpe.sLangue

    @property
    def action_url(self):
        return self._oTpe.sUrlPaiement

    @property
    def date(self):
        return self.context.modified().strftime('%d/%m/%Y:%H:%M:%S')

    @property
    def montant(self):
        if self._montant is not None:
            return self._montant
        raise NotImplementedError("must be implemented in subclass")

    @property
    def reference(self):
        if self._reference is not None:
            return self._reference
        raise NotImplementedError("must be implemented in subclass")

    @property
    def texte_libre(self):
        return u"texte_libre"

    @property
    def mail(self):
        #Note: we may use the creator of hte context ...
        if self.contact is not None:
            return self.contact.getProperty('email')
        raise ValueError("can t get email contact")

    @property
    def options(self):
        return ""

    def aller_form(self):
        return self.aller_form_template()

    @property
    def MAC(self):

        oMac = sceau.CMCIC_Hmac(self._oTpe)
        sChaineMAC = str(format_data(self))

        return oMac.computeHMACSHA1(sChaineMAC)

    def getUUID(self):
        try:
            UUID = IUUID(self.context)
        except TypeError:
            UUID = self.context.UUID()
        return UUID
