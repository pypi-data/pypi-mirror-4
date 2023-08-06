from dm.command.base import Command

class StateCommand(Command):
    "Abstract State command."
        
    def __init__(self, name):
        super(StateCommand, self).__init__(stateName=name)
        self.name = name
        self.states = self.registry.states

class StateCreate(StateCommand):
    "Creates a new state."
        
    def __init__(self, name):
        super(StateCreate, self).__init__(name)

    def execute(self):
        "Make it so."
        super(StateCreate, self).execute()
        if self.name in self.states:
            message = "A state called '%s' already exists." % self.name
            self.raiseError(message)
        else:
            try:
                self.object = self.states.create(self.name)
                self.state = self.object
                self.commitSuccess()
            except Exception, inst:
                message = "Couldn't create that state: %s" % str(inst)
                self.raiseError(message)

