# todo: delete?

from dm.command.base import Command

class RoleCommand(Command):
    "Abstract Role command."
        
    def __init__(self, id):
        super(RoleCommand, self).__init__()
        self.id = id
        self.role = None
        self.roles = self.registry.roles

class RoleRead(RoleCommand):
    "Command to read a registered role."

    def __init__(self, id):
        super(RoleRead, self).__init__(id)

    def execute(self):
        "Make it so."
        super(RoleRead, self).execute()
        id = self.id
        if self.roles.has_key(id):
            self.role = self.roles[id]
        else:
            self.raiseError("No role found with id '%s'." % id)

class RoleList(RoleCommand):
    "Command to list registered roles."

    def __init__(self):
        super(RoleList, self).__init__(None)

    def execute(self):
        "Make it so."
        super(RoleList, self).execute()

