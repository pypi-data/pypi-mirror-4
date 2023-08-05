from testresources import (
    FixtureResource,
    ResourcedTestCase,
    )
from testtools import TestCase

from djlibdep.test_double import LibdepServiceDouble

from libdep_service_client import client


class MakeQueryStringTests(TestCase):

    def test_no_libs(self):
        self.assertEqual('', client.make_query_string([]))

    def test_one_lib(self):
        self.assertEqual('?libs=libfoo.so.1',
                client.make_query_string(['libfoo.so.1']))

    def test_two_libs(self):
        self.assertEqual('?libs=libfoo.so.1&libs=libbar.so.1',
                client.make_query_string(['libfoo.so.1', 'libbar.so.1']))


class MakeURLTests(TestCase):

    def test_inserts_api_path(self):
        base = 'https://libdeps-service.example.com/foo'
        self.assertEqual('{0}/v1/get_binaries_for_libraries'.format(base),
                client.make_url(base, []))

    def test_adds_query_string(self):
        base = 'https://libdeps-service.example.com/foo'
        self.assertEqual(
            '{0}/v1/get_binaries_for_libraries?libs=libfoo.so.1'.format(base),
            client.make_url(base, ['libfoo.so.1']))


class LookupAliasTests(TestCase):

    def test_production(self):
        self.assertEqual('https://libdep-service.ubuntu.com/',
                client.lookup_alias('production'))

    def test_staging(self):
        self.assertEqual('https://libdep-service.staging.ubuntu.com/',
                client.lookup_alias('staging'))

    def test_unknown(self):
        e = self.assertRaises(ValueError, client.lookup_alias, 'unknown')
        self.assertEqual("Unknown alias: unknown", str(e))


class ClientTests(TestCase):

    def test_from_alias_known(self):
        alias = 'production'
        c = client.Client.from_alias(alias)
        self.assertEqual(client.lookup_alias(alias), c.base_url)

    def test_from_alias_unknown(self):
        alias = 'unknown'
        e = self.assertRaises(ValueError, client.Client.from_alias, alias)
        self.assertEqual("Unknown alias: {}".format(alias), str(e))


# This is implicit setup for the tests that share it, so keep
# the data small and the use of it minimal.
TEST_DATA = {
    'v1/service_check': [({}, 'Hello world!')],
    'v1/get_binaries_for_libraries': [
            ({'libs': ['doesnotexist']}, '{}'),
            ({'libs': ['libc.so.6']}, '{"libc.so.6": ["libc-bin"]}'),
    ],
}

test_double_fixture = FixtureResource(LibdepServiceDouble(TEST_DATA))



class ClientIntegrationTests(TestCase, ResourcedTestCase):

    resources = [('double', test_double_fixture)]

    def test_get_binaries_for_libraries_found(self):
        lib = 'libc.so.6'
        c = client.Client(self.double.base_url)
        self.assertEqual({"libc.so.6": ["libc-bin"]},
                c.get_binaries_for_libraries([lib]))

    def test_get_binaries_for_libraries_missing(self):
        lib = 'doesnotexist'
        c = client.Client(self.double.base_url)
        self.assertEqual({}, c.get_binaries_for_libraries([lib]))

    def test_get_binaries_for_libraries_unheard(self):
        lib = 'neverexisted'
        c = client.Client(self.double.base_url)
        self.assertEqual({}, c.get_binaries_for_libraries([lib]))
