from BaseHTTPServer import BaseHTTPRequestHandler
import copy
import json
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
import time
import urlparse

from mock import (patch, Mock)

import requests

from leap.base import config as baseconfig
from leap.base import pluggableconfig
from leap.base.constants import (DEFAULT_PROVIDER_DEFINITION,
                                 DEFINITION_EXPECTED_PATH)
from leap.eip import checks as eipchecks
from leap.eip import specs as eipspecs
from leap.eip import exceptions as eipexceptions
from leap.eip.tests import data as testdata
from leap.testing.basetest import BaseLeapTest
from leap.testing.https_server import BaseHTTPSServerTestCase
from leap.testing.https_server import where as where_cert
from leap.util.fileutil import mkdir_f


class NoLogRequestHandler:
    def log_message(self, *args):
        # don't write log msg to stderr
        pass

    def read(self, n=None):
        return ''


class EIPCheckTest(BaseLeapTest):

    __name__ = "eip_check_tests"
    provider = "testprovider.example.org"
    maxDiff = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # test methods are there, and can be called from run_all

    def test_checker_should_implement_check_methods(self):
        checker = eipchecks.EIPConfigChecker(domain=self.provider)

        self.assertTrue(hasattr(checker, "check_default_eipconfig"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "check_is_there_default_provider"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "fetch_definition"), "missing meth")
        self.assertTrue(hasattr(checker, "fetch_eip_service_config"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "check_complete_eip_config"),
                        "missing meth")

    def test_checker_should_actually_call_all_tests(self):
        checker = eipchecks.EIPConfigChecker(domain=self.provider)

        mc = Mock()
        checker.run_all(checker=mc)
        self.assertTrue(mc.check_default_eipconfig.called, "not called")
        self.assertTrue(mc.check_is_there_default_provider.called,
                        "not called")
        self.assertTrue(mc.fetch_definition.called,
                        "not called")
        self.assertTrue(mc.fetch_eip_service_config.called,
                        "not called")
        self.assertTrue(mc.check_complete_eip_config.called,
                        "not called")

    # test individual check methods

    def test_check_default_eipconfig(self):
        checker = eipchecks.EIPConfigChecker(domain=self.provider)
        # no eip config (empty home)
        eipconfig_path = checker.eipconfig.filename
        self.assertFalse(os.path.isfile(eipconfig_path))
        checker.check_default_eipconfig()
        # we've written one, so it should be there.
        self.assertTrue(os.path.isfile(eipconfig_path))
        with open(eipconfig_path, 'rb') as fp:
            deserialized = json.load(fp)

        # force re-evaluation of the paths
        # small workaround for evaluating home dirs correctly
        EIP_SAMPLE_CONFIG = copy.copy(testdata.EIP_SAMPLE_CONFIG)
        EIP_SAMPLE_CONFIG['openvpn_client_certificate'] = \
            eipspecs.client_cert_path(self.provider)
        EIP_SAMPLE_CONFIG['openvpn_ca_certificate'] = \
            eipspecs.provider_ca_path(self.provider)
        self.assertEqual(deserialized, EIP_SAMPLE_CONFIG)

        # TODO: shold ALSO run validation methods.

    def test_check_is_there_default_provider(self):
        checker = eipchecks.EIPConfigChecker(domain=self.provider)
        # we do dump a sample eip config, but lacking a
        # default provider entry.
        # This error will be possible catched in a different
        # place, when JSONConfig does validation of required fields.

        # passing direct config
        with self.assertRaises(eipexceptions.EIPMissingDefaultProvider):
            checker.check_is_there_default_provider(config={})

        # ok. now, messing with real files...
        # blank out default_provider
        sampleconfig = copy.copy(testdata.EIP_SAMPLE_CONFIG)
        sampleconfig['provider'] = None
        eipcfg_path = checker.eipconfig.filename
        mkdir_f(eipcfg_path)
        with open(eipcfg_path, 'w') as fp:
            json.dump(sampleconfig, fp)
        #with self.assertRaises(eipexceptions.EIPMissingDefaultProvider):
        # XXX we should catch this as one of our errors, but do not
        # see how to do it quickly.
        with self.assertRaises(pluggableconfig.ValidationError):
            #import ipdb;ipdb.set_trace()
            checker.eipconfig.load(fromfile=eipcfg_path)
            checker.check_is_there_default_provider()

        sampleconfig = testdata.EIP_SAMPLE_CONFIG
        #eipcfg_path = checker._get_default_eipconfig_path()
        with open(eipcfg_path, 'w') as fp:
            json.dump(sampleconfig, fp)
        checker.eipconfig.load()
        self.assertTrue(checker.check_is_there_default_provider())

    def test_fetch_definition(self):
        with patch.object(requests, "get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.headers = {
                'last-modified': "Wed Dec 12 12:12:12 GMT 2012"}
            mocked_get.return_value.json = DEFAULT_PROVIDER_DEFINITION
            checker = eipchecks.EIPConfigChecker(fetcher=requests)
            sampleconfig = testdata.EIP_SAMPLE_CONFIG
            checker.fetch_definition(config=sampleconfig)

        fn = os.path.join(baseconfig.get_default_provider_path(),
                          DEFINITION_EXPECTED_PATH)
        with open(fn, 'r') as fp:
            deserialized = json.load(fp)
        self.assertEqual(DEFAULT_PROVIDER_DEFINITION, deserialized)

        # XXX TODO check for ConnectionError, HTTPError, InvalidUrl
        # (and proper EIPExceptions are raised).
        # Look at base.test_config.

    def test_fetch_eip_service_config(self):
        with patch.object(requests, "get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.headers = {
                'last-modified': "Wed Dec 12 12:12:12 GMT 2012"}
            mocked_get.return_value.json = testdata.EIP_SAMPLE_SERVICE
            checker = eipchecks.EIPConfigChecker(fetcher=requests)
            sampleconfig = testdata.EIP_SAMPLE_CONFIG
            checker.fetch_eip_service_config(config=sampleconfig)

    def test_check_complete_eip_config(self):
        checker = eipchecks.EIPConfigChecker()
        with self.assertRaises(eipexceptions.EIPConfigurationError):
            sampleconfig = copy.copy(testdata.EIP_SAMPLE_CONFIG)
            sampleconfig['provider'] = None
            checker.check_complete_eip_config(config=sampleconfig)
        with self.assertRaises(eipexceptions.EIPConfigurationError):
            sampleconfig = copy.copy(testdata.EIP_SAMPLE_CONFIG)
            del sampleconfig['provider']
            checker.check_complete_eip_config(config=sampleconfig)

        # normal case
        sampleconfig = copy.copy(testdata.EIP_SAMPLE_CONFIG)
        checker.check_complete_eip_config(config=sampleconfig)


class ProviderCertCheckerTest(BaseLeapTest):

    __name__ = "provider_cert_checker_tests"
    provider = "testprovider.example.org"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # test methods are there, and can be called from run_all

    def test_checker_should_implement_check_methods(self):
        checker = eipchecks.ProviderCertChecker()

        # For MVS+
        self.assertTrue(hasattr(checker, "download_ca_cert"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "download_ca_signature"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "get_ca_signatures"), "missing meth")
        self.assertTrue(hasattr(checker, "is_there_trust_path"),
                        "missing meth")

        # For MVS
        self.assertTrue(hasattr(checker, "is_there_provider_ca"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "is_https_working"), "missing meth")
        self.assertTrue(hasattr(checker, "check_new_cert_needed"),
                        "missing meth")

    def test_checker_should_actually_call_all_tests(self):
        checker = eipchecks.ProviderCertChecker()

        mc = Mock()
        checker.run_all(checker=mc)
        # XXX MVS+
        #self.assertTrue(mc.download_ca_cert.called, "not called")
        #self.assertTrue(mc.download_ca_signature.called, "not called")
        #self.assertTrue(mc.get_ca_signatures.called, "not called")
        #self.assertTrue(mc.is_there_trust_path.called, "not called")

        # For MVS
        self.assertTrue(mc.is_there_provider_ca.called, "not called")
        self.assertTrue(mc.is_https_working.called,
                        "not called")
        self.assertTrue(mc.check_new_cert_needed.called,
                        "not called")

    # test individual check methods

    @unittest.skip
    def test_is_there_provider_ca(self):
        # XXX commenting out this test.
        # With the generic client this does not make sense,
        # we should dump one there.
        # or test conductor logic.
        checker = eipchecks.ProviderCertChecker()
        self.assertTrue(
            checker.is_there_provider_ca())


class ProviderCertCheckerHTTPSTests(BaseHTTPSServerTestCase, BaseLeapTest):
    provider = "testprovider.example.org"

    class request_handler(NoLogRequestHandler, BaseHTTPRequestHandler):
        responses = {
            '/': ['OK', ''],
            '/client.cert': [
                # XXX get sample cert
                '-----BEGIN CERTIFICATE-----',
                '-----END CERTIFICATE-----'],
            '/badclient.cert': [
                'BADCERT']}

        def do_GET(self):
            path = urlparse.urlparse(self.path)
            message = '\n'.join(self.responses.get(
                path.path, None))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(message)

    def test_is_https_working(self):
        fetcher = requests
        uri = "https://%s/" % (self.get_server())
        # bare requests call. this should just pass (if there is
        # an https service there).
        fetcher.get(uri, verify=False)
        checker = eipchecks.ProviderCertChecker(fetcher=fetcher)
        self.assertTrue(checker.is_https_working(uri=uri, verify=False))

        # for local debugs, when in doubt
        #self.assertTrue(checker.is_https_working(uri="https://github.com",
                        #verify=True))

        # for the two checks below, I know they fail because no ca
        # cert is passed to them, and I know that's the error that
        # requests return with our implementation.
        # We're receiving this because our
        # server is dying prematurely when the handshake is interrupted on the
        # client side.
        # Since we have access to the server, we could check that
        # the error raised has been:
        # SSL23_READ_BYTES: alert bad certificate
        with self.assertRaises(requests.exceptions.SSLError) as exc:
            fetcher.get(uri, verify=True)
            self.assertTrue(
                "SSL23_GET_SERVER_HELLO:unknown protocol" in exc.message)

        # XXX FIXME! Uncomment after #638 is done
        #with self.assertRaises(eipexceptions.EIPBadCertError) as exc:
            #checker.is_https_working(uri=uri, verify=True)
            #self.assertTrue(
                #"cert verification failed" in exc.message)

        # get cacert from testing.https_server
        cacert = where_cert('cacert.pem')
        fetcher.get(uri, verify=cacert)
        self.assertTrue(checker.is_https_working(uri=uri, verify=cacert))

        # same, but get cacert from leap.custom
        # XXX TODO!

    @unittest.skip
    def test_download_new_client_cert(self):
        # FIXME
        # Magick srp decorator broken right now...
        # Have to mock the decorator and inject something that
        # can bypass the authentication

        uri = "https://%s/client.cert" % (self.get_server())
        cacert = where_cert('cacert.pem')
        checker = eipchecks.ProviderCertChecker(domain=self.provider)
        credentials = "testuser", "testpassword"
        self.assertTrue(checker.download_new_client_cert(
                        credentials=credentials, uri=uri, verify=cacert))

        # now download a malformed cert
        uri = "https://%s/badclient.cert" % (self.get_server())
        cacert = where_cert('cacert.pem')
        checker = eipchecks.ProviderCertChecker()
        with self.assertRaises(ValueError):
            self.assertTrue(checker.download_new_client_cert(
                            credentials=credentials, uri=uri, verify=cacert))

        # did we write cert to its path?
        clientcertfile = eipspecs.client_cert_path()
        self.assertTrue(os.path.isfile(clientcertfile))
        certfile = eipspecs.client_cert_path()
        with open(certfile, 'r') as cf:
            certcontent = cf.read()
        self.assertEqual(certcontent,
                         '\n'.join(
                             self.request_handler.responses['/client.cert']))
        os.remove(clientcertfile)

    def test_is_cert_valid(self):
        checker = eipchecks.ProviderCertChecker()
        # TODO: better exception catching
        # should raise eipexceptions.BadClientCertificate, and give reasons
        # on msg.
        with self.assertRaises(Exception) as exc:
            self.assertFalse(checker.is_cert_valid())
            exc.message = "missing cert"

    def test_bad_validity_certs(self):
        checker = eipchecks.ProviderCertChecker()
        certfile = where_cert('leaptestscert.pem')
        self.assertFalse(checker.is_cert_not_expired(
            certfile=certfile,
            now=lambda: time.mktime((2038, 1, 1, 1, 1, 1, 1, 1, 1))))
        self.assertFalse(checker.is_cert_not_expired(
            certfile=certfile,
            now=lambda: time.mktime((1970, 1, 1, 1, 1, 1, 1, 1, 1))))

    def test_check_new_cert_needed(self):
        # check: missing cert
        checker = eipchecks.ProviderCertChecker(domain=self.provider)
        self.assertTrue(checker.check_new_cert_needed(skip_download=True))
        # TODO check: malformed cert
        # TODO check: expired cert
        # TODO check: pass test server uri instead of skip


if __name__ == "__main__":
    unittest.main()
