import logging
from datetime import datetime

#zope
from zope import component
from zope import event
from zope import interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from AccessControl.SecurityManagement import newSecurityManager
from Products.Five.browser import BrowserView

#cmf
from Products.CMFCore.utils import getToolByName

#plone
from plone.registry.interfaces import IRegistry

#others
from collective.cmcicpaiement import sceau
from collective.cmcicpaiement import i18n
from collective.cmcicpaiement import settings

#module var
_ = i18n.message_factory

cvx_vocabulary = SimpleVocabulary([
    SimpleTerm('oui', 'oui', _(u'Le cryptogramme visuel a ete saisie')),
    SimpleTerm('non', 'non', _(u'Pas de cryptogramme'))
])

logger = logging.getLogger('nge.boutique.retour')


class RetourView(BrowserView):
    """Retour browser view is called by the CM CIC"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._oTpe = sceau.CMCIC_Tpe()
        self.portal_state = None
        self.portal_membership = None
        self._settings = None
        self._sceau_validated = False

    def __call__(self):
        self.update()
        if self._sceau_validated:
            self.sudo()
            self.notify()
        return self.message

    def update(self):
        """build retour object, validate it and notify the system"""
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
                self.context, 'portal_membership'
            )

        #update oTpe
        self._oTpe._sCle = self._settings.security_key
        self._oTpe.sCodeSociete = self._settings.societe
        bank_url = settings.URLS.get(self._settings.bank)
        self._oTpe.sUrlPaiement = bank_url["paiement"]

        #code copy paste adapted from provided example from the CM CIC
        params = self.request.form

        oTpe = self._oTpe
        oHmac = sceau.CMCIC_Hmac(oTpe)

        Certification = {
            'MAC': "", 'date': "", 'montant': "", 'reference': "",
            'texte-libre': "", 'code-retour': "", 'cvx': "", 'vld': "",
            'brand': "", 'status3ds': "", 'numauto': "", 'motifrefus': "",
            'originecb': "", 'bincb': "", 'hpancb': "", 'ipclient': "",
            'originetr': "", 'veres': "", 'pares': "", 'montantech': ""
        }

        for key in Certification.keys():
            if key in params:  # .has_key(key):
                Certification[key] = params[key]  # value

        sChaineMAC = oTpe.sNumero + "*" + Certification["date"] + "*" +\
            Certification['montant'] + "*" + Certification['reference'] +\
            "*" + Certification['texte-libre'] + "*" + oTpe.sVersion + "*" +\
            Certification['code-retour'] + "*" + Certification['cvx'] + "*" +\
            Certification['vld'] + "*" + Certification['brand'] + "*" +\
            Certification['status3ds'] + "*" + Certification['numauto'] +\
            "*" + Certification['motifrefus'] + "*" +\
            Certification['originecb'] + "*" + Certification['bincb'] + "*" +\
            Certification['hpancb'] + "*" + Certification['ipclient'] + "*" +\
            Certification['originetr'] + "*" + Certification['veres'] + "*" +\
            Certification['pares'] + "*"

        self._sceau_validated = oHmac.bIsValidHmac(
            sChaineMAC,
            Certification['MAC']
        )

        #for documentation purpose, real code is managed by the notification
        if self._sceau_validated:
            sResult = "0"
        else:
            sResult = "1\n" + sChaineMAC

        self.event = RetourEvent(self.context, self.request, params)
        self.message = "version=2\ncdr=" + sResult

    def notify(self):
        event.notify(self.event)

    def sudo(self):
        """Give admin power to the current call"""
        #TODO: verify the call is emited from the bank server
        acl_users = getToolByName(self.context, 'acl_users')
        admin = acl_users.getUserById(self._settings.sudoer)
        newSecurityManager(self.request, admin)

RETOUR_ATTRS = {
    "MAC": None,
    "TPE": None,
    "date": {"strptime": "%d/%m/%Y_a_%H:%M:%S"},
    "montant": None,
    "texte_libre": {"name": "texte-libre"},
    "reference": None,
    "code_retour": {"name": "code-retour",
                    "constraints": ('payetest', 'paiement', 'Annulation')},
    "cvx": None,
    "vld": None,
    "brand": {"constraints": ('AM', 'CB', 'MC', 'VI', 'na')},
    "status3ds": {"constraints": ('-1', '1', '2', '3', '4')},
    "numauto": None,
    "motifrefus": {"constraints": ('Appel Phonie', 'Refus', 'Interdit',
                                   'Filtrage')},
    "originecb": None,  # TODO code iso 3166-1
    "bincb": None,
    "hpancb": None,
    "ipclient": None,
    "originetr": None,  # TODO code iso 3166-1
    "veres": None,
    "pares": None,
    "montanttech": None,
    "filtragecause": {
        "constraints": ('1', '2', '3', '4', '5', '6', '7', '8',
        '9', '10', '11', '12', '13', '14', '15', '16')
    },
    "filtragevaleur": None,
    "cbmasquee": None
}


class IRetourEvent(interface.Interface):
    """Retour event interface"""


class RetourEvent(object):
    """Retour event is throwed when the bank contact the server
    You have to subscribe to this event to manage bank return

    Notification happens on every try.
    """
    interface.implements(IRetourEvent)

    def __init__(self, context, request, retour):
        self.retour = retour
        self.context = context
        self.request = request

    def __getattr__(self, name):
        if self.retour and name in RETOUR_ATTRS:
            config = RETOUR_ATTRS[name]
            if config and "name" in config and config['name'] in self.retour:
                value = self.retour[config['name']]
            elif name in self.retour:
                value = self.retour[name]
            if config and "strptime" in config:
                value = datetime.strptime(value, config["strptime"])

            if config and 'constraints' in config:
                if value in config['constraints']:
                    return value
                else:
                    logger.error('wrong value for %s: %s' % (name, value))
            else:
                return value
