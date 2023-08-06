from dm.command.emailbase import EmailCommand
from dm.dictionarywords import *
import dm.util.password

class EmailNewPassword(EmailCommand):
        
    msgBody = '''Your new password is: %(NEW_PASSWORD)s

It is strongly recommended that you update your password when you next login.

Regards,

The %(SERVICE_NAME)s Team
'''
    def __init__(self, person):
        super(EmailNewPassword, self).__init__()
        self.person = person

    def execute(self):
        self.newPassword = dm.util.password.generate()
        super(EmailNewPassword, self).execute()
        if self.isDispatchedOK:
            self.person.setPassword(self.newPassword)
            self.person.save()
            msg = "Set password for '%s', and sent notification by email." % self.person.name
            self.logger.info(msg)
        else:
            msg = "Not setting password for '%s' because notification email can not be sent." % self.person.name
            self.logger.warn(msg)

    def getMessageToList(self):
        if self.person.email:
            return [self.person.email]
        else:
            return []

    def getMessageSubject(self):
        return self.wrapMessageSubject('Your new password')

    def getMessageBody(self):
        serviceName = self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8')
        params = {
            'NEW_PASSWORD': self.newPassword,
            'SERVICE_NAME': serviceName,
        }
        return self.msgBody % params


