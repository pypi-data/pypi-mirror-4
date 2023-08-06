class UnipagException(Exception):
    """Parent for all Unipag exceptions."""

    def __init__(self, msg=None, http_code=None, http_body=None,
                 json_body=None):
        super(UnipagException, self).__init__(msg)
        self.http_code = http_code
        self.http_body = http_body
        self.json_body = json_body

class ConnectionError(UnipagException):
    """Unable to connect to Unipag API."""

class APIError(UnipagException):
    """There is a problem with Unipag API."""

class Unauthorized(UnipagException):
    """Requested method can not be used with the API key provided."""

class BadRequest(UnipagException):
    """Some of parameters passed to Unipag were invalid."""

class NotFound(UnipagException):
    """Requested object does not exist in Unipag."""

class MethodNotAllowed(UnipagException):
    """Requested object does not exist in Unipag."""

class InternalError(UnipagException):
    """Internal Unipag error."""

class ServiceUnavailable(UnipagException):
    """There was a problem while trying to fulfill your request."""
