from dm.command.base import DomainObjectCreate
from dm.command.base import DomainObjectRead

class CaptchaCreate(DomainObjectCreate):
    "Command to create a captcha."

    def __init__(self, captchaHash, **kwds):
        kwds['name'] = captchaHash
        super(CaptchaCreate, self).__init__(
            typeName='Captcha',
            objectKwds=kwds,
        )

    def execute(self):
        "Make it so."
        super(CaptchaCreate, self).execute()


class CaptchaRead(DomainObjectRead):
    "Command to read a captcha."

    def __init__(self, captchaHash, **kwds):
        kwds['name'] = captchaHash
        super(CaptchaRead, self).__init__(
            typeName='Captcha',
            objectKwds=kwds,
        )

    def execute(self):
        "Make it so."
        super(CaptchaRead, self).execute()

