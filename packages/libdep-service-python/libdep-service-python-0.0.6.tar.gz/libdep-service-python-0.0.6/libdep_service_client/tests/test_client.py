from fixtures import FakeLogger
from libpathod import test as pathod_test
from testresources import (
    FixtureResource,
    ResourcedTestCase,
    )
from testtools import TestCase
from testtools.matchers import EndsWith

from djlibdep.test_double import LibdepServiceDouble

from libdep_service_client import client


class MakeQueryStringTests(TestCase):

    def test_no_libs(self):
        self.assertEqual('', client.make_query_string([], []))

    def test_one_lib(self):
        self.assertEqual(
            '?libs=libfoo.so.1',
            client.make_query_string(['libfoo.so.1'], []))

    def test_two_libs(self):
        self.assertEqual(
            '?libs=libfoo.so.1&libs=libbar.so.1',
            client.make_query_string(['libfoo.so.1', 'libbar.so.1'], []))

    def test_with_arch(self):
        self.assertEqual(
            '?libs=libfoo.so.1&libs=libbar.so.1&arch=i386',
            client.make_query_string(['libfoo.so.1', 'libbar.so.1'], ['i386']))


class MakeURLTests(TestCase):

    def test_inserts_api_path(self):
        base = 'https://libdeps-service.example.com/foo'
        self.assertEqual('{0}/v2/get_binaries_for_libraries'.format(base),
                client.make_url(base, [], []))

    def test_adds_query_string(self):
        base = 'https://libdeps-service.example.com/foo'
        self.assertEqual(
            '{0}/v2/get_binaries_for_libraries?libs=libfoo.so.1'.format(base),
            client.make_url(base, ['libfoo.so.1'], []))

    def test_adds_query_string_with_arch(self):
        base = 'https://libdeps-service.example.com/foo'
        query_string = 'v2/get_binaries_for_libraries?libs=libfoo.so.1&arch=i386'
        self.assertEqual(
            '{0}/{1}'.format(base, query_string),
            client.make_url(base, ['libfoo.so.1'], ['i386']))


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
TEST_DATA = [('libc', {'i386': {'libc.so.6': 'libc-bin'},
                       'amd64': {'libc.so.6': 'libc-amd64'}})]


test_double_fixture = FixtureResource(LibdepServiceDouble(TEST_DATA))



class ClientIntegrationTests(TestCase, ResourcedTestCase):

    resources = [('double', test_double_fixture)]

    def test_get_binaries_for_libraries_found(self):
        lib = 'libc.so.6'
        c = client.Client(self.double.base_url)
        self.assertEqual(
            {'i386': {"libc.so.6": ["libc-bin"]}},
            c.get_binaries_for_libraries([lib], ['i386']))

    def test_get_binaries_for_libraries_missing(self):
        lib = 'doesnotexist'
        c = client.Client(self.double.base_url)
        self.assertEqual(
            {'i386': {}}, c.get_binaries_for_libraries([lib], ['i386']))

    def test_get_binaries_for_libraries_unheard(self):
        lib = 'neverexisted'
        c = client.Client(self.double.base_url)
        self.assertEqual(
            {'i386': {}}, c.get_binaries_for_libraries([lib], ['i386']))


class ErrorTests(TestCase):

    def setUp(self):
        super(ErrorTests, self).setUp()
        self.useFixture(FakeLogger(name="pathod", level="WARN"))

    def test_no_server(self):
        # Hope that this port isn't in use
        e = self.assertRaises(client.ConnectionError, client.do_request,
                'http://localhost:9082/')
        self.assertThat(str(e), EndsWith("Connection refused"))

    def test_connection_reset(self):
        with pathod_test.Daemon() as server:
            # disconnect after 0 bytes
            e = self.assertRaises(client.ConnectionError, client.do_request,
                    server.p('200:d0'))
            self.assertThat(str(e), EndsWith("Bad status line: ''"))

    def test_404(self):
        error_text = "NotFound"
        with pathod_test.Daemon() as server:
            e = self.assertRaises(client.ConnectionError, client.do_request,
                    server.p('404:b"%s"' % error_text))
            self.assertThat(str(e),
                    EndsWith("Response status 404: %s" % error_text))

    def test_502(self):
        error_text = "ServerDown"
        with pathod_test.Daemon() as server:
            e = self.assertRaises(client.ConnectionError, client.do_request,
                    server.p('502:b"%s"' % error_text))
            self.assertThat(str(e),
                    EndsWith("Response status 502: %s" % error_text))
