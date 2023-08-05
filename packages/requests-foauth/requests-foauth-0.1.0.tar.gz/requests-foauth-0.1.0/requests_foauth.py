# -*- coding: utf-8 -*-

"""
requests_foauth
~~~~~~~~~~~~~~~

This module provides an foauth.org TransportAdapter for Requests.

In short, foauth.org allows you to easily send requests to OAUth'd
services with HTTP Basic authentication. It's fantastic.

Normally, you have to send all requests to foauth.org manually, after
rewriting the URLs. With this adapter, all requests are sent through the
service transparently.

Example usage::

    import requests
    from requests_foauth import Foauth

    s = requests.Session()
    s.mount('http', Foauth('username', 'password))

    >>> s.get('https://api.500px.com/v1/users/')
    <Response [200]>
"""


from requests.adapters import BaseAdapter, HTTPAdapter
from requests.compat import urlparse

FOAUTH_TEMPLATE = 'https://foauth.org/{domain}{path}'

class Foauth(BaseAdapter):
    """The foauth.org transport adapter."""
    def __init__(self, username, password):
        self.auth = (username, password)
        self.http = HTTPAdapter()

    def prepare_request(self, request):
        p = urlparse(request.url)

        # Rewrite the url to use foauth.org
        request.url = FOAUTH_TEMPLATE.format(domain=p.netloc, path=p.path)
        # Authenticate appropriately.
        request.prepare_auth(self.auth)

        return request

    def send(self, request, **kwargs):
        request = self.prepare_request(request)
        return self.http.send(request, **kwargs)

