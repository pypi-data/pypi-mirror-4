from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
import logging


class ErrorditeHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger('errordite_logger')
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_log_error(self):
        try:
            throw_exception("test_log_error")
        except:
            self.logger.error('This is an ERROR message')

    def test_with_request(self):
        try:
            throw_exception("test_with_request")
        except:
            self.logger.error(
                'This is an ERROR message',
                extra={"request": self.request}
            )

    def test_with_request_and_anonymous_user(self):
        try:
            self.request.user = AnonymousUser()
            throw_exception("test_with_request_and_anonymous_user")
        except:
            self.logger.error(
                'This is an ERROR message',
                extra={"request": self.request}
            )

    def test_with_request_and_known_user(self):
        try:
            self.request.user = User.objects.create_user(
                "fred", "fred@example.com", "fred's password"
            )
            throw_exception("test_with_request_and_anonymous_user")
        except:
            self.logger.error(
                'This is an ERROR message',
                extra={"request": self.request}
            )


class CustomException(Exception):
    pass


def throw_exception(message):
    raise CustomException(message)
