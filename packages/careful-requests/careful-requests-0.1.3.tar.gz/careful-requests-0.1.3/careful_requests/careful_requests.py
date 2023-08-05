# -*- coding: utf-8 -*-
"""
The requests library is wonderful. However, it injects custom headers into
outgoing requests due to urllib3 and httplib/http.client. This is an attempt to
isolate and fix this issue.

see also:
    https://github.com/shazow/urllib3/pull/138
    https://github.com/kennethreitz/requests/pull/1077
    http://bugs.python.org/issue16830
"""

import requests

from requests.packages.urllib3.connectionpool import (
    HTTPConnection,
    HTTPSConnection,
    VerifiedHTTPSConnection,
    ssl,
    socket,
    match_hostname,
    HTTPConnectionPool,
    HTTPSConnectionPool,
)

class CarefulHTTPConnection(HTTPConnection):
    def request(self, method, url, body=None, headers={}):
        """Send a complete request to the server."""
        self._send_request(method, url, body, headers)

    def _send_request(self, method, url, body, headers):
        header_names = dict.fromkeys([k.lower() for k in headers])

        skips = {}

        # enable skip_host and skip_accept_encoding from py2.4
        if ('host' in header_names):
            skips['skip_host'] = True
        # always skip Accept-Encoding, never inject it
        skips['skip_accept_encoding'] = True

        self.putrequest(method, url, **skips)

        if body is not None and ('content-length' not in header_names):
            self._set_content_length(body)
        for hdr, value in headers.items():
            self.putheader(hdr, value)
        if isinstance(body, str):
            # RFC 2616 Section 3.7.1 says that text default has a
            # default charset of iso-8859-1.
            body = body.encode('iso-8859-1')
        try:
            self.endheaders(body)
        except TypeError as exception: # py26
            raise exception

class CarefulHTTPSConnection(HTTPSConnection, CarefulHTTPConnection):
    pass


class CarefulVerifiedHTTPSConnection(CarefulHTTPSConnection):
    """
    Based on httplib.HTTPSConnection but wraps the socket with
    SSL certification.
    """
    cert_reqs = None
    ca_certs = None

    def set_cert(self, key_file=None, cert_file=None,
                 cert_reqs='CERT_NONE', ca_certs=None):
        ssl_req_scheme = {
            'CERT_NONE': ssl.CERT_NONE,
            'CERT_OPTIONAL': ssl.CERT_OPTIONAL,
            'CERT_REQUIRED': ssl.CERT_REQUIRED
        }

        self.key_file = key_file
        self.cert_file = cert_file
        self.cert_reqs = ssl_req_scheme.get(cert_reqs) or ssl.CERT_NONE
        self.ca_certs = ca_certs

    def connect(self):
        # Add certificate verification
        sock = socket.create_connection((self.host, self.port), self.timeout)

        # Wrap socket using verification with the root certs in
        # trusted_root_certs
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    cert_reqs=self.cert_reqs,
                                    ca_certs=self.ca_certs)
        if self.ca_certs:
            match_hostname(self.sock.getpeercert(), self.host)
CarefulVerifiedHTTPSConnection.request = CarefulHTTPConnection.request
CarefulVerifiedHTTPSConnection._send_request = CarefulHTTPConnection._send_request

# attach the modifications
requests.packages.urllib3.connectionpool.HTTPConnection = CarefulHTTPConnection
requests.packages.urllib3.connectionpool.HTTPSConnection = CarefulHTTPSConnection
requests.packages.urllib3.connectionpool.VerifiedHTTPSConnection = CarefulVerifiedHTTPSConnection

class CarefulSession(requests.sessions.Session):
    def __init__(self, *args, **kwargs):
        config = {}
        if "config" in kwargs.keys():
            config = kwargs["config"]

        if "base_headers" not in config.keys():
            config["base_headers"] = {}

        kwargs["config"] = config

        requests.sessions.Session.__init__(self, *args, **kwargs)

Careful = CarefulSession
