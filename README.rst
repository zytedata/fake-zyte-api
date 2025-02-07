==================
fake-zyte-api
==================

.. image:: https://img.shields.io/pypi/v/fake-zyte-api.svg
   :target: https://pypi.org/pypi/fake-zyte-api
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/fake-zyte-api.svg
   :target: https://pypi.python.org/pypi/fake-zyte-api
   :alt: Supported Python Versions

.. image:: https://github.com/zytedata/fake-zyte-api/workflows/tox/badge.svg
   :target: https://github.com/zytedata/fake-zyte-api/actions
   :alt: Build Status

.. image:: https://codecov.io/github/zytedata/fake-zyte-api/coverage.svg?branch=master
   :target: https://codecov.io/gh/zytedata/fake-zyte-api
   :alt: Coverage report

Overview
========

fake-zyte-api provides a server that implements a subset of Zyte API that is
able to scrape the websites provided by ``zyte-test-websites``.

Run it with:

.. code-block:: console

    $ python -m fake_zyte_api.main 8899

You can use the http://localhost:8899/extract endpoint in your requests.

Requirements
============

* Python >= 3.9
* aiohttp
