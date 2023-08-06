# -*- coding: utf-8 -*-
"""
dj-mongohq-url
~~~~~~~~~~~~~~~

.. image:: https://secure.travis-ci.org/ferrix/dj-mongohq-url.png?branch=master

This simple Django utility allows you to utilize the
`12factor <http://www.12factor.net/backing-services>`_ inspired
``MONGOURL_URL`` environment variable to configure your Django application.

This is a slight adaptation of the dj-database-url by Kenneth Reitz
(http://github.com/kennethreitz/dj-database-url/). It is compatible with
django-nonrel_ and can be used to dig up the URL setting for other purposes
as well.


.. _django-nonrel: https://github.com/django-nonrel/mongodb-engine/

Usage
-----

Configure your database in ``settings.py`` from ``DATABASE_URL``::

    DATABASES = {'default': dj_mongohq_url.config()}

Parse an arbitrary Database URL::

    DATABASES = {'default': dj_mongohq_url.parse('mongodb://...')}

If you are not using Django with nonrel capabilities and merely want to
dig up the MongoDB settings, use another variable::

    MONGODB = dj_mongohq_url.config()

Supported databases
-------------------

Support currently exists for MongoDB.

"""

from setuptools import setup

setup(
    name='dj-mongohq-url',
    version='0.0.1',
    url='https://github.com/ferrix/dj-mongohq-url',
    license='BSD',
    author='Ferrix Hovi',
    author_email='ferrix+github@ferrix.fi',
    description='Use MongoDB URLs in your Django Application.',
    long_description=__doc__,
    py_modules=['dj_mongohq_url'],
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
