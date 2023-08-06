import os
from dm.exceptions import DictionaryDefinitionError
from dm.exceptions import FilePermissionError
import stat
import commands

class DictionaryDef(str):

    purpose = 'setting'

    def __new__(cls, arg, **kwds):
        return str.__new__(cls, arg)
        
    def __init__(self, arg, purpose=None, default=None):
        super(DictionaryDef, self).__init__()
        if purpose != None:
            self.purpose = purpose
        if default != None:
            self.default = default

    def check(self, value, dictionary):
        self.test(value, dictionary)
        return "%s: %s %s: %s" % (self, self.purpose, 'ok', value)

    def test(self, value, dictionary):
        pass

    def fail(self, failure, value):
        msg = "%s: %s %s: %s" % (self, self.purpose, failure, value)
        raise DictionaryDefinitionError, msg


class StringSetting(DictionaryDef):

    def test(self, value, dictionary):
        super(StringSetting, self).test(value, dictionary)
        if not isinstance(value, basestring):
            self.fail('not a string', value)


class DatabaseNameSetting(DictionaryDef):

    purpose = 'database name'

    def test(self, value, dictionary):
        super(DatabaseNameSetting, self).test(value, dictionary)
        if dictionary['db.type'] == 'sqlite':
            # Check the value is a path that has a file.
            DatabaseFileSetting(self).test(value, dictionary)
            if not os.path.isfile(value):
                self.fail('no file found', value)


class PathSetting(StringSetting):

    purpose = 'file or directory'

    def test(self, value, dictionary):
        super(PathSetting, self).test(value, dictionary)
        if not os.path.exists(value):
            self.fail('not found', value)

    def getFilePermissions(self, path):
        return os.stat(path).st_mode & 0o777


class DirSetting(PathSetting):

    purpose = 'directory'

    def test(self, value, dictionary):
        super(DirSetting, self).test(value, dictionary)
        if not os.path.isdir(value):
            self.fail('not a directory', value)


class DavLockSetting(PathSetting):

    purpose = 'dav lock DB'

    def test(self, value, dictionary):
        lockDbPath = value
        lockDirPath = os.path.dirname(lockDbPath)
        super(DavLockSetting, self).test(lockDirPath, dictionary)
        if not os.path.isdir(lockDirPath):
            self.fail('not a directory', lockDirPath)
        try:
            path = lockDirPath
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "log directory not readable by user: %s" % path
            if not mode & stat.S_IWUSR:
                raise FilePermissionError, "log directory not writable by user: %s" % path
            if not mode & stat.S_IXUSR:
                raise FilePermissionError, "log directory not executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "log directory not readable by group: %s" % path
            if not mode & stat.S_IWGRP:
                raise FilePermissionError, "log directory not writable by group: %s" % path
            if not mode & stat.S_IXGRP:
                raise FilePermissionError, "log directory not executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "log directory readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "log directory writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "log directory executable by other: %s" % path
            child = path
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "%s permission error: %s" % (self.purpose, inst)
            raise DictionaryDefinitionError, msg


class FileSetting(PathSetting):

    purpose = 'file'
    umask = None

    def __init__(self, arg, umask=None, **kwds):
        super(FileSetting, self).__init__(arg, **kwds)
        self.umask = umask

    def test(self, value, dictionary):
        super(FileSetting, self).test(value, dictionary)
        if not os.path.isfile(value):
            self.fail('not a file', value)
        try:
            self.assertFileFitsUmask(value, dictionary)
        except FilePermissionError, inst:
            self.fail(inst, value)

    def isExecutableByUser(self, value):
        return os.stat(value).st_mode & stat.S_IXUSR

    def isExecutableByGroup(self, value):
        return os.stat(value).st_mode & stat.S_IXGRP

    def isWritableByOther(self, value):
        return os.stat(value).st_mode & stat.S_IWOTH

    def isExecutableByOther(self, value):
        return os.stat(value).st_mode & stat.S_IXOTH


    filePermissions = {
        'readable by user': stat.S_IRUSR,
        'writable by user': stat.S_IWUSR,
        'executable by user': stat.S_IXUSR,
        'readable by group': stat.S_IRGRP,
        'writable by group': stat.S_IWGRP,
        'executable by group': stat.S_IXGRP,
        'readable by others': stat.S_IROTH,
        'writable by others': stat.S_IWOTH,
        'executable by others': stat.S_IXOTH,
    }

    def assertFileFitsUmask(self, path, dictionary):
        mode = os.stat(path).st_mode
        umask = self.umask != None and self.umask or dictionary.getUmask()
        conflict = mode & 0777 & umask
        if conflict:
            names = []
            items = self.filePermissions.items()
            items.sort()
            items.reverse()
            for name, value in items:
                if value & conflict:
                    names.append(name)
            msg = "permissions conflict with umask of '0o%o' (bits '0o%o': %s)" % (umask, conflict, ", ".join(names))
            raise FilePermissionError, msg


class ExecutableFileSetting(FileSetting):

    purpose = 'executable file'

    def test(self, value, dictionary):
        super(ExecutableFileSetting, self).test(value, dictionary)
        if not self.isExecutableByUser(value):
            self.fail('not executable by user', value)
        if stat.S_IXGRP & ~ dictionary.getUmask():
            if not self.isExecutableByUser(value):
                self.fail('not executable by group', value)



class NonExecutableFileSetting(FileSetting):

    purpose = 'non-executable file'

    def test(self, value, dictionary):
        super(NonExecutableFileSetting, self).test(value, dictionary)
        if self.isExecutableByUser(value):
            self.fail('executable by user', value)
        if self.isExecutableByGroup(value):
            self.fail('executable by group', value)
        if self.isExecutableByOther(value):
            self.fail('executable by other', value)


class ConfigFileSetting(PathSetting):

    purpose = 'config file'

    def test(self, value, dictionary):
        super(ConfigFileSetting, self).test(value, dictionary)
        path = value
        try:
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "file not readable by user: %s" % path
            if mode & stat.S_IXUSR:
                raise FilePermissionError, "file executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "file not readable by group: %s" % path
            if mode & stat.S_IWGRP:
                raise FilePermissionError, "file writable by group: %s" % path
            if mode & stat.S_IXGRP:
                raise FilePermissionError, "file executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "file readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "file writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "file executable by other: %s" % path
            child = path
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "%s permission error: %s" % (self.purpose, inst)
            raise DictionaryDefinitionError, msg


class GroupWritableFileSetting(PathSetting):

    purpose = 'group-writable file'

    def test(self, value, dictionary):
        super(GroupWritableFileSetting, self).test(value, dictionary)
        path = value
        try:
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "file not readable by user: %s" % path
            if not mode & stat.S_IWUSR:
                raise FilePermissionError, "file not writable by user: %s" % path
            if mode & stat.S_IXUSR:
                raise FilePermissionError, "file executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "file not readable by group: %s" % path
            if not mode & stat.S_IWGRP:
                raise FilePermissionError, "file not writable by group: %s" % path
            if mode & stat.S_IXGRP:
                raise FilePermissionError, "file executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "file readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "file writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "file executable by other: %s" % path
            child = path
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "%s permission error: %s" % (self.purpose, inst)
            raise DictionaryDefinitionError, msg


class AutoGeneratedConfigFileSetting(GroupWritableFileSetting):

    purpose = 'auto-generated config file'


class DatabaseFileSetting(GroupWritableFileSetting):

    purpose = 'database file'


class LogFileSetting(GroupWritableFileSetting):

    purpose = 'log file'


class RotatingLogFileSetting(PathSetting):

    purpose = 'rotating log file'

    def test(self, value, dictionary):
        super(RotatingLogFileSetting, self).test(value, dictionary)
        path = value
        try:
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "file not readable by user: %s" % path
            if not mode & stat.S_IWUSR:
                raise FilePermissionError, "file not writable by user: %s" % path
            if mode & stat.S_IXUSR:
                raise FilePermissionError, "file executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "file not readable by group: %s" % path
            if not mode & stat.S_IWGRP:
                raise FilePermissionError, "file not writable by group: %s" % path
            if mode & stat.S_IXGRP:
                raise FilePermissionError, "file executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "file readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "file writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "file executable by other: %s" % path
            # Check log directory.
            path = os.path.dirname(path)
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "log directory not readable by user: %s" % path
            if not mode & stat.S_IWUSR:
                raise FilePermissionError, "log directory not writable by user: %s" % path
            if not mode & stat.S_IXUSR:
                raise FilePermissionError, "log directory not executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "log directory not readable by group: %s" % path
            if not mode & stat.S_IWGRP:
                raise FilePermissionError, "log directory not writable by group: %s" % path
            if not mode & stat.S_IXGRP:
                raise FilePermissionError, "log directory not executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "log directory readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "log directory writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "log directory executable by other: %s" % path
            child = path
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "%s permission error: %s" % (self.purpose, inst)
            raise DictionaryDefinitionError, msg


class WsgiScriptSetting(PathSetting):

    purpose = 'wsgi script'

    def test(self, value, dictionary):
        super(WsgiScriptSetting, self).test(value, dictionary)
        path = value
        try:
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "file not readable by user: %s" % path
            if mode & stat.S_IXUSR:
                raise FilePermissionError, "file executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "file not readable by group: %s" % path
            if mode & stat.S_IWGRP:
                raise FilePermissionError, "file writable by group: %s" % path
            if mode & stat.S_IXGRP:
                raise FilePermissionError, "file executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "file readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "file writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "file executable by other: %s" % path
            child = path
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "%s permission error: %s" % (self.purpose, inst)
            raise DictionaryDefinitionError, msg


class CgiScriptSetting(PathSetting):

    purpose = 'cgi script'

    def test(self, value, dictionary):
        super(CgiScriptSetting, self).test(value, dictionary)
        path = value
        try:
            mode = self.getFilePermissions(path)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "file not readable by user: %s" % path
            if not mode & stat.S_IXUSR:
                raise FilePermissionError, "file not executable by user: %s" % path
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "file not readable by group: %s" % path
            if mode & stat.S_IWGRP:
                raise FilePermissionError, "file writable by group: %s" % path
            if not mode & stat.S_IXGRP:
                raise FilePermissionError, "file not executable by group: %s" % path
            if mode & stat.S_IROTH:
                raise FilePermissionError, "file readable by other: %s" % path
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "file writable by other: %s" % path
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "file executable by other: %s" % path
            child = path
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "%s permission error: %s" % (self.purpose, inst)
            raise DictionaryDefinitionError, msg



class UmaskSetting(DictionaryDef):

    purpose = 'umask'

    def test(self, value, dictionary):
        super(UmaskSetting, self).test(value, dictionary)
        try:
            self.parse(value)
        except:
            self.fail('not an octal', value)

    def parse(self, value):
        try:
            value = int(value, base=8)
        except Exception, inst:
            msg = "Setting for '%s' doesn't appear to be in base 8: %s: %s" % (self, value, inst)
            raise Exception, msg
        return value


class DomainNameSetting(DictionaryDef):

    purpose = 'domain name'


class ShellCmdSetting(DictionaryDef):

    purpose = 'shell command'


class SystemUserSetting(DictionaryDef):

    purpose = 'system user'


class CommaSeparatedListSetting(DictionaryDef):

    purpose = 'comma separated list'

    def parse(self, value):
        return [i.strip() for i in value.split(',')]

