from dm.dom.stateful import * 
from dm.ioc import * 

class Captcha(StandardObject):
    "Generated captcha image."
    
    word       = String(default='')
    tryCount   = Integer()

    def isTryCountOK(self):
        tryLimit = 5
        return self.tryCount < tryLimit

    def incTryCount(self):
        self.tryCount = self.tryCount + 1
        self.save()

    def checkWord(self, word):
        self.incTryCount()
        isWord = self.word == word
        if not self.isTryCountOK():
            self.delete()
        return isWord

