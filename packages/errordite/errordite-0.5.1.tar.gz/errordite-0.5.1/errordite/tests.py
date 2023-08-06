"""
Basic tests for errordite log handler.

You will need a valid Errordite account in order to run these tests,
and will need to set a local environment variable ERRORDITE_TOKEN with
your Errordite account token. (This is so that the token is not stored
in the public repo.)
"""
import os
import unittest
import logging
from . import ErrorditeHandler

ERRORDITE_TOKEN = os.environ.get("ERRORDITE_TOKEN", None)
if ERRORDITE_TOKEN is None:
    raise Exception("You must set environment variable ERRORDITE_TOKEN "
        "before running these tests.")


class ErrorditeHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.handler = ErrorditeHandler(ERRORDITE_TOKEN)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(self.handler)
        self.logger.level = logging.DEBUG
        self.assertEqual(len(self.logger.handlers), 1)

    def tearDown(self):
        self.logger.handlers = []

    def test_logging_no_exception_does_nothing(self):
        "Test that a log record with no exc_info doesn't do anything."
        func = self.test_logging_no_exception_does_nothing
        self.logger.debug(func.__doc__)

    def test_logging_error(self):
        "Test logging a real exception with logging.error."
        func = self.test_logging_error
        try:
            throw_exception(func.__name__)
        except CustomException:
            self.logger.error(func.__doc__)
            print ("Please check Errordite for a new issue with the "
                "messsage '%s'" % func.__doc__)

    def test_logging_exception(self):
        "Test logging a real exception with logging.exception."
        func = self.test_logging_exception
        try:
            throw_exception(func.__name__)
        except CustomException:
            self.logger.exception(func.__doc__)
            print ("Please check Errordite for a new issue with the "
                "messsage '%s'" % func.__doc__)

    def test_logging_with_complex_message(self):
        "Test the user of format string and args in logged message."
        func = self.test_logging_with_complex_message
        try:
            throw_exception(func.__name__)
        except CustomException:
            self.logger.exception("%s: %s", func.__doc__, 'ok')
            print ("Please check Errordite for a new issue with the "
                "messsage '%s'" % func.__doc__)


class CustomException(Exception):
    def __init__(self, message):
        super(CustomException, self).__init__(message)


def throw_exception(message):
    raise CustomException(message)
