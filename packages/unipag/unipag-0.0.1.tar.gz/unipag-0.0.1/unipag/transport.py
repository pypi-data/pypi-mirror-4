import base64
import platform
from .exceptions import *
from .version import version

try:
    import simplejson as json
except ImportError:
    import json


# TODO: use urlfetch for Google App Engine
# TODO: fallback to URLLib2 if requests lib is unavailable
import requests
_session = requests.session()

class API(object):
    def __init__(self, key=None, base_url=None):
        from .defaults import api_key, api_url
        self.api_key = key or api_key
        self.base_url = base_url or api_url

    def url(self, url):
        return '%s%s' % (self.base_url, url)

    def request(self, method, url, params={}):

        if not self.api_key:
            raise Unauthorized('You did not provide an API key. There are 2 ways to do it:\n'
                               '\n1) set it globally for all requests via unipag.defaults.api_key, like this:\n'
                               '\nimport unipag.defaults\n\nunipag.defaults.api_key = "<your-key>"\n\n'
                               '\n2) pass it to methods which communicate with the API as keyword argument, '
                               'like this:\n'
                               '\nfrom unipag import Invoice\n\ninv = Invoice.create(api_key="<your-key>", ...)')

        abs_url = self.url(url)

        client_info = {
            'publisher': 'Unipag',
            'platform': platform.platform(),
            'language': 'Python %s' % platform.python_version(),
            'httplib': 'Requests v%s' % requests.__version__
        }

        headers = {
            'Authorization': 'Basic %s' % base64.b64encode('%s:' % self.api_key),
            'User-Agent': 'Unipag Client for Python, v%s' % version,
            'X-Unipag-User-Agent-Info': json.dumps(client_info)
        }

        # Do not pass params with None values
        data = {}
        for k, v in params.items():
            if v is not None:
                data[k] = v

        # Send request to API and handle communication errors
        try:
            response = _session.request(method, abs_url, data=data, headers=headers, timeout=60)
            http_code = response.status_code
            http_body = response.content
        except requests.RequestException as e:
            raise ConnectionError('Cannot connect to Unipag API using URL %s' % abs_url)

        # For some reason, in live environment http body is not returned when 401.
        # This behaviour is not reproduced when using development django runserver.
        # The following 2 lines are just a quick workaround. TODO: investigate and fix.
        if http_code == 401:
            raise Unauthorized('TODO: Return normal error message here.')

        try:
            json_body = json.loads(http_body)
        except Exception as e:
            raise APIError('Invalid response from the API: %s' % http_body, http_code, http_body)

        # Handle API errors
        if http_code != 200:
            try:
                error = json_body['error']
                error_description = error['description']
                error_params = {}
                error_params.update(error.get('params', {}))
            except (KeyError, TypeError, ValueError):
                raise APIError('Invalid response from the API: %s' % json_body, http_code, http_body, json_body)

            if http_code == 400:
                err_msg = error_description
                if error_params:
                    err_msg += '\nParams:\n' + '\n'.join(['%s: %s' % (k, v) for k, v in error_params.items()])
                raise BadRequest(err_msg, http_code, http_body, json_body)
            elif http_code == 401:
                raise Unauthorized(error_description, http_code, http_body, json_body)
            elif http_code == 404:
                raise NotFound(error_description, http_code, http_body, json_body)
            elif http_code == 405:
                raise NotFound(error_description, http_code, http_body, json_body)
            elif http_code == 500:
                raise InternalError(error_description, http_code, http_body, json_body)
            elif http_code == 503:
                raise ServiceUnavailable(error_description, http_code, http_body, json_body)
            else:
                raise APIError(error_description, http_code, http_body, json_body)

        return json_body