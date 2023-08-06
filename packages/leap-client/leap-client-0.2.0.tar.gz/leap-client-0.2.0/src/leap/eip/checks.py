import logging
import time
import os
import sys

import requests

from leap import __branding as BRANDING
from leap import certs as leapcerts
from leap.base.auth import srpauth_protected, magick_srpauth
from leap.base import config as baseconfig
from leap.base import constants as baseconstants
from leap.base import providers
from leap.crypto import certs
from leap.eip import config as eipconfig
from leap.eip import constants as eipconstants
from leap.eip import exceptions as eipexceptions
from leap.eip import specs as eipspecs
from leap.util.certs import get_mac_cabundle
from leap.util.fileutil import mkdir_p
from leap.util.web import get_https_domain_and_port

logger = logging.getLogger(name=__name__)

"""
ProviderCertChecker
-------------------
Checks on certificates. To be moved to base.
docs TBD

EIPConfigChecker
----------
It is used from the eip conductor (a instance of EIPConnection that is
managed from the QtApp), running `run_all` method before trying to call
`connect` or any other of the state-changing methods.

It checks that the needed files are provided or can be discovered over the
net. Much of these tests are not specific to EIP module, and can be splitted
into base.tests to be invoked by the base leap init routines.
However, I'm testing them alltogether for the sake of having the whole unit
reachable and testable as a whole.

"""


def get_branding_ca_cert(domain):
    # deprecated
    ca_file = BRANDING.get('provider_ca_file')
    if ca_file:
        return leapcerts.where(ca_file)


class ProviderCertChecker(object):
    """
    Several checks needed for getting
    client certs and checking tls connection
    with provider.
    """
    def __init__(self, fetcher=requests,
                 domain=None,
                 apidomain=None):

        self.fetcher = fetcher
        self.domain = domain
        #XXX needs some kind of autoinit
        #right now we set by hand
        #by loading and reading provider config
        self.apidomain = apidomain
        self.cacert = eipspecs.provider_ca_path(domain)

    def run_all(
            self, checker=None,
            skip_download=False, skip_verify=False):

        if not checker:
            checker = self

        do_verify = not skip_verify
        logger.debug('do_verify: %s', do_verify)
        # checker.download_ca_cert()

        # For MVS+
        # checker.download_ca_signature()
        # checker.get_ca_signatures()
        # checker.is_there_trust_path()

        # For MVS
        checker.is_there_provider_ca()

        checker.is_https_working(verify=do_verify, autocacert=False)
        checker.check_new_cert_needed(verify=do_verify)

    def download_ca_cert(self, uri=None, verify=True):
        req = self.fetcher.get(uri, verify=verify)
        req.raise_for_status()

        # should check domain exists
        capath = self._get_ca_cert_path(self.domain)
        with open(capath, 'w') as f:
            f.write(req.content)

    def check_ca_cert_fingerprint(
            self, hash_type="SHA256",
            fingerprint=None):
        """
        compares the fingerprint in
        the ca cert with a string
        we are passed
        returns True if they are equal, False if not.
        @param hash_type: digest function
        @type hash_type: str
        @param fingerprint: the fingerprint to compare with.
        @type fingerprint: str (with : separator)
        @rtype bool
        """
        ca_cert_path = self.ca_cert_path
        ca_cert_fpr = certs.get_cert_fingerprint(
            filepath=ca_cert_path)
        return ca_cert_fpr == fingerprint

    def verify_api_https(self, uri):
        assert uri.startswith('https://')
        cacert = self.ca_cert_path
        verify = cacert or True

        # DEBUG
        logger.debug('uri -> %s' % uri)
        logger.debug('cacertpath -> %s' % cacert)

        req = self.fetcher.get(uri, verify=verify)
        req.raise_for_status()
        return True

    def download_ca_signature(self):
        # MVS+
        raise NotImplementedError

    def get_ca_signatures(self):
        # MVS+
        raise NotImplementedError

    def is_there_trust_path(self):
        # MVS+
        raise NotImplementedError

    def is_there_provider_ca(self):
        if not self.cacert:
            return False
        cacert_exists = os.path.isfile(self.cacert)
        if cacert_exists:
            logger.debug('True')
            return True
        logger.debug('False!')
        return False

    def is_https_working(
            self, uri=None, verify=True,
            autocacert=False):
        if uri is None:
            uri = self._get_root_uri()
        # XXX raise InsecureURI or something better
        try:
            assert uri.startswith('https')
        except AssertionError:
            raise AssertionError(
                "uri passed should start with https")
        if autocacert and verify is True and self.cacert is not None:
            logger.debug('verify cert: %s', self.cacert)
            verify = self.cacert
        if sys.platform == "darwin":
            verify = get_mac_cabundle()
        logger.debug('checking https connection')
        logger.debug('uri: %s (verify:%s)', uri, verify)

        try:
            self.fetcher.get(uri, verify=verify)

        except requests.exceptions.SSLError as exc:
            raise eipexceptions.HttpsBadCertError

        except requests.exceptions.ConnectionError:
            logger.error('ConnectionError')
            raise eipexceptions.HttpsNotSupported

        else:
            return True

    def check_new_cert_needed(self, skip_download=False, verify=True):
        # XXX add autocacert
        if not self.is_cert_valid(do_raise=False):
            logger.debug('cert needed: true')
            self.download_new_client_cert(
                skip_download=skip_download,
                verify=verify)
            return True
        logger.debug('cert needed: false')
        return False

    def download_new_client_cert(self, uri=None, verify=True,
                                 skip_download=False,
                                 credentials=None):
        logger.debug('download new client cert')
        if skip_download:
            return True
        if uri is None:
            uri = self._get_client_cert_uri()
        # XXX raise InsecureURI or something better
        #assert uri.startswith('https')

        if verify is True and self.cacert is not None:
            verify = self.cacert
            logger.debug('verify = %s', verify)

        fgetfn = self.fetcher.get

        if credentials:
            user, passwd = credentials
            logger.debug('apidomain = %s', self.apidomain)

            @srpauth_protected(user, passwd,
                               server="https://%s" % self.apidomain,
                               verify=verify)
            def getfn(*args, **kwargs):
                return fgetfn(*args, **kwargs)

        else:
            # XXX FIXME fix decorated args
            @magick_srpauth(verify)
            def getfn(*args, **kwargs):
                return fgetfn(*args, **kwargs)
        try:

            req = getfn(uri, verify=verify)
            req.raise_for_status()

        except requests.exceptions.SSLError:
            logger.warning('SSLError while fetching cert. '
                           'Look below for stack trace.')
            raise eipexceptions.HttpsBadCertError("SSLError")
        except Exception as exc:
            raise eipexceptions.EIPClientError(exc.message)

        try:
            logger.debug('validating cert...')
            pemfile_content = req.content
            valid = self.is_valid_pemfile(pemfile_content)
            if not valid:
                logger.warning('invalid cert')
                return False
            cert_path = self._get_client_cert_path()
            self.write_cert(pemfile_content, to=cert_path)
        except:
            logger.warning('Error while validating cert')
            raise
        return True

    def is_cert_valid(self, cert_path=None, do_raise=True):
        exists = lambda: self.is_certificate_exists()
        valid_pemfile = lambda: self.is_valid_pemfile()
        not_expired = lambda: self.is_cert_not_expired()

        valid = exists() and valid_pemfile() and not_expired()
        if not valid:
            if do_raise:
                raise Exception('missing valid cert')
            else:
                return False
        return True

    def is_certificate_exists(self, certfile=None):
        if certfile is None:
            certfile = self._get_client_cert_path()
        return os.path.isfile(certfile)

    def is_cert_not_expired(self, certfile=None, now=time.gmtime):
        if certfile is None:
            certfile = self._get_client_cert_path()
        from_, to_ = certs.get_time_boundaries(certfile)

        return from_ < now() < to_

    def is_valid_pemfile(self, cert_s=None):
        """
        checks that the passed string
        is a valid pem certificate
        @param cert_s: string containing pem content
        @type cert_s: string
        @rtype: bool
        """
        if cert_s is None:
            certfile = self._get_client_cert_path()
            with open(certfile) as cf:
                cert_s = cf.read()
        try:
            valid = certs.can_load_cert_and_pkey(cert_s)
        except certs.BadCertError:
            logger.warning("Not valid pemfile")
            valid = False
        return valid

    @property
    def ca_cert_path(self):
        return self._get_ca_cert_path(self.domain)

    def _get_root_uri(self):
        return u"https://%s/" % self.domain

    def _get_client_cert_uri(self):
        return "https://%s/1/cert" % self.apidomain

    def _get_client_cert_path(self):
        return eipspecs.client_cert_path(domain=self.domain)

    def _get_ca_cert_path(self, domain):
        # XXX this folder path will be broken for win
        # and this should be moved to eipspecs.ca_path

        # XXX use baseconfig.get_provider_path(folder=Foo)
        # !!!

        capath = baseconfig.get_config_file(
            'cacert.pem',
            folder='providers/%s/keys/ca' % domain)
        folder, fname = os.path.split(capath)
        if not os.path.isdir(folder):
            mkdir_p(folder)
        return capath

    def write_cert(self, pemfile_content, to=None):
        folder, filename = os.path.split(to)
        if not os.path.isdir(folder):
            mkdir_p(folder)
        with open(to, 'w') as cert_f:
            cert_f.write(pemfile_content)

    def set_api_domain(self, domain):
        self.apidomain = domain


class EIPConfigChecker(object):
    """
    Several checks needed
    to ensure a EIPConnection
    can be sucessfully established.
    use run_all to run all checks.
    """

    def __init__(self, fetcher=requests, domain=None):
        # we do not want to accept too many
        # argument on init.
        # we want tests
        # to be explicitely run.

        self.fetcher = fetcher

        # if not domain, get from config
        self.domain = domain
        self.apidomain = None
        self.cacert = eipspecs.provider_ca_path(domain)

        self.defaultprovider = providers.LeapProviderDefinition(domain=domain)
        self.defaultprovider.load()
        self.eipconfig = eipconfig.EIPConfig(domain=domain)
        self.set_api_domain()
        self.eipserviceconfig = eipconfig.EIPServiceConfig(domain=domain)
        self.eipserviceconfig.load()

    def run_all(self, checker=None, skip_download=False):
        """
        runs all checks in a row.
        will raise if some error encountered.
        catching those exceptions is not
        our responsibility at this moment
        """
        if not checker:
            checker = self

        # let's call all tests
        # needed for a sane eip session.

        # TODO: get rid of check_default.
        # check_complete should
        # be enough. but here to make early tests easier.
        checker.check_default_eipconfig()

        checker.check_is_there_default_provider()
        checker.fetch_definition(skip_download=skip_download)
        checker.fetch_eip_service_config(skip_download=skip_download)
        checker.check_complete_eip_config()
        #checker.ping_gateway()

    # public checks

    def check_default_eipconfig(self):
        """
        checks if default eipconfig exists,
        and dumps a default file if not
        """
        # XXX ONLY a transient check
        # because some old function still checks
        # for eip config at the beginning.

        # it *really* does not make sense to
        # dump it right now, we can get an in-memory
        # config object and dump it to disk in a
        # later moment
        logger.debug('checking default eip config')
        if not self._is_there_default_eipconfig():
            self._dump_default_eipconfig()

    def check_is_there_default_provider(self, config=None):
        """
        raises EIPMissingDefaultProvider if no
        default provider found on eip config.
        This is catched by ui and runs FirstRunWizard (MVS+)
        """
        if config is None:
            config = self.eipconfig.config
        logger.debug('checking default provider')
        provider = config.get('provider', None)
        if provider is None:
            raise eipexceptions.EIPMissingDefaultProvider
        # XXX raise also if malformed ProviderDefinition?
        return True

    def fetch_definition(self, skip_download=False,
                         force_download=False,
                         config=None, uri=None,
                         domain=None):
        """
        fetches a definition file from server
        """
        # TODO:
        # - Implement diff
        # - overwrite only if different.
        #   (attend to serial field different, for instance)

        logger.debug('fetching definition')

        if skip_download:
            logger.debug('(fetching def skipped)')
            return True
        if config is None:
            config = self.defaultprovider.config
        if uri is None:
            if not domain:
                domain = config.get('provider', None)
            uri = self._get_provider_definition_uri(domain=domain)

        if sys.platform == "darwin":
            verify = get_mac_cabundle()
        else:
            verify = True

        self.defaultprovider.load(
            from_uri=uri,
            fetcher=self.fetcher,
            verify=verify)
        self.defaultprovider.save()

    def fetch_eip_service_config(self, skip_download=False,
                                 force_download=False,
                                 config=None, uri=None,  # domain=None,
                                 autocacert=True, verify=True):
        if skip_download:
            return True
        if config is None:
            self.eipserviceconfig.load()
            config = self.eipserviceconfig.config
        if uri is None:
            #XXX
            #if not domain:
                #domain = self.domain or config.get('provider', None)
            uri = self._get_eip_service_uri(
                domain=self.apidomain)

        if autocacert and self.cacert is not None:
            verify = self.cacert

        self.eipserviceconfig.load(
            from_uri=uri,
            fetcher=self.fetcher,
            force_download=force_download,
            verify=verify)
        self.eipserviceconfig.save()

    def check_complete_eip_config(self, config=None):
        # TODO check for gateway
        if config is None:
            config = self.eipconfig.config
        try:
            assert 'provider' in config
            assert config['provider'] is not None
            # XXX assert there is gateway !!
        except AssertionError:
            raise eipexceptions.EIPConfigurationError

        # XXX TODO:
        # We should WRITE eip config if missing or
        # incomplete at this point
        #self.eipconfig.save()

    #
    # private helpers
    #

    def _is_there_default_eipconfig(self):
        return self.eipconfig.exists()

    def _dump_default_eipconfig(self):
        self.eipconfig.save(force=True)

    def _get_provider_definition_uri(self, domain=None, path=None):
        if domain is None:
            domain = self.domain or baseconstants.DEFAULT_PROVIDER
        if path is None:
            path = baseconstants.DEFINITION_EXPECTED_PATH
        uri = u"https://%s/%s" % (domain, path)
        logger.debug('getting provider definition from %s' % uri)
        return uri

    def _get_eip_service_uri(self, domain=None, path=None):
        if domain is None:
            domain = self.domain or baseconstants.DEFAULT_PROVIDER
        if path is None:
            path = eipconstants.EIP_SERVICE_EXPECTED_PATH
        uri = "https://%s/%s" % (domain, path)
        logger.debug('getting eip service file from %s', uri)
        return uri

    def set_api_domain(self):
        """sets api domain from defaultprovider config object"""
        api = self.defaultprovider.config.get('api_uri', None)
        # the caller is responsible for having loaded the config
        # object at this point
        if api:
            api_dom = get_https_domain_and_port(api)
            self.apidomain = "%s:%s" % api_dom

    def get_api_domain(self):
        """gets api domain"""
        return self.apidomain
