# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import sys
import time
import logging

import subprocess as sp
import getpass

import configobj
import validate
import json
import requests

from commodity.os_ import check_output
from commodity.pattern import MetaBunch
from commodity.str_ import Printable
from commodity.os_ import resolve_path

import bitbucket.exceptions as exc

BB_HTTP_BASE = 'https://{credentials}bitbucket.org/{owner}/{repo}/'
BB_SSH_BASE = 'ssh://hg@bitbucket.org/{owner}/{repo}/'
BB_API = 'https://api.bitbucket.org/1.0/{path}'

USERDIR = os.environ['HOME']
BUCKETCONFIG = os.path.join(USERDIR, '.bucket')
BUCKETSPECS = resolve_path('config.spec', ['.', '/usr/lib/bucket'])[0]


def get_password(username):
    return getpass.getpass("{0}'s password: ".format(username))


class Credentials(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Account(Printable):
    def __init__(self, accounts, account, get_pass_cb=get_password):
        self.accounts = accounts
        self.get_pass = get_pass_cb
        self.username = None
        self.password = None
        self.load(account)

    def load(self, account):
        # explicit account
        if account and ':' in account:
            return self._get_account(account)

        if account is None:
            account = 'default'
            if not self._has_account(account):
                return self._get_account(None)

        if not self._has_account(account):
            return self._get_account(account)

        return self._get_account_by_label(account)

    def _get_account_by_label(self, label):
        user_pass = self.accounts[label]
        return self._get_account(user_pass)

    def _get_account(self, user_and_pass):
        if user_and_pass is None:
            return None

        try:
            username, password = user_and_pass.split(':')
        except ValueError:
            username, password = user_and_pass, None

        if not password:
            password = self.get_pass(username)

        self.username = username
        self.password = password

    def _has_account(self, label):
        if label is None:
            return False

        return label in self.accounts

    def __nonzero__(self):
        return self.username is not None

    def __unicode__(self):
        return u"<Account %s:%s>" % (self.username, self.password)


class Config(MetaBunch):
    def __init__(self):
        cobj = configobj.ConfigObj(configspec=BUCKETSPECS)
        cobj.validate(validate.Validator(), copy=True)
        MetaBunch.__init__(self, cobj)
        self.accounts = {}

    def load(self, data):
        if data is None:
            return

        self.dct.merge(configobj.ConfigObj(data))

    def resolve(self):
        self.account = Account(self.accounts, self.account)
        self.repo_clone.destdir = os.path.expanduser(self.repo_clone.destdir)

    def __str__(self):
        retval = '<Config\n'
        for key, item in self.items():
            retval += "  %s: %s\n" % (key, repr(item))
        return retval


def exec_command(cmd):
    try:
        check_output(cmd.split(), stderr=sp.STDOUT)
    except sp.CalledProcessError, e:
        raise exc.CommandError(e)


def reply2json(req, ok=None, errors=None):

    def raise_error(error):
        e = error[0]
        args = error[1:]
        raise e(*args)

    ok = ok or 200
    errors = errors or {}

    if req.status_code != ok:
        raise_error(errors[req.status_code])

    if not req.content:
        return None

    return json.loads(req.content)


def bb_api_uri(path):
    uri = BB_API.format(path=path)
    return uri


def bb_http_uri(**kargs):
    uri = BB_HTTP_BASE.format(**kargs)
    return uri


def bb_ssh_uri(**kargs):
    uri = BB_SSH_BASE.format(**kargs)
    return uri


class Session(object):
    def __init__(self, credentials=None, logger=None):
        self.credentials = credentials
        self.timeout = 10
        self._http_session = None
        self.logger = logger or logging.getLogger()

        self.user = None
        if self.credentials is not None:
            self.user = self.credentials.username

    def auth(self):
        if not self.credentials:
            return None

        return (self.credentials.username, self.credentials.password)

    @property
    def http_session(self):
        if self._http_session is not None:
            return self._http_session

        self._http_session = requests.session(auth=self.auth(), timeout=self.timeout)
        self._http_session.config['prefetch'] = True

        if self.logger.level == logging.DEBUG:
            self._http_session.config['verbose'] = sys.stderr

        if self.credentials:
            self.test_auth()

        return self._http_session

    def test_auth(self):
        errors = {
            400: [exc.InvalidOrAlreadyRegisteredSSHkey],
            401: [exc.InvalidCredentials]}

        self.http_get('ssh-keys', errors=errors)

    def request(self, method, path, data=None, ok=None, errors=None):
        while 1:
            try:
                reply = self.http_session.request(method, bb_api_uri(path), data=data)
                retval = reply2json(reply, ok=ok, errors=errors)
                break

            except exc.ServiceUnavailable:
                time.sleep(1)

            except requests.exceptions.ConnectionError, e:
                self.logger.error(e)
                sys.exit(1)

        return retval

    def http_get(self, path, **kargs):
        return self.request('get', path, **kargs)

    def http_put(self, path, **kargs):
        return self.request('put', path, **kargs)

    def http_post(self, path, **kargs):
        return self.request('post', path, **kargs)

    def http_delete(self, path, **kargs):
        return self.request('delete', path, **kargs)

    def create_ssh_key_manager(self):
        return SshKeyManager(self)

    def create_repo_manager(self, **kargs):
        return RepoManager(self, **kargs)

    def __repr__(self):
        return "<Session credentials:%s>" % self.credentials


class SshKeyManager:
    def __init__(self, session):
        self.session = session

    def list_keys(self):
        return self.session.http_get('ssh-keys')

    def list_key_labels(self):
        return [x['label'] for x in self.list_keys()]

    def list_key_summaries(self):
        retval = []

        template = "pk: {pk:>8} |  label: {label:<12} |  {key_summary}"
        for key in self.list_keys():
            retval.append(template.format(label=key['label'],
                                          pk=key['pk'],
                                          key_summary=self._key_summary(key['key'])))
        return retval

    def _key_summary(self, keycontent):
        fields = keycontent.split()
        proto = seq = host = ''
        try:
            proto = fields[0]
            seq = fields[1]
            host = fields[2]
        except IndexError:
            pass

        return "{0} {1}...{2} {3}".format(proto, seq[:12], seq[-12:], host)

    def add_key(self, label, keyfile):
        errors = {
            400: [exc.InvalidOrAlreadyRegisteredSSHkey],
            401: [exc.InvalidCredentials]}

        retval = self.session.http_post(
            'ssh-keys', data=dict(label=label, key=keyfile.read()), errors=errors)
        return retval['pk']

    def delete_key_by_id(self, pk):
        errors = {
            404: [exc.NoSuchKey, pk]}

        self.session.http_delete('ssh-keys/%s' % pk, ok=204, errors=errors)

    def find_key_by_label(self, label):
        for key in self.list_keys():
            if key['label'] == label:
                return key['pk']

        return None

    def delete_key_by_label(self, label):
        pk = self.find_key_by_label(label)
        if pk is None:
            raise exc.NoSuchKey(label)

        self.delete_key_by_id(pk)


class FieldManager(object):
    def __init__(self, manager, name):
        self.manager = manager
        self.name = name

    @property
    def _repo_fields(self):
        return self.manager.get_repo_fields(self.name)

    def __getitem__(self, key):
        return self._repo_fields[key]

    def __setitem__(self, key, value):
        self.manager.set_repo_field(self.name, key, value)

    def keys(self):
        return self._repo_fields.keys()

    def copy(self):
        return self._repo_fields.copy()

    def __repr__(self):
        return str(self._repo_fields)


class Repo(object):
    def __init__(self, name, repo_manager):
        self.name = name
        self.repo_manager = repo_manager
        self.session = repo_manager.session
        self.owner = repo_manager.owner
        self._uri = None

        self.uri_factories = {
            'http': self.bb_http_uri,
            'ssh': self.bb_ssh_uri}

        self.fields = FieldManager(repo_manager, name)
        self.logger = self.repo_manager.logger

    @property
    def uri(self):
        if self._uri is None:
            proto = self.repo_manager.proto
            return self.uri_factories[proto]()

        return self._uri

    # FIXME: property
    def bb_http_uri(self):
        kargs = dict(credentials='', owner=self.owner, repo=self.name)
        if self.fields['is_private']:
            kargs['credentials'] = '{0}:{1}@'.format(*self.session.auth())

        return bb_http_uri(**kargs)

    # FIXME: property
    def bb_ssh_uri(self):
        kargs = dict(owner=self.owner, repo=self.name)
        return bb_ssh_uri(**kargs)

    def assure_local_copy(self, path):
        if not self.have_local_copy(path):
            raise exc.NotLocalCopy(self.name)

    def have_local_copy(self, path):
        raise NotImplemented

    def __unicode__(self):
        return u"%s/%s" % (self.owner, self.fields['slug'])

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, unicode(self))

    def clone(self, path):
        raise NotImplementedError

    def update(self, path):
        raise NotImplementedError


class MercurialRepo(Repo):
    # FIXME: assert it is the same repository
    def have_local_copy(self, path):
        """
        have_local_copy(str) -> boolean

        Return True if there is a repository in 'path'
        """
        return os.path.isdir(os.path.join(path, self.name, '.hg'))

    def clone(self, path):
        "Clone repository to the specified destination 'path'"
        exec_command("hg clone %s %s/%s" % (self.uri, path, self.name))
        self.logger.info(u'cloned: %s', self)

    def update(self, path):
        "Update repository in the downloaded in the specified 'path'"
        self.assure_local_copy(path)
        exec_command("hg -R %s/%s pull %s -u" % (path, self.name, self.uri))
        self.logger.info(u'updated: %s', self)


class GitRepo(Repo):
    def have_local_copy(self, path):
        return os.path.isdir(os.path.join(path, self.name, '.git'))

    def clone(self, path):
        exec_command("git clone %s %s/%s" % (self.uri, path, self.name))
        self.logger.info(u'cloned: %s', self)

    def update(self, path):
        exec_command("git --git-dir %s/%s/.git pull" % (path, self.name))
        self.logger.info(u'updated: %s', self)


class UserOverview:
    def __init__(self, data):
        self.repos = {}
        for info in data['repositories']:
            self.repos[info['slug']] = info


class RepoManager:
    repo_classes = {'hg': MercurialRepo, 'git': GitRepo}

    def __init__(self, session=None, owner=None, proto='http'):
        self.session = session or Session()
        self.owner = owner or self.session.user
        self.proto = proto

        if self.owner is None or '/' in self.owner:
            raise exc.OwnerRequired

        self._overview = None
        self.logger = self.session.logger

    @property
    def overview(self):
        if self._overview is None:
            self._overview = UserOverview(
                self.session.http_get('users/{0}'.format(self.owner)))

        return self._overview

    def invalidate_cache(self):
        self._overview = None

    def get_repo_fields(self, reponame):
        if reponame not in self.overview.repos:
            raise exc.RepositoryNotFound(reponame)

        return self.overview.repos[reponame]

    def set_repo_field(self, name, key, value):
        self.session.http_put('repositories/%s/%s' % (self.owner, name),
                              data={key: value})

    def get_repo(self, name):
        if name not in self.overview.repos.keys():
            raise exc.RepositoryNotFound(name)

        scm = self.overview.repos[name]['scm']
        return self.repo_classes[scm](name, self)

    def get_repos(self, names=None):
        names = names or self.list_names()
        return [self.get_repo(x) for x in names]

    def list_names(self):
        return sorted(self.overview.repos.keys())

    def repo_exists(self, name):
        return name in self.list_names()

    def create_repo(self, name, scm='hg', private=True):
        errors = {
            400: [exc.RepositoryAlreadyExists, name],  # FIXME: incorrect user too
            401: [exc.InvalidCredentials],
            403: [exc.Forbidden]}

        data = dict(owner=self.owner, name=name, scm=scm,
                    is_private=str(bool(private)))
        self.session.http_post('repositories', data=data, errors=errors)
        self.invalidate_cache()
        return self.get_repo(name)

    def delete_repo(self, name):
        errors = {
            403: [exc.Forbidden, name],
            404: [exc.RepositoryNotFound, name]}

        data = dict(owner=self.owner)
        self.session.http_delete('repositories/%s/%s' % (self.owner, name),
                                 ok=204, data=data, errors=errors)
        self.invalidate_cache()

    def create_repo_mirror(self, target):
        return RepoMirror(self, target)


class RepoMirror:
    def __init__(self, repo_manager, target):
        self.repo_manager = repo_manager
        assert target and os.path.isdir(target), target
        self.path = target
        self.logger = repo_manager.logger

    def clone(self, repo):
        assert isinstance(repo, Repo)
        repo.clone(self.path)

    def update(self, repo):
        repo.update(self.path)

    def sync(self, *repos):
        for repo in repos:
            try:
                self.sync_single(repo)
            except exc.CommandError as e:
                self.logger.error(e)

    def sync_single(self, repo):
        if not repo.have_local_copy(self.path):
            repo.clone(self.path)
        else:
            repo.update(self.path)

    def sync_all(self):
        repos = self.repo_manager.get_repos()
        self.sync(*repos)
