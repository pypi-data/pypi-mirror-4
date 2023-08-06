"""
Django-aware exception handler for integration with Errordite.

Adds django user and request information to the exception as appropriate.
"""
from errordite import ErrorditeHandler


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
            return payload

        rq = record.request
        payload['Url'] = rq.get_full_path()

        if 'HTTP_USER_AGENT' in rq.META:
            payload['UserAgent'] = rq.META['HTTP_USER_AGENT']

        data = payload['ExceptionInfo'].get('Data', {})

        if 'HTTP_X_FORWARDED_FOR' in rq.META:
            data['X-Forwarded-For'] = rq.META['HTTP_X_FORWARDED_FOR']
        if 'REMOTE_ADDR' in rq.META:
            data['client_ip'] = rq.META['REMOTE_ADDR']

        if hasattr(rq, 'user'):
            if rq.user is not None:
                if rq.user.is_anonymous():
                    data['user'] = "anonymous"
                else:
                    data['user'] = rq.user.username

        # prepend request GET/POST keys with 'GET_'/'POST_' and add to data
        if rq.method == 'GET':
            data.update({('GET_%s' % k): v for k, v in rq.GET.dict().items()})
        elif rq.method == 'POST':
            data.update({('POST_%s' % k): v for k, v in rq.POST.dict().items()})

        payload['ExceptionInfo']['Data'] = data
        return payload
