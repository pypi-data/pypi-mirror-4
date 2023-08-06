from email.MIMEText import MIMEText
from smtplib import SMTP

def sendmail(msgFrom, msgTo, msgSubject, msgBody, smtpHost='', smtpPort=0, smtpUser='', smtpPassword='', smtpUseTls=False):

    # Construct the Mime message string.
    if type(msgBody) == unicode:
        msgBody = msgBody.encode('utf-8')
    emailMsg = MIMEText(msgBody, _charset='utf-8')
    if type(msgFrom) == unicode:
        msgFrom = msgFrom.encode('utf-8')
    emailMsg['From'] = msgFrom
    if type(msgTo) == list:
        msgTo = [address.encode('utf-8') for address in msgTo]
        COMMASPACE = ', '
        emailMsg['To'] = COMMASPACE.join(msgTo)
    elif type(msgTo) == unicode:
        msgTo = msgTo.encode('utf-8')
        emailMsg['To'] = msgTo
    if type(msgSubject) == unicode:
        msgSubject = msgSubject.encode('utf-8')
    emailMsg['Subject'] = msgSubject
    msgText = emailMsg.as_string()

    # Construct the SMTP connection and send the message.
    try:
        smtp = SMTP(host=smtpHost, port=smtpPort)
        if smtpUseTls:
            smtp.starttls()
        if smtpUser and smtpPassword:
            smtp.login(user=smtpUser, password=smtpPassword)
        response = smtp.sendmail(msgFrom, msgTo, msgText)
        if response:
            msg = "Couldn't send email to all recipients: %s" % repr(response)
            raise Exception(msg)
    finally:
        try:
            smtp.close()
        except:
            pass


def send(from_address, to_addresses, subject, body):
    # Deprecated.
    sendmail(from_address, to_addresses, subject, body)
