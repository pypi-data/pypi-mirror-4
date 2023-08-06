from dm.command import Command
from dm.util.mailer import sendmail
from dm.dictionarywords import *

class EmailCommand(Command):

    messageTemplate = ''

    def execute(self):
        msgFrom = self.getMessageFrom()
        msgToList = self.getMessageToList()
        msgSubject = self.getMessageSubject()
        msgBody = self.getMessageBody()
        self.dispatchEmailMessage(msgFrom, msgToList, msgSubject, msgBody)

    def dispatchEmailMessage(self, msgFrom, msgToList, msgSubject, msgBody):
        self.isDispatchedOK = False
        smtpHost = self.dictionary[SMTP_HOST]
        smtpPort = self.dictionary[SMTP_PORT] or 0
        smtpUser = self.dictionary[SMTP_USER]
        smtpPassword = self.dictionary[SMTP_PASSWORD]
        smtpUseTls = bool(self.dictionary[SMTP_USE_TLS])
        logMsg = "email from '%s', to '%s', subject '%s', body: %s" % (
            repr(msgFrom), repr(msgToList), repr(msgSubject), repr(msgBody))
        if self.dictionary[ENABLE_EMAIL_SENDING]:
            self.logger.info("Sending %s" % logMsg)
            self.logger.debug("Sending email via host '%s' and port '%s'." % (smtpHost, smtpPort))
            if smtpUser and smtpPassword:
                self.logger.debug("Sending email using login credentials user '%s' and password '%s'." % (smtpUser, smtpPassword, smtpUseTls))
            self.logger.debug("Sending email %s TLS." % (smtpUseTls and 'with' or 'without'))
            for msgTo in msgToList:
                if msgTo:
                    try:
                        sendmail(msgFrom, msgTo, msgSubject, msgBody, smtpHost, smtpPort, smtpUser, smtpPassword, smtpUseTls)
                        self.isDispatchedOK = True
                    except Exception, inst:
                        msg = "Couldn't send %s: %s" % (logMsg, inst)
                        self.logger.error(msg)
        else:
            self.logger.debug("Email sending is not enabled. Skipping sending %s" % logMsg)

    def getMessageFrom(self):
        return self.dictionary[SERVICE_EMAIL]

    def getMessageToList(self):
        return []

    def getMessageSubject(self):
        return self.wrapMessageSubject("Service message")

    def wrapMessageSubject(self, msgSubject):
        systemName = self.dictionary[SYSTEM_NAME]
        return '[%s]: %s' % (systemName, msgSubject)

    def getMessageBody(self):
        return self.messageTemplate % self.getParams()

    def getParams(self):
        return {}
