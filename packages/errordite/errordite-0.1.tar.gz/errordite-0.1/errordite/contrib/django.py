"""
Django-aware exception handler.

Adds django user and request information to the exception as appropriate.
"""
from .. import ErrorditeHandler


class DjangoErrorditeHandler(ErrorditeHandler):
    """
    Django-aware Errordite handler than enriches logs with request info.
    """
    def enrich_errordite_payload(self, payload, record):
        """
        Overrides base class implementation to add Django-specific error
        data - specifically user and HTTP request information.
        """
        payload = super(DjangoErrorditeHandler, self).enrich_errordite_payload(
            payload, record
        )

        if not hasattr(record, 'request'):
            return

        rq = record.request
        payload['Url'] = rq.get_full_path()

        if 'HTTP_USER_AGENT' in rq.META:
            payload['UserAgent'] = rq.META['HTTP_USER_AGENT']

        #custom fields for the exception - IP and Django user info.
        payload['ExceptionInfo']['Data'] = {
            'client-ip': rq.META.get('REMOTE_ADDR', 'unknown')
        }

        if hasattr(rq, 'user'):
            if rq.user is not None:
                if rq.user.is_anonymous():
                    payload['ExceptionInfo']['Data']['user'] = "anonymous"
                else:
                    payload['ExceptionInfo']['Data']['user'] = rq.user.username

        return payload
