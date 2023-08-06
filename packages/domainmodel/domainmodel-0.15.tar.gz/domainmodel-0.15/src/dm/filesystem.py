import os
from dm.ioc import *
from dm.dictionarywords import PLUGIN_DIR_PATH
import stat

class FileSystem(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')

    def isFile(self, path):
        return os.path.isfile(self.norm(path))
    
    def readFile(self, path):
        path = self.norm(path)
        fileObject = open(path, 'r')
        return fileObject.read()

    def writeWsgiFile(self, path, content, purpose):
        self.writeFileIfChanged(path, content, purpose)
 
    def writeCgiFile(self, path, content, purpose):
        if self.writeFileIfChanged(path, content, purpose):
            self.makeFileExecutable(path)
 
    def writeFile(self, path, content, purpose, umask=0o027):
        path = self.norm(path)
        parent = os.path.dirname(path)
        oldumask = os.umask(umask)
        try:
            if not os.path.exists(parent):
                os.makedirs(parent)
            content = content.encode('utf-8', 'ignore')
            # Todo: Make this filewriting safer.
            fileObject = open(path, 'w')
            fileObject.write(content)
            fileObject.close()
            self.logger.info("Wrote %s on path: %s" % (purpose, path))
        finally:
            os.umask(oldumask)

    def writeFileIfChanged(self, path, content, purpose):
        if not self.isFile(path) or self.readFile(path) != content:
            self.writeFile(path, content, purpose)
            return True

    def makeFileExecutable(self, path):
        # Read current perms.
        mode = os.stat(path).st_mode & 0o777
        # Add executable bits.
        mode = mode | stat.S_IXUSR | stat.S_IXGRP
        # Set result.
        try:
            os.chmod(path, mode)
        except Exception, inst:
            raise Exception, "Couldn't chmod path: %s: %s" % (path, inst)

    def norm(self, path):
        return os.path.normpath(path)

    def getPluginsPath(self):
        if PLUGIN_DIR_PATH in self.dictionary:
            return self.dictionary[PLUGIN_DIR_PATH]
        else:
            # Todo: Config validation (since it's user input).
            msg = "Missing dictionary word. Try "
            msg += "setting '%s = /path/to/%s' in configuration." % (
                PLUGIN_DIR_PATH, PLUGIN_DIR_PATH
            )
            raise Exception, msg
    
    def getPluginPath(self, plugin):
        "Returns path of directory containing plugin filesystems."
        return os.path.join(self.getPluginsPath(), plugin.name)

# Old name.
class FileSystemPathBuilder(FileSystem):
    pass 
    

