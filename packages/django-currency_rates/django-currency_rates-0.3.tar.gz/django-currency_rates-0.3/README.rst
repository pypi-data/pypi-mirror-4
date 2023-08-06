=====================
django-currency-rates
=====================

Django currencies and exchange rates for django projects

You need a key from http://openexchangerates.org/ to get the echange rates

Features
========

- Currencies and exchange rates models
- Exchange rates with diferent rates for diferent dates
- Load automatically currencies and rates from http://openexchangerates.org/

Installation
============

#. Add ``"currency_rates"`` directory to your Python path.
#. Add ``"currency_rates"`` to the ``INSTALLED_APPS`` tuple found in
   your settings file.
#. Add ``OPENEXCHANGERATES_APP_ID`` to your setting file with an app key from http://openexchangerates.org/
#. Run ``manage.py syncdb`` to create the new tables or ``manage.py migrate`` is you are using South_
#. Run ``manage.py load_currencies`` to load currencies from http://openexchangerates.org/
#. Run ``manage.py load_rates`` to load current eschange rates from http://openexchangerates.org/

Migrate to v0.3
===============

On version v0.3 we changed the curency name length from 25 to 50 and we adopted south for
the schema migrations.

If you have installed **django-currency-rates** version v0.1 or v0.2 and want to migrate,
first you have to install South_ update the **django-currency-rates** app and then you have to execute
the first migration as fake with ::
   
    ./manage.py migrate currency_rates 0001_initial --fake
    ./manage.py migrate currency_rates


.. _South: http://south.aeracode.org/
