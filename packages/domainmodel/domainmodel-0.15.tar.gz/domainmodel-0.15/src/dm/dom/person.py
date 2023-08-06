from dm.dom.stateful import *
from dm.ioc import *
from dm.messagedigest import md5
#import dm.messagedigest import sha
from dm.dictionarywords import INITIAL_PERSON_ROLE
import dm.regexps

class EmailAddress(SimpleObject):

    emailAddress = String(isUnique=True)
    isConfirmed = Boolean(isHidden=True)
    person = HasA('Person')

    ownerAttrNames = ['person', 'emailAddresses']

    sortOnName = 'emailAddress'


personNameRegex = '^(?!%s)%s$' % (dm.regexps.reservedPersonName, dm.regexps.personName)

class Person(StandardObject):
    "Registered person."

    collectiveNoun = 'people'

    searchAttributeNames = ['name', 'fullname']

    name = String(isUnique=True, isIndexed=True, isImmutable=True,
        regex=personNameRegex, minLength=2, maxLength=256)
    password = Password(regex='^\S{4,}$', minLength=4)
    fullname = String(regex='.*\S.*', isRequired=False)
    role     = HasA('Role', isEditable=False, default=StandardObject.dictionary[INITIAL_PERSON_ROLE])
    emailAddresses = HasMany('EmailAddress')
    sessions = HasMany('Session', 'key', isHidden=True)
    grants   = HasMany('PersonalGrant', 'permission', isHidden=True)
    bars     = HasMany('PersonalBar', 'permission', isHidden=True)

    sortOnName = 'fullname'

    def getLabelValue(self):
        return self.fullname.strip() or self.name

    def getFirstName(self):
        name = self.getLabelValue()
        parts = name.strip().split(' ')
        return parts[0]

    def initialise(self, register=None):
        super(Person, self).initialise(register)
        if not self.role:
            roleName = self.dictionary[INITIAL_PERSON_ROLE]
            self.role = self.registry.roles[roleName]
            self.isChanged = True

    def isPassword(self, password):
        if not self.password:
            return False
        return self.password == self.makeDigest(password)

    def setPassword(self, password):
        if password:
            self.password = self.makeDigest(password)
        else:
            self.password = ''

    def makeDigest(self, clearText):
        passwordAttr = self.meta.attributeNames['password']
        return passwordAttr.makeDigest(clearText)

    def getEmailAddress(self):
        emailAddress = self.emailAddresses.findFirstDomainObject()
        if emailAddress:
            return emailAddress.emailAddress
        else:
            return ''

    def setEmailAddress(self, emailAddress):
        domainObject = self.emailAddresses.findFirstDomainObject()
        if domainObject:
            if emailAddress != domainObject.emailAddress:
                domainObject.emailAddress = emailAddress
                domainObject.save()
        else:
            self.emailAddresses.create(emailAddress=emailAddress)

    email = property(getEmailAddress, setEmailAddress)


    def getApiKey(self):
        # Todo: Convert to model attribute?
        apiKeys = self.registry.apiKeys.findDomainObjects(person=self)
        if len(apiKeys) == 0:
            apiKey = self.registry.apiKeys.create(person=self)
        elif len(apiKeys) == 1:
            apiKey = apiKeys[0]
        else:
            raise Exception, "Error: Person '%s' has %s API keys (should only have 1)." % (self.name, len(apiKeys))
        return apiKey

    def delete(self):
        for session in self.sessions:
            session.delete()
        super(Person, self).delete()

    def undelete(self):
        super(Person, self).undelete()

    def purge(self):
        for session in self.sessions:
            session.delete()
        for grant in self.grants:
            grant.delete()
        for bar in self.bars:
            bar.delete()
        super(Person, self).purge()


class PersonalGrant(SimpleObject):
    "Positively associates a Person directly with a Permission."

    person      = HasA('Person')
    permission  = HasA('Permission')

    def getLabelValue(self):
        return "%s-%s" % (
            self.person.getLabelValue(),
            self.permission.getLabelValue(),
        )


class PersonalBar(PersonalGrant):
    "Negatively associates a Person directly with a Permission."
    pass

