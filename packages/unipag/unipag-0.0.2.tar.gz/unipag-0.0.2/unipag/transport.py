from base64 import b64encode
import platform
from .exceptions import *
from .version import version
import warnings
import textwrap

try:
    import simplejson as json
except ImportError:
    import json

# TODO: use urlfetch for Google App Engine
try:
    import requests
    _session = requests.session()
    _lib = 'requests'
    _lib_ver = requests.__version__
except ImportError:
    warnings.warn(
        '\n\n' + textwrap.fill(
            'requests library is not available, falling to urllib2. '
            'Note that urllib2 does NOT verifies SSL certificates, so '
            'we recommend to install requests, if possible.'
        )
    )
    import urllib
    import urllib2
    _lib = 'urllib2'
    _lib_ver = urllib2.__version__

class API(object):
    def __init__(self, key=None, base_url=None):
        from .defaults import api_key, api_url
        self.api_key = key or api_key
        self.base_url = base_url or api_url

    def url(self, url):
        return '%s%s' % (self.base_url, url)

    def urllib2_request(self, method, url, data, headers, timeout):
        params = urllib.urlencode(data)
        if method == 'get':
            abs_url = '%s?%s' % (url, params)
            req = urllib2.Request(abs_url, None, headers)
        elif method == 'post':
            req = urllib2.Request(url, params, headers)
        elif method == 'delete':
            abs_url = '%s?%s' % (url, params)
            req = urllib2.Request(abs_url, None, headers)
            req.get_method = lambda: 'DELETE'
        else:
            raise APIError, 'Unsupported method: %s' % method

        try:
            response = urllib2.urlopen(req, timeout=timeout)
            http_code = response.code
            http_body = response.read()
        except urllib2.HTTPError, e:
            http_code = e.code
            http_body = e.read()
        return http_code, http_body

    def request(self, method, url, params={}):
        if not self.api_key:
            raise Unauthorized(
                'You did not provide an API key. There are 2 ways to do it:\n'
                '\n1) set it globally for all requests via '
                'unipag.defaults.api_key, like this:\n'
                '\nimport unipag.defaults\n'
                '\nunipag.defaults.api_key = "<your-key>"\n'
                '\n'
                '\n2) pass it to methods which communicate with the API as '
                'keyword argument, like this:\n'
                '\nfrom unipag import Invoice\n'
                '\ninv = Invoice.create(api_key="<your-key>", ...)'
            )

        abs_url = self.url(url)

        client_info = {
            'publisher': 'Unipag',
            'platform': platform.platform(),
            'language': 'Python %s' % platform.python_version(),
            'httplib': '%s v%s' % (_lib, _lib_ver)
        }

        headers = {
            'Authorization': 'Basic %s' % b64encode('%s:' % self.api_key),
            'User-Agent': 'Unipag Client for Python, v%s' % version,
            'X-Unipag-User-Agent-Info': json.dumps(client_info)
        }

        # Do not pass params with None values
        data = {}
        for k, v in params.items():
            if v is not None:
                data[k] = v

        # Send request to API and handle communication errors
        if _lib == 'requests':
            try:
                response = _session.request(
                    method,
                    abs_url,
                    data=data,
                    headers=headers,
                    timeout=60
                )
                http_code = response.status_code
                http_body = response.content
            except requests.RequestException as e:
                raise ConnectionError(
                    'Cannot connect to Unipag API using URL %s' % abs_url
                )
        elif _lib == 'urllib2':
            try:
                http_code, http_body = self.urllib2_request(
                    method,
                    abs_url,
                    data=data,
                    headers=headers,
                    timeout=60
                )
            except urllib2.URLError as e:
                raise ConnectionError(
                    'Cannot connect to Unipag API using URL %s' % abs_url
                )

        # For some reason, in live environment http body is not returned 
        # when 401. This behaviour is not reproduced when using development 
        # django runserver. The following 2 lines are just a quick workaround.
        # TODO: investigate and fix.
        if http_code == 401:
            raise Unauthorized('TODO: Return normal error message here.')

        try:
            json_body = json.loads(http_body)
        except Exception as e:
            raise APIError(
                'Invalid response from the API: %s' % http_body, 
                http_code, 
                http_body
            )

        # Handle API errors
        if http_code != 200:
            try:
                error = json_body['error']
                err_desc = error['description']
                err_params = {}
                err_params.update(error.get('params', {}))
            except (KeyError, TypeError, ValueError):
                raise APIError(
                    'Invalid response from the API: %s' % json_body, 
                    http_code, 
                    http_body, 
                    json_body
                )

            if http_code == 400:
                err_msg = err_desc
                if err_params:
                    err_msg += '\nParams:\n' + '\n'.join(
                        ['%s: %s' % (k, v) for k, v in err_params.items()]
                    )
                raise BadRequest(err_msg, http_code, http_body, json_body)
            elif http_code == 401:
                raise Unauthorized(err_desc, http_code, http_body, json_body)
            elif http_code == 404:
                raise NotFound(err_desc, http_code, http_body, json_body)
            elif http_code == 405:
                raise NotFound(err_desc, http_code, http_body, json_body)
            elif http_code == 500:
                raise InternalError(err_desc, http_code, http_body, json_body)
            elif http_code == 503:
                raise ServiceUnavailable(
                    err_desc, http_code, http_body, json_body
                )
            else:
                raise APIError(err_desc, http_code, http_body, json_body)

        return json_body