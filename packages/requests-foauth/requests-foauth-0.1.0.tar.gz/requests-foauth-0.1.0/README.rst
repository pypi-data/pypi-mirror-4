requests-foauth
===============

This module provides an foauth.org TransportAdapter for Requests.

In short, foauth.org allows you to easily send requests to OAUth'd
services with HTTP Basic authentication. It's fantastic.

Normally, you have to send all requests to foauth.org manually, after
rewriting the URLs. With this adapter, all requests are sent through the
service transparently.

Example usage
~~~~~~~~~~~~~

::

    import requests
    from requests_foauth import Foauth

    s = requests.Session()
    s.mount('http', Foauth('username', 'password))

    >>> s.get('https://api.500px.com/v1/users/')
    <Response [200]>
