import os
from DateTime.DateTime import DateTime


class EnvSettings(object):
    def __init__(self):
        self.security_key = os.getenv(
            'CMCIC_SECURITY_KEY',
            'BEBD2381223A4BDD2C767B3F87E0B15C434C227B'
        )
        self.TPE = os.getenv('CMCIC_TPE')
        self.societe = os.getenv('CMCIC_SOCIETE')
        self.bank = os.getenv(
            'CMCIC_BANK',
            'https://paiement.creditmutuel.fr/test/'
        )
        self.contact_source = os.getenv('CMCIC_CONTACT_SOURCE', 'member')


SETTINGS = EnvSettings()


class FakeAcquisition(object):
    def __init__(self):
        self.aq_explicit = None


class FakeContext(object):

    def __init__(self):
        self.id = "myid"
        self.title = "a title"
        self.description = "a description"
        self.creators = ["myself"]
        self.date = "a date"
        self.aq_inner = FakeAcquisition()
        self.aq_inner.aq_explicit = self
        self._modified = "modified date"
        self.remoteUrl = ''  # fake Link
        self._modified = DateTime()

    def UUID(self):
        return "MYUUID"

    def Language(self):
        return "fr"

    def getId(self):
        return self.id

    def Title(self):
        return self.title

    def Creators(self):
        return self.creators

    def Description(self):
        return self.description

    def Date(self):
        return self.date

    def modified(self):
        return self._modified

    def getPhysicalPath(self):
        return ('/', 'a', 'not', 'existing', 'path')

    def getFolderContents(self, filter=None):
        catalog = FakeCatalog()
        return catalog.searchResults()

    def absolute_url(self):
        return "http://nohost.com/" + self.id

    def queryCatalog(self, **kwargs):  # fake Topic
        catalog = FakeCatalog()
        return catalog.searchResults()

    def getRemoteUrl(self):  # fake Link
        return self.remoteUrl


class FakeMember(object):
    def __init__(self):
        self.email = "fakemember@gmail.com"
        self.id = ""

    def getProperty(self, pp):
        return getattr(self, pp)


class FakePortalState(object):

    def navigation_root_url(self):
        return 'http://nohost.com'

    def member(self):
        return FakeMember()


class FakePortalMembership(object):

    def getMemberById(self, id):
        member = FakeMember()
        member.id = id
        return member


class FakeBrain(object):
    def __init__(self):
        self.Title = ""
        self.Description = ""
        self.getId = ""
        self.portal_type = ""

    def getURL(self):
        return "http://fakebrain.com"

    def getObject(self):
        ob = FakeContext()
        ob.title = self.Title

        return ob


class FakeCatalog(object):
    def searchResults(self, **kwargs):
        brain1 = FakeBrain()
        brain1.Title = "My first article"
        brain2 = FakeBrain()
        brain2.Title = "A great event"
        brain2.Description = "you will drink lots of beer"
        return [brain1, brain2]

    def modified(self):
        return '654654654654'
