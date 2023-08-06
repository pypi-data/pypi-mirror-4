'''
We're using PyOpenSSL now

import ctypes
from StringIO import StringIO
import socket

import gnutls.connection
import gnutls.crypto
import gnutls.library

from leap.util.misc import null_check


class BadCertError(Exception):
    """raised for malformed certs"""


def get_https_cert_from_domain(domain):
    """
    @param domain: a domain name to get a certificate from.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cred = gnutls.connection.X509Credentials()

    session = gnutls.connection.ClientSession(sock, cred)
    session.connect((domain, 443))
    session.handshake()
    cert = session.peer_certificate
    return cert


def get_cert_from_file(_file):
    getcert = lambda f: gnutls.crypto.X509Certificate(f.read())
    if isinstance(_file, str):
        with open(_file) as f:
            cert = getcert(f)
    else:
        cert = getcert(_file)
    return cert


def get_pkey_from_file(_file):
    getkey = lambda f: gnutls.crypto.X509PrivateKey(f.read())
    if isinstance(_file, str):
        with open(_file) as f:
            key = getkey(f)
    else:
        key = getkey(_file)
    return key


def can_load_cert_and_pkey(string):
    try:
        f = StringIO(string)
        cert = get_cert_from_file(f)

        f = StringIO(string)
        key = get_pkey_from_file(f)

        null_check(cert, 'certificate')
        null_check(key, 'private key')
    except:
        # XXX catch GNUTLSError?
        raise BadCertError
    else:
        return True

def get_cert_fingerprint(domain=None, filepath=None,
                         hash_type="SHA256", sep=":"):
    """
    @param domain: a domain name to get a fingerprint from
    @type domain: str
    @param filepath: path to a file containing a PEM file
    @type filepath: str
    @param hash_type: the hash function to be used in the fingerprint.
        must be one of SHA1, SHA224, SHA256, SHA384, SHA512
    @type hash_type: str
    @rparam: hex_fpr, a hexadecimal representation of a bytestring
             containing the fingerprint.
    @rtype: string
    """
    if domain:
        cert = get_https_cert_from_domain(domain)
    if filepath:
        cert = get_cert_from_file(filepath)

    _buffer = ctypes.create_string_buffer(64)
    buffer_length = ctypes.c_size_t(64)

    SUPPORTED_DIGEST_FUN = ("SHA1", "SHA224", "SHA256", "SHA384", "SHA512")
    if hash_type in SUPPORTED_DIGEST_FUN:
        digestfunction = getattr(
            gnutls.library.constants,
            "GNUTLS_DIG_%s" % hash_type)
    else:
        # XXX improperlyconfigured or something
        raise Exception("digest function not supported")

    gnutls.library.functions.gnutls_x509_crt_get_fingerprint(
        cert._c_object, digestfunction,
        ctypes.byref(_buffer), ctypes.byref(buffer_length))

    # deinit
    #server_cert._X509Certificate__deinit(server_cert._c_object)
    # needed? is segfaulting

    fpr = ctypes.string_at(_buffer, buffer_length.value)
    hex_fpr = sep.join(u"%02X" % ord(char) for char in fpr)

    return hex_fpr
'''
