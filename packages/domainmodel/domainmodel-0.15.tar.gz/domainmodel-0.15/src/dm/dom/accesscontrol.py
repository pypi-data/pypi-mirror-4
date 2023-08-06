from dm.dom.base import *
from dm.ioc import *
from dm.strategy import MakeProtectedNames
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS

class Grant(SimpleObject):
    "Registered granted permission. Associates a Role and a Permission."

    permission  = HasA('Permission')
    role        = HasA('Role')
    dbName      = 'grants'  # plural table name ('grant' is SQL keyword)

    def getLabelValue(self):
        return "%s-%s" % (
            self.role.getLabelValue(),
            self.permission.getLabelValue(),
        )

class Role(NamedObject):
    "Registered role."

    isConstant  = True
    grants = AggregatesMany('Grant', 'permission')
    
    def hasPermission(self, permission):
        return permission in self.grants


class Action(NamedObject):
    """
    Registered action.
    Actions are combined with ProtectionObjects to create Permissions.
    """
    
    isConstant  = True
    # define aggregates
    permissions = AggregatesMany('Permission', 'protectionObject')  
    
    def initialise(self, register):
        super(Action, self).initialise(register)
        # initialise aggregates
        if not self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            for protectionObject in self.registry.protectionObjects:
                self.permissions.create(protectionObject)


class Permission(SimpleObject):
    """
    Registered permission. Associates Actions and ProtectionObjects.
    Permissions are combined with Roles and Persons to create Grants and Bars.
    """

    action           = HasA('Action')
    protectionObject = HasA('ProtectionObject')
    grants           = AggregatesMany('Grant', 'role')
    personalGrants   = AggregatesMany('PersonalGrant', 'person')
    personalBars     = AggregatesMany('PersonalBar', 'person')
    
    def getLabelValue(self):
        return "%s-%s" % (
            self.protectionObject.getLabelValue(),
            self.action.getLabelValue(),
        )


class ProtectionObject(NamedObject):
    "Protects a protected object with a protected name."

    permissions = AggregatesMany('Permission', 'action')

    def initialise(self, register):
        super(ProtectionObject, self).initialise(register)
        # initialise aggregates 
        for action in self.registry.actions:
            self.permissions.create(action)

