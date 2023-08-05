# -*- coding:utf-8; tab-width:4; mode:python -*-


class BBException(Exception):
    def __str__(self):
        return 'bitbucket exception:\n  %s %s' % (self.__class__.__name__, Exception.__str__(self))


class Forbidden(BBException): pass

class RequestError(BBException): pass

class InvalidOrAlreadyRegisteredSSHkey(BBException): pass
class InvalidCredentials(BBException): pass

class RepositoryAlreadyExists(BBException): pass
class RepositoryNotFound(BBException): pass
class NotLocalCopy(BBException): pass
class ServiceUnavailable(BBException): pass
class NoSuchKey(BBException): pass


class OwnerRequired(BBException):
    help = "Must specify an account or repository owner"


class CommandError(BBException):
    pass


#    def __str__(self):
#        ex = self.args[0]
#        cmd = str.join(' ', ex.cmd)
#        return "[%s] %s\n%s\n%s" % (ex.returncode, cmd, ex.output, ex.err)
