import ConfigParser
import collections
import datetime
import json
import optparse
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import logging

from distchecker import describepython

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CmdOutput = collections.namedtuple('CmdOutput', 'stdout stderr')


class NonZeroStatusError(OSError):

    def __init__(self, cmd, status):
        self.cmd = cmd
        self.status = status

    def __str__(self):
        return ('"%i" status code while '
                'running command: %s' % (self.status, self.cmd))


class FileHandler(collections.namedtuple('FileHandler', 'source name size')):

    _openfile = open

    def open(self):
        if isinstance(self.source, tuple) \
                and hasattr(self.source[0], 'extractfile'):
            return self.source[0].extractfile(self.source[1])
        return self._openfile(self.source)


def config_to_dict(config):
    d = {}
    for section in config.sections():
        d[section] = subdict = {}
        for k, v in config.items(section):
            subdict[k] = v
    return d


class EntryComparer(object):

    def compare_configs(self, entry1, entry2):
        config1 = ConfigParser.ConfigParser()
        config1.readfp(entry1.open(), str(entry1.source))

        config2 = ConfigParser.ConfigParser()
        config2.readfp(entry2.open(), str(entry2.source))

        try:
            dict1 = config_to_dict(config1)
            dict2 = config_to_dict(config2)

            if cmp(dict1, dict2) != 0:
                return ('different configs', entry1.name)
        except:
            pass

        if entry2.size != entry1.size:
            return ('different sizes', entry1.name)

    checks = {
        'setup.cfg': compare_configs,
        '.ini': compare_configs,
        }

    def compare(self, entry1, entry2):
        for k, v in self.checks.items():
            if entry1.name.endswith(k):
                return v(self, entry1, entry2)
        if entry2.size != entry1.size:
            return ('different sizes', entry1.name)

compare_entries = EntryComparer().compare


def clone_config(config):
    newconfig = ConfigParser.RawConfigParser()
    for section in config.sections():
        newconfig.add_section(section)
        for opt in config.options(section):
            newconfig.set(section, opt, config.get(section, opt))
    return newconfig


def find_python_execs():
    '''Look at the OS path and find anything that looks like
    a python executable.
    '''

    python_execs = []
    exec_re = re.compile('^python[0-9.]*$')
    for x in os.environ['PATH'].split(os.pathsep):
        for f in os.listdir(x):
            if exec_re.search(f) is not None:
                full = os.path.join(x, f)
                if full not in python_execs:
                    python_execs.append(full)
    return tuple(python_execs)


def indent(s, spaces=2):
    res = []
    for x in s.split('\n'):
        res.append(' ' * spaces + x)
    return '\n'.join(res)


class ProcessRunner(object):

    _call = staticmethod(subprocess.call)

    def run(self, s, capture=False):
        if isinstance(s, basestring):
            cmd = s.split(' ')
        else:
            cmd = list(s)

        if capture:
            stdout = tempfile.NamedTemporaryFile()
            stderr = tempfile.NamedTemporaryFile()
            logger.debug('=== Running: %s' % cmd)
            ret = self._call(cmd, stdout=stdout, stderr=stderr)
            stdout.seek(0)
            stderr.seek(0)
            data = CmdOutput(stdout.read(), stderr.read())
            stdout.close()
            stderr.close()

            if ret > 0:
                logging.error('stdout=' + data.stdout)
                logging.error('stderr=' + data.stderr)
                raise NonZeroStatusError(s, ret)
            return data
        else:
            logging.debug('=== Running: %s' % cmd)
            if self._call(cmd) > 0:
                print 'Received error'
                raise OSError('Error while running command: %s' % s)

    def get_osinfo(self):
        full = list(os.uname())
        s = self.run('cat /etc/lsb-release', True).stdout.strip()
        distrib = {}
        for x in s.split('\n'):
            k, v = x.split('=', 1)
            distrib[k] = v
        full += [distrib['DISTRIB_ID'],
                 distrib['DISTRIB_RELEASE'],
                 distrib['DISTRIB_CODENAME'],
                 distrib['DISTRIB_DESCRIPTION']]

        return OSInfo(*full)

OSInfo = collections.namedtuple(
    'OSInfo', ('sysname nodename release version machine '
               'distrib_id distrib_release distrib_codename '
               'distrib_description'))


class VirtualEnv(object):

    def __init__(self, path, processrunner=None):
        self.path = path
        self.processrunner = processrunner or ProcessRunner()

    @classmethod
    def create_temp(cls, virtualenvpath, python_exec,
                    processrunner=None):
        tempdir = tempfile.mkdtemp('-tmp', 'scripts-')
        return cls.create(virtualenvpath, python_exec, tempdir + '/ve',
                          processrunner)

    @classmethod
    def create(cls, virtualenvpath, python_exec, path,
               processrunner=None):

        processrunner = processrunner or ProcessRunner()
        ve = cls(path, processrunner)
        if virtualenvpath is None:
            raise OSError('Please declare path to virtualenv.py '
                          'in ~/.distchecker')
        processrunner.run('%s %s --no-site-packages %s' % (python_exec,
                                                           virtualenvpath,
                                                           ve.path))
        return ve

    @property
    def python_exec(self):
        return self.path + '/bin/python'

    def python(self, cmd, *args, **kwargs):
        return self.processrunner.run(
            self.python_exec + ' ' + cmd, *args, **kwargs)

    def pip(self, cmd, *args, **kwargs):
        extra = 'file://' + os.path.join(os.environ['HOME'],
                                         '.distchecker-extras')
        return self.processrunner.run(
            self.path + '/bin/pip ' + cmd + ' -f ' + extra, *args, **kwargs)

    def run(self, cmd, *args, **kwargs):
        return self.processrunner.run(
            self.path + '/bin/' + cmd, *args, **kwargs)

    def get_eggs(self):
        return self.pip('freeze', True).stdout.strip()

    def get_info(self):
        pe = describepython.PythonEnvironment(self.python_exec)
        pe.prefetch()
        s = ''
        for k in pe._fields:
            v = getattr(pe, k)
            s += '%s: %s\n' % (k, v)

        return s


class Dist(object):
    DEFAULT_PYTHON_EXEC = None

    _chdir = staticmethod(os.chdir)

    def __init__(self, path, python_exec, processrunner):
        self.path = path
        self.python_exec = python_exec
        self.processrunner = processrunner

    def _setuppy(self, cmd):
        cwd = os.getcwd()
        self._chdir(self.path)
        res = self.processrunner.run(
            self.python_exec + ' setup.py ' + cmd, True).stdout.strip()
        self._chdir(cwd)
        return res

    @property
    def name(self):
        if not hasattr(self, '_name'):
            self._name = self._setuppy('--name')
        return self._name

    @property
    def version(self):
        if not hasattr(self, '_version'):
            self._version = self._setuppy('--version')
        return self._version

    def create_sdist(self):
        self._setuppy('sdist --formats=gztar')
        return '%s/dist/%s-%s.tar.gz' % (self.path, self.name, self.version)

    @property
    def packages(self):
        if not hasattr(self, '_packages'):
            cwd = os.getcwd()
            self._chdir(self.path)
            location = '.'
            if os.path.exists('src'):
                location = 'src'
            cmd = [self.python_exec, '-c']
            cmd.append("from setuptools import find_packages; "
                       "print find_packages('%s')" % location)
            s = self.processrunner.run(cmd, capture=True).stdout.strip()
            s = s.replace("'", '"')  # json doesn't like single quotes
            self._packages = json.loads(s)
            self._chdir(cwd)
        return self._packages

entries_to_exclude = [re.compile('~$'),
                      re.compile('.pyc$'),
                      re.compile('^[.]'),
                      re.compile('^PKG-INFO$'),
                      re.compile('[.]egg-info/'),
                      re.compile('^docs/_'),  # sphinx doc build files
                      re.compile('^build/'),  # sphinx doc build files
                      re.compile('^dist/')]


class DistChecker(object):

    init_logging = staticmethod(logging.basicConfig)
    actions = {}
    logger = logger
    processrunner = ProcessRunner()

    opentarfile = staticmethod(tarfile.open)
    _chdir = staticmethod(os.chdir)

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.homedir = os.environ.get('HOME', '/')
        if os.path.exists(os.path.join(self.homedir, '.distchecker')):
            self.config.read(os.path.join(self.homedir, '.distchecker'))

        if self.config.has_option('pythons', 'default'):
            self.python_exec = self.config.get_option('pythons', 'default')
            self.DEFAULT_PYTHON_EXEC = self.python_exec
        else:
            execs = find_python_execs()
            if len(execs) == 0:
                raise OSError('Could not find any python executables '
                              'on the path')
            self.DEFAULT_PYTHON_EXEC = self.python_exec = execs[0]

    def action_test_sdist(self, args):
        if self.config.has_option('general', 'virtualenv'):
            vebin = self.config.get('general', 'virtualenv')
        else:
            try:
                import virtualenv
                vebin = virtualenv.__file__
                if vebin.endswith('.pyc'):
                    vebin = vebin[:-1]
            except ImportError, ex:
                pass
        ve = VirtualEnv.create_temp(vebin, self.python_exec)

        # args[0] should be the path to a project
        if len(args) > 0:
            self._chdir(args[0])

        dist = Dist('.', ve.python_exec, ve.processrunner)

        if len(dist.packages) < 1:
            raise ValueError('packages is empty')

        sdist = dist.create_sdist()

        ve.pip('install %s' % sdist)
        freeze = ve.get_eggs()
        ve.pip('install nose coverage')

        cmd = 'nosetests --with-coverage --cover-inclusive'
        for x in dist.packages:
            cmd += ' --cover-package=' + x
        try:
            coverage = ve.run(cmd, True).stderr.strip()
        except NonZeroStatusError, ex:
            self.logger.error(str(ex))
            coverage = "Test errors are present"

        osinfo = self.processrunner.get_osinfo()._asdict()
        osinfo_s = ''
        for k, v in osinfo.items():
            osinfo_s += '%s: %s\n' % (k, v)
        describe = ve.get_info()

        self.logger.info('''; -*-rst-*-
**Date:**  %(now)s

Test Coverage
=============

::
%(coverage)s

Python Info
===========

::
%(describe)s

OS Info
=======

::
%(osinfo)s

Installed Eggs
==============

::
%(freeze)s
''' % {'coverage': indent(coverage),
       'describe': indent(describe),
       'osinfo': indent(str(osinfo_s)),
       'now': datetime.datetime.now(),
       'freeze': indent(freeze)})

        return ve

    actions['test_sdist'] = action_test_sdist

    def action_test_paster_template(self, args):
        if len(args) < 2:
            print 'Usage: test_paster_template <sdist> <template_name>'
            return
        ve = self.action_test_sdist([args[0]])
        self._chdir(ve.path)
        ve.run('paster create -t %s Something' % args[1])
        self._chdir('Something')
        ve.pip('install -e .')
        ve.python('setup.py test')

    actions['test_paster_template'] = action_test_paster_template

    def action_compare_sdist(self, args=()):
        local = {}
        path = os.getcwd()
        if len(args) > 0:
            path = args[0]
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                name = full[len(path) + 1:]

                exclude = False
                for r in entries_to_exclude:
                    if r.search(name) is not None:
                        exclude = True
                        break
                if not exclude:
                    local[name] = fh = FileHandler(full, name,
                                                   os.path.getsize(full))

        working = dict(local)
        distro = Dist(path, self.python_exec, self.processrunner)
        f = distro.create_sdist()
        tarball = self.opentarfile(f, 'r:gz')
        bad = []
        for tarentry in tarball:
            if tarentry.isfile():
                fulln = '%s-%s' % (distro.name, distro.version)
                name = tarentry.name[len(fulln) + 1:]
                exclude = False
                for r in entries_to_exclude:
                    if r.search(name) is not None:
                        exclude = True
                        break
                if exclude:
                    continue
                localf = working.get(name, None)
                if localf is None:
                    bad.append(('extra', name))
                    continue
                del working[name]

                fh = FileHandler((tarball, tarentry),
                                 tarentry.name, tarentry.size)
                res = compare_entries(localf, fh)
                if res is not None:
                    bad.append(res)

        for name, sz in working.items():
            bad.append(('missing', name))

        tarball.close()

        self.logger.info('Source 1: dir: ' + str(path))
        self.logger.info('Source 2: tarfile: ' + str(f))
        for x in sorted(bad):
            self.logger.info(str(x))
        if not bad:
            self.logger.info('no differences')

    actions['compare_sdist'] = action_compare_sdist

    def main(self, cmdargs=sys.argv[1:]):
        self.init_logging()
        parser = optparse.OptionParser()
        parser.add_option('', '--setup-config', dest='setup_config',
                          default=False,
                          action='store_true',
                          help=('Generate a default configuration '
                                'for %s/.distchecker' % self.homedir))
        parser.add_option('', '--with-python', dest='with_python',
                          default=self.DEFAULT_PYTHON_EXEC,
                          action='store',
                          help='Which Python interpreter to run command with')
        (options, args) = parser.parse_args(cmdargs)

        self.python_exec = options.with_python

        if options.setup_config:
            newconfig = clone_config(self.config)
            if not newconfig.has_section('general'):
                newconfig.add_section('general')
            if not newconfig.has_section('pythons'):
                newconfig.add_section('pythons')
                execs = find_python_execs()
                for x in execs:
                    newconfig.set('pythons', os.path.basename(x), x)
                if len(execs):
                    raise OSError('Could not find any python '
                                  'executables on the path')
                newconfig.set('pythons', 'default', execs[0])
            if not newconfig.has_option('general', 'pip_download_cache'):
                newconfig.set('general',
                              'pip_download_cache',
                              os.path.join(self.homedir,
                                           '.pip_download_cache'))
            if not newconfig.has_option('general', 'virtualenv'):
                newconfig.set('general', 'virtualenv', '')
            logging.info('Please save the following in: %s'
                         % os.path.join(self.homedir, '.distchecker'))
            newconfig.write(sys.stdout)
            return

        if self.config.has_option('general', 'pip_download_cache'):
            os.environ['PIP_DOWNLOAD_CACHE'] = \
                self.config.get('general', 'pip_download_cache')

        if len(args) > 0 and args[0] in self.actions:
            action = self.actions[args[0]]
            return action(self, args[1:])
        else:
            print
            print 'Commands:'
            print
            for k in self.actions:
                print '  ', k
            print


def main():
    return DistChecker().main()

if __name__ == '__main__':
    main()
