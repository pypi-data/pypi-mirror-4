import os
from dm.command.base import Command
from dm.command.state import *
from dm.command.accesscontrol import GrantStandardSystemAccess
from dm.command.person import *
import shutil
import pkg_resources
from dm.dictionarywords import *

class InitialiseDomainModelBase(Command):

    def execute(self):
        super(InitialiseDomainModelBase, self).execute()
        self.failIfDomainModelIsInitialised()
        self.initialiseDomainModelObjects()

    def failIfDomainModelIsInitialised(self):
        if self.registry.states.count():
            raise Exception, "Database is already initialised."

    def initialiseDomainModelObjects(self):
        self.createStates()
        self.createSystem()
        self.createActions()

    def createStates(self):
        self.registry.states.create('active')
        self.registry.states.create('deleted')
        self.registry.states.create('pending')
        
    def createSystem(self):
        self.registry.systems.create(
            version=self.dictionary[SYSTEM_VERSION],
            mode=self.dictionary[SYSTEM_MODE],
        )

    def createActions(self):
        self.registry.actions.create('Create')
        self.registry.actions.create('Approve')
        self.registry.actions.create('Read')
        self.registry.actions.create('Update')
        self.registry.actions.create('Delete')
        self.registry.actions.create('Purge')
        

class InitialiseDomainModel(InitialiseDomainModelBase):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(InitialiseDomainModel, self).__init__()
    
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createRoles()
        self.createProtectionObjects()
        self.createGrants()
        self.createRefusals()
        self.createAccessControlPlugin()
        self.createPersons()
        if self.dictionary[SYSTEM_MODE] == 'development':
            self.createTestPlugins()
            self.setUpTestFixtures()
        self.commitSuccess()

    def createRoles(self):
        roles = self.registry.roles
        self.adminRole     = roles.create('Administrator')
        self.developerRole = roles.create('Developer')
        self.friendRole    = roles.create('Friend')
        self.visitorRole   = roles.create('Visitor')
        
    def createProtectionObjects(self):
        self.registry.protectionObjects.create('Session')
        self.registry.protectionObjects.create('System')
        self.registry.protectionObjects.create('Person')
        self.registry.protectionObjects.create('Plugin')
        self.registry.protectionObjects.create('Role')

    def createGrants(self):
        self.grantAdministratorAccess()
        self.grantRegistrationAccess()
        self.grantStandardSystemAccess('System')
        self.grantStandardSystemAccess('Person')

    def grantAdministratorAccess(self):
        for protectionObject in self.registry.protectionObjects:
            for permission in protectionObject.permissions:
                if not permission in self.adminRole.grants:
                    self.adminRole.grants.create(permission)

    def grantRegistrationAccess(self):
        create = self.registry.actions['Create']
        protectionObjects = self.registry.protectionObjects
        for role in self.registry.roles:
            personProtection = protectionObjects['Person']
            createPerson = personProtection.permissions[create]
            if not createPerson in role.grants:
                role.grants.create(createPerson)

    def grantStandardSystemAccess(self, protectedName):
        protectionObject = self.registry.protectionObjects[protectedName]
        cmd = GrantStandardSystemAccess(protectionObject)
        cmd.execute()

    def createRefusals(self):
        pass

    def createPersons(self):
        domainName = self.dictionary[SITE_HOST]
        cmd = PersonCreate('admin', 
            role=self.adminRole,
            fullname='Administrator',
        )
        cmd.execute()
        self.adminPerson = cmd.person
        self.adminPerson.setPassword('pass')
        self.adminPerson.save()
        self.adminPerson.setEmailAddress('kforge-admin@%s' % domainName)
        
        visitorRoleName = self.dictionary[VISITOR_ROLE]
        visitorRole = self.registry.roles[visitorRoleName]
        cmd = PersonCreate(self.dictionary[VISITOR_NAME],
            role = visitorRole,
            fullname='Visitor',
        )
        cmd.execute()
        self.visitorPerson = cmd.person
        
    def createAccessControlPlugin(self):
        plugins = self.registry.plugins
        plugins.create('accesscontrol')
    
    def createTestPlugins(self):
        plugins = self.registry.plugins
        plugins.create('example')
    
    def setUpTestFixtures(self):
        domainName = self.dictionary[SITE_HOST]
        personRoleName = self.dictionary[INITIAL_PERSON_ROLE]
        personRole = self.registry.roles[personRoleName]
        # do not reuse roles set in other methods as this method
        # should be callable on its own
        adminPerson = self.registry.people['admin']
        adminRole = self.registry.roles['Administrator']
        friendRole = self.registry.roles['Friend']

        cmd = PersonCreate('levin',
            role = personRole,
            fullname=u'Levin \xf3',
        )
        cmd.execute()
        levin = cmd.person
        levin.setPassword('levin')
        levin.save()
        levin.setEmailAddress('levin@%s' % domainName)
        
        cmd = PersonCreate('natasha',
            role = personRole,
            fullname=u'Natasha \xf3',
        )
        cmd.execute()
        natasha = cmd.person
        natasha.setPassword('natasha')
        natasha.save()
        natasha.setEmailAddress('natasha@%s' % domainName)
        visitor = self.registry.people[self.dictionary[VISITOR_NAME]]
        
    def tearDownTestFixtures(self):
        # [[TODO: factor this out into a command class]]
        
        def purgePerson(personName):
            if self.registry.people.has_key(personName):
                self.registry.people[personName].delete()
            if self.registry.people.getAll().has_key(personName):
                self.registry.people.getAll()[personName].purge()
        purgePerson('natasha')
        purgePerson('levin')
        purgePerson('anna')
        purgePerson('bolskonski')


class InitialiseFilesystem(object):

    def __init__(self, dictionary=None, verbose=False):
        self.dictionary = dictionary
        self.templatesResourcePath = self.dictionary[TEMPLATES_RESOURCE_PATH]
        self.mediaResourcePath = self.dictionary[MEDIA_RESOURCE_PATH]
        self.systemName = self.dictionary[SYSTEM_NAME]
        self.packageName = self.dictionary[SYSTEM_PACKAGE_NAME]
        self.verbose = verbose

    def execute(self):
        umask = os.umask(0o027)
        try:
            varDirPath = os.path.join(self.dictionary[FILESYSTEM_PATH], 'var')
            logDirPath = os.path.dirname(self.dictionary[LOG_PATH])
            if not os.path.exists(varDirPath):
                os.makedirs(varDirPath)
            if not os.path.exists(logDirPath):
                os.makedirs(logDirPath)
            os.chmod(logDirPath, 0o770)
            if not os.path.exists(self.dictionary[IMAGES_DIR_PATH]):
                os.makedirs(self.dictionary[IMAGES_DIR_PATH])
            self.installTemplates()
            self.installMedia()
        finally:
            os.umask(umask)

    def installTemplates(self):
        #self.installDmPackageTemplates()
        self.installApplicationTemplates()

    def installDmPackageTemplates(self):
        if self.packageName != 'dm':
            installPath = self.dictionary[DJANGO_TEMPLATES_DIR]
            self.installFiles('templates', self.templatesResourcePath, installPath, packageName='dm')

    def installApplicationTemplates(self):
        installPath = self.dictionary[DJANGO_TEMPLATES_DIR]
        self.installFiles('templates', self.templatesResourcePath, installPath)

    def installMedia(self):
        installPath = self.dictionary[MEDIA_PATH]
        if os.path.exists(installPath):
            raise Exception, "Path already exists: %s" % installPath
        self.installFiles('media', self.mediaResourcePath, installPath)

    def installFiles(self, purpose, resourcePath, installPath, packageName=None):
        if not installPath:
            raise Exception, "installPath is missing."
        installPath = os.path.normpath(installPath)
        if os.path.exists(installPath):
            raise Exception, "Folder for '%s' already exists : %s" % (purpose, installPath)
        if not packageName:
            packageName = self.packageName
        packageModule = __import__(packageName, '', '', '*')
        packagePath = os.path.dirname(packageModule.__file__)
        fullResourcePath = os.path.join(packagePath, resourcePath)
        if not os.path.exists(os.path.dirname(installPath)):
            os.makedirs(installPath)
        try:
            shutil.copytree(fullResourcePath, installPath)
        except OSError, inst:
            msg = "Couldn't install files from package resources: %s to %s: %s" % (
                fullResourcePath, installPath, inst
            )
            raise Exception, msg

