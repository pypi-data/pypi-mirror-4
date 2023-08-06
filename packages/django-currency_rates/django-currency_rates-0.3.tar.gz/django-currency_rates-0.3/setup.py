#!/usr/bin/env python

from distutils.core import setup
from currency_rates import  __version__, __author__, __email__


long_description = open('README.rst').read()


setup(
    name='django-currency_rates',
    version=__version__,
    url='http://bitbucket.org/ferranp/django-currency-rates',
    author=__author__,
    author_email=__email__,
    license='GPL',
    packages=['currency_rates',
                'currency_rates.management',
                'currency_rates.management.commands'],
    package_data={'openonmobile': ['fixtures/*.json']},
    data_files=[('', ['README.rst'])],
    description='Currencies & echange rates for django projects',
    long_description=long_description,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
)
