# -*- coding: utf-8 -*-
"""Le sceau (à mettre dans le champ MAC) est calculé à l’aide d’une fonction
de hachage cryptographique en combinaison avec une clé secrète respectant
les spécifications de la RFC 2104.
Cette fonction générera le sceau à partir de données à certifier et
de la clé de sécurité commerçant sous sa forme opérationnelle.
Les données à certifier seront présentées sous la forme d’une concaténation
dans un ordre précis des informations du formulaire :

  <TPE>*<date>*<montant>*<reference>*<texte-libre>*
  <version>*<lgue>*<societe>*<mail>*<nbrech>*<dateech1>*<monta
  ntech1>*<dateech2>*<montantech2>*<dateech3>*<montantech3>*<d
  ateech4>*<montantech4>*<options>"""

#python
import hmac  # the python implementation of RFC 2104
import sha
from encodings import hex_codec

KEYS_ORDER = (
    'TPE', 'date', 'montant', 'reference', 'texte_libre',
    'version', 'lgue', 'societe', 'mail', 'nbrech', 'dateech1',
    'montantech1', 'dateech2', 'montantech2', 'dateech3', 'montantech3',
    'dateech4', 'montantech4', 'options'
)

SEPARATOR = '*'


def format_data(data):
    """Return a string from a dict supposed to have all waited keys"""
    concatened = ""

    if type(data) == dict:
        for KEY in KEYS_ORDER:
            if KEY in data:
                concatened += data[KEY]
            concatened += "*"
    else:
        for KEY in KEYS_ORDER:
            if hasattr(data, KEY):
                value = getattr(data, KEY)
                if hasattr(value, "__call__"):
                    value = value()
                if value:
                    concatened += value
            concatened += "*"
    return concatened[:-1]  # remove last *


class CMCIC_Tpe:

    def __init__(self):

        self.sVersion = "3.0"
        self._sCle = ""
        self.sNumero = "0394542"
        self.sUrlPaiement = ""

        self.sCodeSociete = "ABE"
        self.sLangue = "FR"

        self.sUrlOk = ""
        self.sUrlKo = ""


class CMCIC_Hmac:

    def __init__(self, oTpe):

        self._sUsableKey = self._getUsableKey(oTpe)

    def computeHMACSHA1(self, sData):

        return self.hmac_sha1(self._sUsableKey, sData)

    def hmac_sha1(self, sKey, sData):

        #HMAC = hmac.HMAC(sKey,None,hashlib.sha1)
        HMAC = hmac.HMAC(sKey, None, sha)
        HMAC.update(sData)

        return HMAC.hexdigest()

    def bIsValidHmac(self, sChaine, sMAC):

        return self.computeHMACSHA1(sChaine) == sMAC.lower()

    def _getUsableKey(self, oTpe):

        hexStrKey = oTpe._sCle[0:38]
        hexFinal = oTpe._sCle[38:40] + "00"

        cca0 = ord(hexFinal[0:1])

        if cca0 > 70 and cca0 < 97:
                hexStrKey += chr(cca0 - 23) + hexFinal[1:2]
        elif hexFinal[1:2] == "M":
                hexStrKey += hexFinal[0:1] + "0"
        else:
                hexStrKey += hexFinal[0:2]

        c = hex_codec.Codec()
        hexStrKey = c.decode(hexStrKey)[0]

        return hexStrKey
