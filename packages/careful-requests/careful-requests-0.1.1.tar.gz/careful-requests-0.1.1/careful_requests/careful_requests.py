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

try: # Python 3
    from http.client import HTTPConnection, HTTPException
    from http.client import HTTP_PORT, HTTPS_PORT
except ImportError:
    from httplib import HTTPConnection, HTTPException
    from httplib import HTTP_PORT, HTTPS_PORT

from requests.packages.urllib3.connectionpool import (
    ConnectionPool,
    VerifiedHTTPSConnection,
    HTTPConnectionPool,
    HTTPSConnectionPool,
)

from requests.packages.urllib3.request import RequestMethods
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.poolmanager import log as pool_log
from requests.packages.urllib3.connectionpool import port_by_scheme

class CarefulHTTPConnection(HTTPConnection):
    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)

        self.omit_headers = None

    def request(self, method, url, body=None, skip_host=False, skip_accept_encoding=False, headers={}):
        """Send a complete request to the server."""
        self._send_request(method, url, body, headers, skip_host=skip_host, skip_accept_encoding=skip_accept_encoding)

    def _send_request(self, method, url, body, headers, skip_host=False, skip_accept_encoding=False):
        header_names = dict.fromkeys([k.lower() for k in headers])

        skips = {}

        # enable skip_host and skip_accept_encoding from py2.4
        if skip_host or ('host' in header_names):
            skips['skip_host'] = 1
        if skip_accept_encoding or ('accept-encoding' in header_names):
            skips['skip_accept_encoding'] = 1

        # omit some default headers when asked
        if self.omit_headers:
            omits = [key.lower() for key in self.omit_headers]
            if "host" in omits:
                skips["skip_host"] = True
            if "accept-encoding" in omits:
                skips["skip_accept_encoding"] = True

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

try: # Compiled with SSL?
    try: # Python 3
        from http.client import HTTPSConnection
    except ImportError:
        from httplib import HTTPSConnection

    class CarefulHTTPSConnection(HTTPSConnection, CarefulHTTPConnection): pass
except (ImportError, AttributeError):
    pass

class CarefulVerifiedHTTPSConnection(VerifiedHTTPSConnection, CarefulHTTPSConnection):
    pass

class CarefulHTTPConnectionPool(HTTPConnectionPool):
    def __init__(self, *args, **kwargs):
        self.omit_headers = None
        HTTPConnectionPool.__init__(self, *args, **kwargs)

    def _new_conn(self):
        """
        Returns a fresh :class:`httplib.HTTPConnection`.
        """
        self.num_connections += 1
        pool_log.info("Starting new HTTP connection (%d): %s" %
                 (self.num_connections, self.host))
        return CarefulHTTPConnection(host=self.host,
                                    port=self.port,
                                    strict=self.strict)

    def urlopen(self, *args, **kwargs):
        #if "omit_headers" in kwargs.keys():
        #    omit_headers = kwargs["omit_headers"]
        #    del kwargs["omit_headers"]
        #    self.omit_headers = omit_headers
        #else:
        #    self.omit_headers = None
        # urlopen calls _make_request which sets conn.omit_headers
        return HTTPConnectionPool.urlopen(self, *args, **kwargs)

    def _make_request(self, conn, method, url, **kwargs):
        conn.omit_headers = self.omit_headers
        return HTTPConnectionPool._make_request(self, conn, method, url, **kwargs)

# inherit from CarefulHTTPConnectionPool to get the better urlopen
class CarefulHTTPSConnectionPool(HTTPSConnectionPool, CarefulHTTPConnectionPool):
    def _new_conn(self):
        """
        Return a fresh :class:`httplib.HTTPSConnection`.
        """
        self.num_connections += 1
        pool_log.info("Starting new HTTPS connection (%d): %s"
                 % (self.num_connections, self.host))

        if not ssl: # Platform-specific: Python compiled without +ssl
            if not CarefulHTTPSConnection or CarefulHTTPSConnection is object:
                raise SSLError("Can't connect to HTTPS URL because the SSL "
                               "module is not available.")

            return CarefulHTTPSConnection(host=self.host,
                                         port=self.port,
                                         strict=self.strict)

        connection = CarefulVerifiedHTTPSConnection(host=self.host,
                                                   port=self.port,
                                                   strict=self.strict)
        connection.set_cert(key_file=self.key_file, cert_file=self.cert_file,
                            cert_reqs=self.cert_reqs, ca_certs=self.ca_certs)

        if self.ssl_version is None:
            connection.ssl_version = ssl.PROTOCOL_SSLv23
        else:
            connection.ssl_version = self.ssl_version

        return connection

class CarefulPoolManager(PoolManager):
    pool_classes_by_scheme = {
        "http": CarefulHTTPConnectionPool,
        "https": CarefulHTTPSConnectionPool,
    }

    def connection_from_host(self, host, port=None, scheme='http'):
        """
        Get a :class:`ConnectionPool` based on the host, port, and scheme.

        If ``port`` isn't given, it will be derived from the ``scheme`` using
        ``urllib3.connectionpool.port_by_scheme``.
        """
        port = port or port_by_scheme.get(scheme, 80)

        pool_key = (scheme, host, port)

        # If the scheme, host, or port doesn't match existing open connections,
        # open a new ConnectionPool.
        pool = self.pools.get(pool_key)
        if pool:
            return pool

        # Make a fresh ConnectionPool of the desired type.
        # Use self.pool_classes_by_scheme instead of urllib3 defaults.
        pool_cls = self.pool_classes_by_scheme[scheme]
        pool = pool_cls(host, port, **self.connection_pool_kw)

        self.pools[pool_key] = pool

        return pool

class CarefulHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize):
        self.poolmanager = CarefulPoolManager(num_pools=connections, maxsize=maxsize)

    def send(self, request, **kwargs):
        omit_headers = None
        if "omit_headers" in kwargs.keys():
            omit_headers = kwargs["omit_headers"]
            del kwargs["omit_headers"]
        # get an existing or new connection
        conn_pool = self.get_connection(request.url, proxies=kwargs["proxies"])
        # store omit_headers
        conn_pool.omit_headers = omit_headers
        # HTTPAdapter.send will call get_connection and get back this conn_pool
        return requests.adapters.HTTPAdapter.send(self, request, **kwargs)

    # An alternative implementation might choose to rewrite send to pass
    # omits_headers to urlopen.

class CarefulSession(requests.Session):
    def __init__(self, *args, **kwargs):
        always_omit = None
        if "always_omit" in kwargs.keys():
            always_omit = kwargs["always_omit"]
            del kwargs["always_omit"]

        omit_headers = set()
        if "omit_headers" in kwargs.keys():
            omit_headers = kwargs["omit_headers"]
            del kwargs["omit_headers"]

            # Persistent by default if the session was created with
            # omit_headers.
            if omit_headers != None and len(omit_headers) > 0:
                if always_omit == None:
                    always_omit = True
                elif always_omit == False:
                    raise Exception("Can't use session-level omit_headers when explicitly not using always_omit.")

        requests.Session.__init__(self, *args, **kwargs)

        self.always_omit = always_omit
        self.default_omit_headers = set(omit_headers)
        self.headers = {}

        self.adapters = {}
        self.mount("http://", CarefulHTTPAdapter())
        self.mount("https://", CarefulHTTPAdapter())

    def request(self, *args, **kwargs):
        if "omit_headers" in kwargs.keys():
            self.omit_headers = set(kwargs["omit_headers"])
            del kwargs["omit_headers"]
        elif not self.always_omit:
            self.omit_headers = set()
        elif self.always_omit:
            self.omit_headers = self.default_omit_headers
        r = requests.Session.request(self, *args, **kwargs)
        return r

    def send(self, request, **kwargs):
        if self.omit_headers:
            kwargs["omit_headers"] = self.omit_headers
        adapter = self.get_adapter(url=request.url)
        r = adapter.send(request, **kwargs)
        return r
Careful = CarefulSession

