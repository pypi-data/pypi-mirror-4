# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import argparse
import logging

from .api import Config, BUCKETCONFIG


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kargs):
        self.preload = []

        if 'logger' in kargs:
            self.logger = kargs['logger']
            del kargs['logger']
        else:
            self.logger = logging

        kargs['description'] = 'Bitbucket CLI'
        kargs['prog'] = 'bucket'
#        kargs['argument_default'] = argparse.SUPPRESS
        argparse.ArgumentParser.__init__(self, *args, **kargs)

        self.add_argument('-a', '--account', dest='account',
                          help='Account in the form user[:pass]')

        self.add_argument('-c', '--config',
                          help='Read config from specified file')

        self.add_argument('-v', '--verbose', action='count',
                          help='Be verbose')

        self.commands = self.add_subparsers(dest='command', help='commands help')
        self.commands._parser_class = argparse.ArgumentParser

        self.add_command_config()
        self.add_command_ssh()
        self.add_command_list()
        self.add_command_create()
        self.add_command_delete()
        self.add_command_clone()
        self.add_command_sync()

    def add_parser(self, *args, **kargs):
        kargs['argument_default'] = argparse.SUPPRESS
        return self.commands.add_parser(*args, **kargs)

    def add_command_config(self):
        self.add_parser('show-config',
                        help='Show current config')

    def add_command_ssh(self):
        parser = self.add_parser('ssh-ls',
                                 help='List your account SSH keys')

        parser = self.add_parser('ssh-add',
                                 help='Upload a SSH key to your account')
        parser.add_argument('keylabel')
        parser.add_argument('keyfile', type=argparse.FileType('r'))

        parser = self.add_parser('ssh-del',
                                 help='Delete a SSH key by label')
        parser.add_argument('keylabel',
                            help='key label. Run ssh-ls')

    def add_command_list(self):
        parser = self.add_parser('repo-ls', help='List repos')
        parser.add_argument(
            'owner', nargs='?',
            help='Bitbucket repo owner [default:authenticated user]')

        parser.add_argument('-s', '--show-scm',
                            dest='repo_ls.show_scm',
                            action='store_true',
                            help='show SCM')
        parser.add_argument('-d', '--show-desc',
                            dest='repo_ls.show_desc',
                            action='store_true',
                            help='show repo description')
        parser.add_argument('-a', '--show-access',
                            dest='repo_ls.show_access',
                            action='store_true',
                            help='show repo access: private/public')
        parser.add_argument('--public', dest='repo_ls.access',
                            action='store_const', const='public',
                            help='list public repos only')
        parser.add_argument('--private', dest='repo_ls.access',
                            action='store_const', const='private',
                            help='list private repos only')
        parser.add_argument('--hg', dest='repo_ls.scm',
                            action='store_const', const='hg',
                            help='list mercurial repos only')
        parser.add_argument('--git', dest='repo_ls.scm',
                            action='store_const', const='git',
                            help='list git repos only')

    def add_command_create(self):
        parser = self.add_parser('repo-create',
                                 help='Create remote repo')
        parser.add_argument('reponame', metavar='name',
                            help='name of the new repo')
        parser.add_argument('--public', dest='repo_create.private',
                            action='store_false',
                            help='make this repo public')
        parser.add_argument('--private', dest='repo_create.private',
                            action='store_true',
                            help='make this repo private')
        parser.add_argument('--hg', dest='repo_create.scm',
                            action='store_const', const='hg',
                            help='create a mercurial repo')
        parser.add_argument('--git', dest='repo_create.scm',
                            action='store_const', const='git',
                            help='create a git repo')
        parser.add_argument('--clone', dest='repo_create.clone',
                            action='store_true',
                            help='clone newly created repo')

    #FIXME
    def add_command_set(self):
        parser = self.add_parser('repo-set',
                                 help='Change repo config')
        parser.add_argument('reponame', metavar='name',
                            help='name of the new repo')
        parser.add_argument('--public', dest='repo_set.private',
                            action='store_false',
                            help='make this repo public')
        parser.add_argument('--private', dest='repo_set.private',
                            action='store_true',
                            help='make this repo private')

    def add_command_delete(self):
        parser = self.add_parser('repo-del',
                                 help='Delete upstream remote repo (at bitbucket!!)')
        parser.add_argument('reponame', metavar='name',
                            help='name of the repo to delete')

    def add_command_clone(self):
        parser = self.add_parser('repo-clone',
                                 help="Clone remote repo")
        self.add_proto_args(parser, 'repo_clone.proto')

        parser.add_argument('reponame', metavar='repo-name',
                            help='name of the repo to clone')
        parser.add_argument('--destdir', metavar='dirname',
                            dest="repo_clone.destdir",
                            help='where to clone')

    def add_command_sync(self):
        parser = self.add_parser('repo-sync',
                                 help='Sync (clone/update) repos of same owner')
        self.add_proto_args(parser, 'repo_clone.proto')

        parser.add_argument('reponames', metavar='repo-name', nargs='*',
                            default=None,
                            help='repos to sync')
        # FIXME: same of repo-clone??
        parser.add_argument('--destdir', metavar='dirname',
                            dest="repo_clone.destdir",
                            help='where to store repos [default:$(cwd)]')
        parser.add_argument('--all', action='store_true',
                            dest='repo_sync.all',
                            help='clone/update all repos of given owner')
        parser.add_argument('--already', action='store_true',
                            dest='repo_sync.already',
                            help='update local directory repos of given owner')
        parser.add_argument('-o', '--owner', metavar='OWNER',
                            dest='repo_sync.owner',
                            help='repo owner account name [default:authenticated user]')

    def add_proto_args(self, parser, dest):
        parser.add_argument('--ssh', dest=dest,
                            action='store_const', const='ssh',
                            help='use SSH to clone')
        parser.add_argument('--http', dest=dest,
                            action='store_const', const='http',
                            help='use HTTP to clone')

    def get_config_file(self, argv):
        return self.parse_args(argv).config

    def parse(self, argv=None, config=None):
        if isinstance(argv, str):
            argv = argv.split()

        if argv is None:
            argv = sys.argv[1:]

        if config is None:
            config = Config()
            config_file = self.get_config_file(argv) or BUCKETCONFIG
            self.logger.info("loading config from: %s", config_file)
            config.load(config_file)

        self.parse_args(argv, namespace=config)
        config.resolve()
#        print config

        return config
