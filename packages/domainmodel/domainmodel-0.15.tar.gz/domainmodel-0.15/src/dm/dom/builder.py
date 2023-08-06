from dm.ioc import *

class ModelBuilder(object):

    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')

    def construct(self):
        if self.registry != None:
            self.loadState()
            self.loadSystem()
            self.loadEmailAddress()
            self.loadImage()
            self.loadPlugin()
            self.loadAccessControl()
            self.loadPerson()
            self.loadPersonalAccessControl()
            self.loadSession()
            self.loadCaptcha()

    def preload(self):
        self.registry.preloadCache = []
        for c in self.registry.domainClassRegister.values():
            self.registry.log.info('Preloading %s' % c.__name__)
            register = c.principalRegister or c.createRegister()
            self.registry.preloadCache.extend(register)

    def loadState(self):
        from dm.dom.state import State
        self.registry.registerDomainClass(State)
        self.registry.states = State.createRegister()
        State.principalRegister = self.registry.states
        self.registry.loadBackgroundRegister(self.registry.states)

    def loadSystem(self):
        from dm.dom.system import System
        self.registry.registerDomainClass(System)
        self.registry.systems = System.createRegister()
        System.principalRegister = self.registry.systems

    def loadImage(self):
        from dm.dom.image import Image
        self.registry.registerDomainClass(Image)
        self.registry.images = Image.createRegister()
        Image.principalRegister = self.registry.images

    def loadPlugin(self):
        from dm.dom.plugin import Plugin
        self.registry.registerDomainClass(Plugin)
        self.registry.plugins = Plugin.createRegister()
        Plugin.principalRegister = self.registry.plugins

    def loadAccessControl(self):
        from dm.dom.accesscontrol import Grant
        self.registry.registerDomainClass(Grant)
        self.registry.grants = Grant.createRegister()
        Grant.principalRegister = self.registry.grants
        
        from dm.dom.accesscontrol import Role
        self.registry.registerDomainClass(Role)
        self.registry.roles = Role.createRegister()
        Role.principalRegister = self.registry.roles

        from dm.dom.accesscontrol import Action
        self.registry.registerDomainClass(Action)
        self.registry.actions = Action.createRegister()
        Action.principalRegister = self.registry.actions

        from dm.dom.accesscontrol import Permission
        self.registry.registerDomainClass(Permission)
        self.registry.permissions = Permission.createRegister()
        Permission.principalRegister = self.registry.permissions

        from dm.dom.accesscontrol import ProtectionObject
        self.registry.registerDomainClass(ProtectionObject)
        self.registry.protectionObjects = ProtectionObject.createRegister()
        ProtectionObject.principalRegister = self.registry.protectionObjects

        self.registry.loadBackgroundRegister(self.registry.roles)
        self.registry.loadBackgroundRegister(self.registry.actions)

    def loadEmailAddress(self):
        from dm.dom.person import EmailAddress
        self.registry.registerDomainClass(EmailAddress)

    def loadPerson(self):
        from dm.dom.person import Person
        self.registry.registerDomainClass(Person)
        self.registry.people = Person.createRegister()
        Person.principalRegister = self.registry.people

    def loadPersonalAccessControl(self):
        from dm.dom.person import PersonalBar
        self.registry.registerDomainClass(PersonalBar)
        from dm.dom.person import PersonalGrant
        self.registry.registerDomainClass(PersonalGrant)

    def loadSession(self):
        from dm.dom.session import Session
        self.registry.registerDomainClass(Session)
        self.registry.sessions = Session.createRegister()
        Session.principalRegister = self.registry.sessions

    def loadCaptcha(self):
        if self.dictionary['captcha.enable']:
            from dm.dom.captcha import Captcha
            self.registry.registerDomainClass(Captcha)
            self.registry.captchas = Captcha.createRegister()

