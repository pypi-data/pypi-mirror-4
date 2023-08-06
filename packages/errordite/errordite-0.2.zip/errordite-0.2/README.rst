Python-Errordite
================

This app provides integration between Python and Errordite, a centralised
error logging and management service, not unlike Sentry, but with a more
functionality around the classification and management of errors.

The application is provided in the form of a standard Python logging handler.
In order to log exceptions with Errorite, you simply use ``logging.error`` or
``logging.exception`` in your *except* block:

    >>> import logging
    >>> import errordite
    >>> logger = logging.getLogger(\_\_name\_\_)
    >>> logger.addHandler(errordite.ErrorditeHandler('token'))
    >>> try:
    ...    raise Exception()
    ... except:
    ...    logging.error("Something went wrong")
    >>>

Details of the implementation are best found in the code itself - it's fairly
self-explanatory.

Configuration
-------------

In order to set up a valid ErrorditeHandler you must pass in an Errordite API
token, which you can get by signing up at www.errordite.com

Installation
------------

The library is available at pypi as 'python-errordite', and can therefore be
installed using pip:

    $ pip install python-errordite

Once installed you can import the handler:

    >>> import errordite
    >>> handler = errordite.ErrorditeHandler("your_errordite_token")

Tests
-----

There are tests in the package - they can be run using unittest:

    $ python -m unittest errordite.tests

NB These tests do log real exceptions over the wire, so you will need to be
connected to the web to run them. You will also need to set a local environment
variable (ERRORDITE_TOKEN), which is picked up in the test suite. This is a
technique used to prevent having to have sensitive information in the public
repo.

If you are *nix you can pass this in on the command line:

    $ ERRORDITE_TOKEN=123 python -m unittest erroridite.tests

If you are on Windows you'll need to set it up:

    c:\> set ERRORDITE_TOKEN=123
    c:\> python -m unittest erroridite.tests
