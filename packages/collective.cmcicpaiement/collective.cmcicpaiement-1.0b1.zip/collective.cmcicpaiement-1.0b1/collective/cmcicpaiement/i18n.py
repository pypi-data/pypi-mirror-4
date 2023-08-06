from zope.i18nmessageid import MessageFactory

message_factory = MessageFactory("collective.cmcicpaiement")
_ = message_factory

retour_MAC_desc_def = u"Sceau resultant de la certification des donnees"
retour_MAC_desc = _(u"retour_MAC_description", retour_MAC_desc_def)

retour_numauto_desc = _(u"Only if the paiement is authorized")
