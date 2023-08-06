#zope
from zope import schema
from zope import interface

#others
from collective.cmcicpaiement import i18n
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

_ = i18n.message_factory
contact_source_vocab = SimpleVocabulary([
    SimpleTerm('member', 'member', u'Authenticated Member'),
    SimpleTerm('creator', 'creator', u'Creator of the context')
])


URLS = {
    "https://paiement.creditmutuel.fr/test/": {
        "recredit": "https://paiement.creditmutuel.fr/test/recredit_paiement.cgi",
        "capture": "https://paiement.creditmutuel.fr/test/capture_paiement.cgi",
        "paiement": "https://paiement.creditmutuel.fr/test/paiement.cgi"
    },
    "https://paiement.creditmutuel.fr/": {
        "recredit": "https://paiement.creditmutuel.fr/recredit_paiement.cgi",
        "capture": "https://paiement.creditmutuel.fr/capture_paiement.cgi",
        "paiement": "https://paiement.creditmutuel.fr/paiement.cgi"
    },
    "https://ssl.paiement.cic-banques.fr/test/": {
        "recredit": "https://ssl.paiement.cic-banques.fr/test/recredit_paiement.cgi",
        "capture": "https://ssl.paiement.cic-banques.fr/test/capture_paiement.cgi",
        "paiement": "https://ssl.paiement.cic-banques.fr/test/paiement.cgi"
    },
    "https://ssl.paiement.cic-banques.fr/": {
        "recredit": "https://ssl.paiement.cic-banques.fr/recredit_paiement.cgi",
        "capture": "https://ssl.paiement.cic-banques.fr/capture_paiement.cgi",
        "paiement": "https://ssl.paiement.cic-banques.fr/paiement.cgi"
    },
    "https://ssl.paiement.banque-obc.fr/test/": {
        "recredit": "https://ssl.paiement.banque-obc.fr/test/recredit_paiement.cgi",
        "capture": "https://ssl.paiement.banque-obc.fr/test/capture_paiement.cgi",
        "paiement": "https://ssl.paiement.banque-obc.fr/test/paiement.cgi"
    },
    "https://ssl.paiement.banque-obc.fr/": {
        "recredit": "https://ssl.paiement.banque-obc.fr/recredit_paiement.cgi",
        "capture": "https://ssl.paiement.banque-obc.fr/capture_paiement.cgi",
        "paiement": "https://ssl.paiement.banque-obc.fr/paiement.cgi"
    }
}


bank_vocabulary = SimpleVocabulary([
    SimpleTerm("https://paiement.creditmutuel.fr/test/",
               "https://paiement.creditmutuel.fr/test/",
               u"Credit Mutuel TEST"),
    SimpleTerm("https://paiement.creditmutuel.fr/",
               "https://paiement.creditmutuel.fr/",
               u"Credit Mutuel PRODUCTION"),
    SimpleTerm("https://ssl.paiement.cic-banques.fr/test/",
               "https://ssl.paiement.cic-banques.fr/test/",
               u"CIC banques TEST"),
    SimpleTerm("https://ssl.paiement.cic-banques.fr/",
               "https://ssl.paiement.cic-banques.fr/",
               u"CIC banques PRODUCTION"),
    SimpleTerm("https://ssl.paiement.banque-obc.fr/test/",
               "https://ssl.paiement.banque-obc.fr/test/",
               u"Banque-obc TEST"),
    SimpleTerm("https://ssl.paiement.banque-obc.fr/",
               "https://ssl.paiement.banque-obc.fr/",
               u"Banque-obc PRODUCTION"),
])


class Settings(interface.Interface):

    security_key = schema.Password(
        title=u"Security Key",
        description=u"This key is provided by the CM-CIC to the seller.\
            Must be kept secret. This key is a 40 length of hexa caracters"
    )

    TPE = schema.ASCIILine(title=_(u"TPE"))

    societe = schema.ASCIILine(title=_(u"Societe number"))

    bank = schema.Choice(
        title=_(u"Bank"),
        vocabulary=bank_vocabulary,
        default="https://paiement.creditmutuel.fr/test/"
    )

    contact_source = schema.Choice(
        title=_(u"Contact source"),
        vocabulary=contact_source_vocab,
        default='member'
    )

    sudoer = schema.ASCIILine(title=_(u"UserId to manage notification"))
