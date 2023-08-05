# -*- coding:utf-8; tab-width:4; mode:python -*-


def read_file(filename):
    return file(filename).read().strip()


class DummyConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.user = read_file('USER')
        self.pasw = read_file('PASS')

        self.create_config()

    def create_config(self):
        with file(self.filename, 'w') as fd:
            fd.write('''\
[accounts]
default = {0}:{1}
testuser = {0}:{1}
'''.format(self.user, self.pasw))
