"""
Gah. requests-1.x breaks proxies, so now we do it all over again for
requests-0.14.2 this time.
"""

import requests
import requests.packages.urllib3

from requests.packages.urllib3.connectionpool import HTTPConnection

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
        skips['skip_accept_encoding'] = True

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

requests.packages.urllib3.connectionpool.HTTPConnection = CarefulHTTPConnection
