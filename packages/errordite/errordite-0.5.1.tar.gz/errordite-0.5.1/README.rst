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

**Important info regarding sys.exc_info() and sys.exc_clear()**

This logging handler is explicitly designed to capture and publish Python
exceptions. It is not a generic logger, and as such it relies on the use of
``sys.exc_info()`` to determine whether there is anything to report. This can
have an unexpected effect if you are logging items as errors that have no
explicit exception attached, but where a previous exception has been swallowed.

In the example below - we are catching and swallowing the DoesNotExist error
because it's a known code path. However, the exception does still exist and
if you call sys.exc_info() further on it will return this exception::

    try:
        .. do something that raises a known error - e.g. model.DoesNotExist
    except model.DoesNotExist:
        .. we half expected this, so just ignore it for now

A little further on in our example we are logging a business exception (trying
to checkout a negative basket value) but not attaching any explicit python
error::

    .. continue on with the method
    .. some time later

    if basket_total < 0:
        logger.error("Someone tried to hack out checkout.")

**In this case the wrong exception information will be recorded.**

The solution to this is to call ``sys.exc_clear()`` in the ``except`` block
so that the exception is removed explicitly. The Python docs state that:

 *This function is only needed in only a few obscure situations.*

Which suggest that this is not recommended, however, they go on to state:

 *These include logging and error handling systems that report information
 on the last or current exception.*

It is the author's opinion that this describes our exact predicament, and so
the use of ``sys.exc_clear()`` is justified. 

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
