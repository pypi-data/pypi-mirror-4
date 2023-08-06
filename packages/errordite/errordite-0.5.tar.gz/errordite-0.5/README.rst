Python-Errordite
================

This app provides integration between Python and Errordite, a centralised
error logging and management service, not unlike Sentry, but with more
functionality around the classification and management of errors.

The application is provided in the form of a standard Python logging handler.
In order to log exceptions with Errorite, you simply use ``logging.error`` or
``logging.exception`` in your ``except`` block::

    >>> import logging
    >>> import errordite
    >>> logger = logging.getLogger(__name__)
    >>> logger.addHandler(errordite.ErrorditeHandler('token'))
    >>> try:
    ...    raise Exception()
    ... except:
    ...    # handler uses sys.exc_info() so no need to pass
    ...    # exception info explicitly.
    ...    logging.error("Something went wrong")
    >>>

Details of the implementation are best found in the code itself - it's fairly
self-explanatory.

Installation
------------

The library is available at pypi as 'errordite', and can therefore be
installed using pip::
    
    $ pip install errordite

Once installed you can import the handler::

    >>> import errordite
    >>> handler = errordite.ErrorditeHandler("your_errordite_token")

Configuration
-------------

In order to set up a valid **ErrorditeHandler** you must pass in an
Errordite API token, which you can get by signing up at http://www.errordite.com

Tests
-----

There are tests in the package - they can be run using ``unittest``::

    $ python -m unittest errordite.tests

NB These tests do log real exceptions over the wire, so you will need to be
connected to the web to run them. You will also need to set a local environment
variable (**ERRORDITE_TOKEN**), which is picked up in the test suite.

If you are \*nix you can pass this in on the command line::

    $ ERRORDITE_TOKEN=123 python -m unittest errordite.tests

If you are on Windows you'll need to set it up explicitly as an env var::

    c:\> set ERRORDITE_TOKEN=123
    c:\> python -m unittest errordite.tests

(This is a technique used to prevent having to have sensitive information in
the public repo.)
