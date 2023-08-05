import unittest
from StringIO import StringIO


class TestNonStatusError(unittest.TestCase):

    def test_it(self):
        from distchecker import NonZeroStatusError
        er = NonZeroStatusError('foo', 1)
        self.assertEqual(er.__str__(),
                         '"1" status code while running command: foo')


class TestFileHandler(unittest.TestCase):

    def test_tarfile(self):
        from distchecker import FileHandler
        marker = object()
        fh = FileHandler((Mock(extractfile=lambda x: marker),
                          Mock()), 'foo', 20)
        self.assertEqual(fh.open(), marker)

    def test_file(self):
        from distchecker import FileHandler
        marker = object()
        fh = FileHandler('somefile', 'foo', 20)
        fh._openfile = lambda x: marker
        self.assertEqual(fh.open(), marker)


class TestConfigToDict(unittest.TestCase):

    def test_it(self):
        from distchecker import config_to_dict
        from ConfigParser import ConfigParser
        config = ConfigParser()
        config.add_section('section1')
        config.set('section1', 'foo', 'bar')
        self.assertEqual(config_to_dict(config),
                         {'section1': {'foo': 'bar'}})


class TestEntryComparer(unittest.TestCase):

    def setUp(self):
        from distchecker import EntryComparer
        self.ec = EntryComparer()

    def test_compare_configs(self):
        res = self.ec.compare_configs(MockFileHandler('[abc]\nfoo=bar', 'foo'),
                                      MockFileHandler('[abc]\nbar=foo', 'bar'))
        self.assertEqual(res, ('different configs', 'foo'))

    def test_compare(self):
        res = self.ec.compare(MockFileHandler('', 'foo', 5),
                              MockFileHandler('', 'bar', 10))
        self.assertEqual(res, ('different sizes', 'foo'))

        res = self.ec.compare(MockFileHandler('', 'foo.ini', 5),
                              MockFileHandler('', 'bar.ini', 10))
        self.assertEqual(res, None)


class TestCloneConfig(unittest.TestCase):

    def test_it(self):
        from distchecker import clone_config, config_to_dict
        from ConfigParser import ConfigParser

        config = ConfigParser()
        config.add_section('foo')
        config.set('foo', 'bar', 'goo')

        copy = clone_config(config)
        self.assertEqual(config_to_dict(config),
                         config_to_dict(copy))


class TestDistChecker(unittest.TestCase):

    def setUp(self):
        from distchecker import DistChecker
        self.dc = DistChecker()
        self.dc.opentarfile = lambda x, y: MockTarFile()
        self.dc.processrunner = MockProcessRunner()

    def test_it(self):
        self.dc.action_compare_sdist()


class MockTarFile(list):
    def close(self):
        pass


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockProcessRunner(object):

    def __init__(self):
        self.ran = []

    def run(self, *args, **kwargs):
        self.ran.append([args, kwargs])
        return Mock(stdout='')


class MockFileHandler(object):
    source = Mock()

    def __init__(self, s, name, size=0):
        self.s = s
        self.name = name
        self.size = size

    def open(self):
        return StringIO(self.s)
