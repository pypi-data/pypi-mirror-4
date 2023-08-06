# -*- coding: utf-8 -*-

"""
bluevia.exceptions
~~~~~~~~~~~~~~~~~~

This module contains the set of pyBlueVia's exceptions.

"""


class BVException(Exception):
    """The base pyBlueVia exception from which other exceptions inherit.
    It can be used to catch any pyBlueVia exception.

    """
    pass


class APIError(BVException):

    """BlueVia has returned an API exception. Details can be got through the following attributes: """

    def __init__(self, resp):
        #: the HTTP status code returned by BlueVia.
        self.http_status_code = resp.status_code
        #: a description (if available) of the HTTP status code.
        self.http_reason = resp.reason  # TODO: Corregir acento: Petici�n incorrecta
        if resp.headers['content-type'] and resp.headers['content-type'].startswith('application/json'):
            content = resp.json()
            if 'exceptionId' in content:
                #: the exception id as returned by BlueVia (it might be ``None``).
                self.id = content['exceptionId']
                #: the exception description as returned by BlueVia.
                self.message = content['exceptionText']
            elif 'error' in content:
                self.message = content['error']
        else:
            self.message = resp.content

    def __str__(self):
        msg = 'API error: [{0} {1}]'.format(self.http_status_code, self.http_reason)
        if hasattr(self, 'id'):
            msg += ' {0}: {1}'.format(self.id, self.message)
        else:
            msg += ' {0}'.format(self.message)

        return msg


class ContentTypeError(BVException):
    """Unsupported Content-Type. """
    pass


class AccessTokenError(BVException):
    """Trying to call a method which needs *access token* and it has not been set. """
    pass


class AuthResponseError(BVException):
    """An error occurred trying to parse the URI to which the Authorization Server redirects after finishing
    the authorization process. """
    pass
