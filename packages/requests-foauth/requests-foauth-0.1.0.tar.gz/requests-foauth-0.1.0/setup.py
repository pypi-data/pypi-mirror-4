# -*- coding: utf-8 -*-
"""
requests-foauth
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

from setuptools import setup

setup(
    name='requests-foauth',
    version='0.1.0',
    url='https://github.com/kennethreitz/requests-foauth',
    license='BSD',
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    description='Requests TransportAdapter for foauth.org!',
    long_description=__doc__,
    py_modules=['requests_foauth'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
