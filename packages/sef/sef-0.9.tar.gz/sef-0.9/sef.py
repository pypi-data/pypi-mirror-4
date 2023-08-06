import os
import shlex

__all__ = ['set_defaults']


class EnvReader(object):
    def set_environ(self, lines):
        for key, value in self.dict(lines).items():
            os.environ.setdefault(key, value)

    def dict(self, lines):
        env = {}
        for line in lines:
            if self.is_empty(line):
                continue
            key, value = self.key_value_from_line(line)
            env[key] = value
        return env

    def key_value_from_line(self, line):
        key_str, separator, value_str = line.partition('=')
        key = shlex.split(key_str, comments=False, posix=False)
        value = shlex.split(value_str, comments=True, posix=True)
        if len(key) != 1 or len(value) != 1:
            raise Exception('Bad format: %s' % line)
        return key[0], value[0]

    def is_empty(self, line):
        stripped = line.strip()
        return stripped == '' or stripped.startswith('#')


def read_lines(file):
    if isinstance(file, basestring):
        try:
            with open(file) as fp:
                return fp.readlines()
        except IOError:
            return []
    else:
        return file.readlines()


def set_defaults(file):
    lines = read_lines(file)
    reader = EnvReader()
    reader.set_environ(lines)
