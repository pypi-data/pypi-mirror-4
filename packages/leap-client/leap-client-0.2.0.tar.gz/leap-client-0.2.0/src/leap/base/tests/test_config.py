import json
import os
import platform
import socket
#import tempfile

import mock
import requests

from leap.base import config
from leap.base import constants
from leap.base import exceptions
from leap.eip import constants as eipconstants
from leap.util.fileutil import mkdir_p
from leap.testing.basetest import BaseLeapTest


try:
    import unittest2 as unittest
except ImportError:
    import unittest

_system = platform.system()


class JSONLeapConfigTest(BaseLeapTest):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_metaclass(self):
        with self.assertRaises(exceptions.ImproperlyConfigured) as exc:
            class DummyTestConfig(config.JSONLeapConfig):
                __metaclass__ = config.MetaConfigWithSpec
            exc.startswith("missing spec dict")

        class DummyTestConfig(config.JSONLeapConfig):
            __metaclass__ = config.MetaConfigWithSpec
            spec = {'properties': {}}
        with self.assertRaises(exceptions.ImproperlyConfigured) as exc:
            DummyTestConfig()
            exc.startswith("missing slug")

        class DummyTestConfig(config.JSONLeapConfig):
            __metaclass__ = config.MetaConfigWithSpec
            spec = {'properties': {}}
            slug = "foo"
        DummyTestConfig()

######################################3
#
# provider fetch tests block
#


class ProviderTest(BaseLeapTest):
    # override per test fixtures

    def setUp(self):
        pass

    def tearDown(self):
        pass


# XXX depreacated. similar test in eip.checks

#class BareHomeTestCase(ProviderTest):
#
    #__name__ = "provider_config_tests_bare_home"
#
    #def test_should_raise_if_missing_eip_json(self):
        #with self.assertRaises(exceptions.MissingConfigFileError):
            #config.get_config_json(os.path.join(self.home, 'eip.json'))


class ProviderDefinitionTestCase(ProviderTest):
    # XXX MOVE TO eip.test_checks
    # -- kali 2012-08-24 00:38

    __name__ = "provider_config_tests"

    def setUp(self):
        # dump a sample eip file
        # XXX Move to Use EIP Spec Instead!!!
        # XXX tests to be moved to eip.checks and eip.providers
        # XXX can use eipconfig.dump_default_eipconfig

        path = os.path.join(self.home, '.config', 'leap')
        mkdir_p(path)
        with open(os.path.join(path, 'eip.json'), 'w') as fp:
            json.dump(eipconstants.EIP_SAMPLE_JSON, fp)


# these tests below should move to
# eip.checks
# config.Configuration has been deprecated

# TODO:
# - We're instantiating a ProviderTest because we're doing the home wipeoff
# on setUpClass instead of the setUp (for speedup of the general cases).

# We really should be testing all of them in the same testCase, and
# doing an extra wipe of the tempdir... but be careful!!!! do not mess with
# os.environ home more than needed... that could potentially bite!

# XXX actually, another thing to fix here is separating tests:
# - test that requests has been called.
# - check deeper for error types/msgs

# we SHOULD inject requests dep in the constructor
# (so we can pass mock easily).


#class ProviderFetchConError(ProviderTest):
    #def test_connection_error(self):
        #with mock.patch.object(requests, "get") as mock_method:
            #mock_method.side_effect = requests.ConnectionError
            #cf = config.Configuration()
            #self.assertIsInstance(cf.error, str)
#
#
#class ProviderFetchHttpError(ProviderTest):
    #def test_file_not_found(self):
        #with mock.patch.object(requests, "get") as mock_method:
            #mock_method.side_effect = requests.HTTPError
            #cf = config.Configuration()
            #self.assertIsInstance(cf.error, str)
#
#
#class ProviderFetchInvalidUrl(ProviderTest):
    #def test_invalid_url(self):
        #cf = config.Configuration("ht")
        #self.assertTrue(cf.error)


# end provider fetch tests
###########################################


class ConfigHelperFunctions(BaseLeapTest):

    __name__ = "config_helper_tests"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # tests

    @unittest.skipUnless(_system == "Linux", "linux only")
    def test_lin_get_config_file(self):
        """
        config file path where expected? (linux)
        """
        self.assertEqual(
            config.get_config_file(
                'test', folder="foo/bar"),
            os.path.expanduser(
                '~/.config/leap/foo/bar/test')
        )

    @unittest.skipUnless(_system == "Darwin", "mac only")
    def test_mac_get_config_file(self):
        """
        config file path where expected? (mac)
        """
        self._missing_test_for_plat(do_raise=True)

    @unittest.skipUnless(_system == "Windows", "win only")
    def test_win_get_config_file(self):
        """
        config file path where expected?
        """
        self._missing_test_for_plat(do_raise=True)

    #
    # XXX hey, I'm raising exceptions here
    # on purpose. just wanted to make sure
    # that the skip stuff is doing it right.
    # If you're working on win/macos tests,
    # feel free to remove tests that you see
    # are too redundant.

    @unittest.skipUnless(_system == "Linux", "linux only")
    def test_lin_get_config_dir(self):
        """
        nice config dir? (linux)
        """
        self.assertEqual(
            config.get_config_dir(),
            os.path.expanduser('~/.config/leap'))

    @unittest.skipUnless(_system == "Darwin", "mac only")
    def test_mac_get_config_dir(self):
        """
        nice config dir? (mac)
        """
        self._missing_test_for_plat(do_raise=True)

    @unittest.skipUnless(_system == "Windows", "win only")
    def test_win_get_config_dir(self):
        """
        nice config dir? (win)
        """
        self._missing_test_for_plat(do_raise=True)

    # provider paths

    @unittest.skipUnless(_system == "Linux", "linux only")
    def test_get_default_provider_path(self):
        """
        is default provider path ok?
        """
        self.assertEqual(
            config.get_default_provider_path(),
            os.path.expanduser(
                '~/.config/leap/providers/%s/' %
                constants.DEFAULT_PROVIDER)
        )

    # validate ip

    def test_validate_ip(self):
        """
        check our ip validation
        """
        config.validate_ip('3.3.3.3')
        with self.assertRaises(socket.error):
            config.validate_ip('255.255.255.256')
        with self.assertRaises(socket.error):
            config.validate_ip('foobar')

    @unittest.skip
    def test_validate_domain(self):
        """
        code to be written yet
        """
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
