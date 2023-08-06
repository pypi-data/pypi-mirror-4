# -*- coding: utf8 -*-

from pyramid import testing

from pyramid_rawes import (
    IRawes,
    get_rawes,
    _build_rawes,
    includeme,
    _parse_settings
)

import rawes

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa


class TestRegistry(object):

    def __init__(self, settings=None):

        if settings is None:
            self.settings = {}
        else:
            self.settings = settings

        self.rawes = None

    def queryUtility(self, iface):
        return self.rawes

    def registerUtility(self, rawes, iface):
        self.rawes = rawes


class TestGetAndBuild(unittest.TestCase):

    def test_get_rawes(self):
        r = TestRegistry()
        ES = rawes.Elastic(url='http://localhost:9200')
        r.registerUtility(ES, IRawes)
        ES2 = get_rawes(r)
        self.assertEquals(ES, ES2)

    def test_build_rawes_already_exists(self):
        r = TestRegistry()
        ES = rawes.Elastic('http://localhost:9200')
        r.registerUtility(ES, IRawes)
        ES2 = _build_rawes(r)
        self.assertEquals(ES, ES2)

    def test_build_rawes_default_settings(self):
        r = TestRegistry()
        ES = _build_rawes(r)
        self.assertIsInstance(ES, rawes.Elastic)
        self.assertEquals('localhost:9200', ES.url.netloc)

    def test_build_rawes_custom_settings(self):
        settings = {
            'rawes.url': 'http://elastic.search.org:9200',
            'rawes.path': '/search',
            'rawes.timeout': 123,
            'rawes.except_on_error': True
        }
        r = TestRegistry(settings)
        ES = _build_rawes(r)
        self.assertIsInstance(ES, rawes.Elastic)
        self.assertEquals('elastic.search.org:9200', ES.url.netloc)


class TestSettings(unittest.TestCase):

    def _assert_contains_all_keys(self, args):
        self.assertIn('url', args)
        self.assertIn('path', args)
        self.assertIn('except_on_error', args)
        self.assertIn('timeout', args)

    def test_get_default_settings(self):
        settings = {}
        args = _parse_settings(settings)
        self._assert_contains_all_keys(args)

    def test_get_some_settings(self):
        settings = {
            'rawes.url': 'http://elastic.search.org:9200',
            'rawes.timeout': 123,
            'rawes.except_on_error': True
        }
        args = _parse_settings(settings)
        self._assert_contains_all_keys(args)
        self.assertEquals('http://elastic.search.org:9200', args['url'])
        self.assertEquals(123, args['timeout'])
        self.assertEquals(True, args['except_on_error'])

    def test_get_all_settings(self):
        settings = {
            'rawes.url': 'http://elastic.search.org:9200',
            'rawes.path': '/search',
            'rawes.timeout': 123,
            'rawes.except_on_error': True
        }
        args = _parse_settings(settings)
        self._assert_contains_all_keys(args)
        self.assertEquals(123, args['timeout'])
        self.assertEquals(True, args['except_on_error'])


class TestIncludeMe(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings['rawes.url'] = 'http://localhost:9300'

    def tearDown(self):
        del self.config

    def test_includeme(self):
        includeme(self.config)
        ES = self.config.registry.queryUtility(IRawes)
        self.assertIsInstance(ES, rawes.Elastic)
        self.assertEquals('localhost:9300', ES.url.netloc)

    def test_directive_was_added(self):
        includeme(self.config)
        ES = self.config.get_rawes()
        self.assertIsInstance(ES, rawes.Elastic)
        self.assertEquals('localhost:9300', ES.url.netloc)
