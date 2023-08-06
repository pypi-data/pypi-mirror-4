"""
Definition of ErrorditeHandler. Imported into package root.
"""
import logging
import sys
import traceback
import datetime
import platform
import requests
import json

# see https://www.errordite.com/help/senderrorwithjson for details:
ERRORDITE_API_URL = 'https://www.errordite.com/receiveerror'


class ErrorditeHandler(logging.Handler):
    """
    Log handler used to send exceptions to errordite.
    """
    def __init__(self, token):
        """
        Args:
            token: the auth token for access to the API - see errordite.com
        """
        logging.Handler.__init__(self)
        self.token = token

    def enrich_errordite_payload(self, payload, record):
        """
        Create the Errordite JSON from the log record.

        This is a separate method that can be overridden in subclasses.
        This decouples specific framework exception (e.g. Django) from
        basic exceptions that may not, for instance, include HTTP request
        information.

        If you are subclassing this you should always call the base
        implementation first as this fills the basic information out.

        Args:
            record: the logger record passed to the emit method.

        Returns:
            JSON-serializable dictionary that can be sent to Errordite
            as the HTTP payload.
        """
        return payload

    def emit(self, record):
        """
        Sends exception info to Errordite.

        This handler will ignore the log level, and look for an exception
        within the record (as recored.exc_info) or current stack frame
        (sys.exc_info()). If it finds neither, it will simply return without
        doing anything.
        """
        if not self.token:
            raise Exception("Missing Errordite service token.")

        if record.levelname == 'EXCEPTION':
            exc_info = record.exc_info
        else:
            exc_info = sys.exc_info()

        if exc_info == (None, None, None):
            # we can't find an exception to report on, so just return
            return

        ex_type, ex_value, ex_tb = exc_info
        ex_source = traceback.extract_tb(ex_tb)[-1]

        payload = {
            "TimestampUtc": datetime.datetime.utcnow().isoformat(),
            "Token": self.token,
            "MachineName": platform.node(),
            "ExceptionInfo": {
                "Message": record.msg % record.args,
                "Source": '%s: line %s' % (ex_source[0], ex_source[1]),
                "ExceptionType": '%s.%s' % (ex_type.__module__, ex_type.__name__),
                "StackTrace": traceback.format_exc(),
                "MethodName": ex_source[2]
            }
        }
        if hasattr(record, 'version'):
            payload['Version'] = record.version

        # enrich with additional, non-core information. This may be sub-
        # classed
        payload = self.enrich_errordite_payload(payload, record)

        try:
            requests.post(
                ERRORDITE_API_URL,
                data=json.dumps(payload),
                headers={'content-type': 'application/json'}
            )
            # since we already in the logger, logging an error, there's
            # there's really nothing we can do with the response that adds
            # any value - so ignore it.
            return 'ok'

        except:
            self.handleError(record)
