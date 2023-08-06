# -*- coding: utf-8 -*-

import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse



# Register database schemes in URLs.
urlparse.uses_netloc.append('mongodb')

DEFAULT_ENV = 'MONGOHQ_URL'

SCHEMES = {
    'mongodb': 'django_mongodb_engine',
}


def config(env=DEFAULT_ENV, default=None):
    """Returns configured DATABASE dictionary from MONGOHQ_URL."""

    config = {}

    s = os.environ.get(env, default)

    if s:
        config = parse(s)

    return config


def parse(url):
    """Parses a database URL."""

    config = {}

    url = urlparse.urlparse(url)

    # Remove query strings.
    path = url.path[1:]
    path = path.split('?', 2)[0]

    # Update with environment configuration.
    config.update({
        'NAME': path,
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port,
    })

    if url.scheme in SCHEMES:
        config['ENGINE'] = SCHEMES[url.scheme]

    return config
