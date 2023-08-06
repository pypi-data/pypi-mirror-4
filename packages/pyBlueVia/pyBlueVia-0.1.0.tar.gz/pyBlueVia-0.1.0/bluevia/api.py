# -*- coding: utf-8 -*-

"""
bluevia.api
~~~~~~~~~~~

This module implements the pyBlueVia API class.

:copyright: (c) 2013 Telefonica Investigación y Desarrollo, S.A.U.
:license: Apache 2.0, see LICENSE for more details.

"""

import logging
#import uuid
import urllib
import urlparse

from .base_api import BaseApi
from .exceptions import AuthResponseError


log = logging.getLogger(__name__)


# OAuth scopes
SMS_MT = 'sms.send'
MMS_MT = 'mms.send'


class Api(BaseApi):

    """This is the main pyBlueVia class, which wraps the BlueVia API.

    The first step to use pyBlueVia is to create an :class:`Api <Api>` object.

    :param client_id: OAuth 2.0 *client id*.
    :param client_secret: OAuth 2.0 *client secret*.
    :param access_token: (optional) OAuth 2.0 *access token* needed to send sms and mms or to get their delivery
        status. If not provided here it can be set later setting the attribute :attr:`access_token` or during
        the OAuth authorization process when calling :meth:`get_access_token`.
    :param sandbox: (optional) set to ``True`` in order to use the BlueVia Sandbox feature. Default is ``False``.
    :type sandbox: bool

    Usage::

        >>> import bluevia
        >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
        >>> bluevia_client.send_sms(to='34600000000', message='Hello world!')

    """

    # API endpoints
    _API_BASE_URL = 'https://live-api.bluevia.com/'
    _SB_API_BASE_URL = 'https://sandbox-api.bluevia.com/'
    _AUTH_BASE_URL = 'https://id.tu.com/'

    PATHS = {
        'access_token': 'oauth2/token'
    }

    def __init__(self, client_id, client_secret, access_token=None, sandbox=False):
        base_url = self._SB_API_BASE_URL if sandbox else self._API_BASE_URL
        self.auth_base_url = self._AUTH_BASE_URL

        BaseApi.__init__(self, base_url, client_id, client_secret, access_token=access_token)

        self.sandbox = sandbox
        self.oauth_redirect_uri = self.oauth_state = None

    def get_authorization_uri(self, scope, redirect_uri=None, state=None):

        """Build the OAuth authorization URI.

        As a first step to get an access token (needed to call some of the BlueVia APIs) the user must
        be redirected to the Authorization Server, where she will authorize your app to make such calls
        on her behalf.
        The URI where the user must be redirected is built by this method based on the input parameters.

        :param scope: *scope* (or array/tuple of scopes) for which the authorization is requested.
            Supported *scope* values are: ``bluevia.SMS_MT`` and ``bluevia.MMS_MT`` which ask for permission
            to send SMS and MMS, respectively (and ask for the delivery status).
        :param redirect_uri: (optional) following the OAuth dance, after completing the authorization, the
            user will be redirected to this URI (hosted by your app) including query parameters that could
            be parsed by :meth:`parse_authorization_response` as a previous step to get the *access token*.
            If this parameter is not provided, the Authorization Server will show an *authorization code* that
            the user must provide to your app to continue with the process of getting the *access token*.
        :param state: (optional) if provided, the Authorization Server will include it in the *redirect uri*
            and will be returned by :meth:`parse_authorization_response`. It may be used to correlate
            authorization requests with their responses.
        :returns: The authorization URI.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> uri = bluevia_client.get_authorization_uri([bluevia.SMS_MT, bluevia.MMS_MT],
            ...                                            'https://mydomain.com/authorization_response',
            ...                                            '3829167f-7f5e-42b7-944d-469f9662e738')
            >>> print uri
            https://id.tu.com/authorize?scope=sms.send+mms.send&state=3829167f-7f5e-42b7-944d-469f9662e738&redirect_uri=https%3A%2F%2Fmydomain.com%2Fauthorization_response&response_type=code&client_id=634dca1685cd2d1c8c5f2577d7595c2f

        .. seealso:: OAuth 2.0 specification: `Authorization Request <http://tools.ietf.org/html/rfc6749#section-4.1.1>`_.

        """

        if isinstance(scope, str):
            scope = [scope]
        scope = ' '.join(scope)

#        if redirect_uri and not state:
#            state = str(uuid.uuid4())

        params = {'client_id': self.client_id,
                  'scope': scope,
                  'response_type': 'code'}

        if redirect_uri:
            self.oauth_redirect_uri = redirect_uri
            params['redirect_uri'] = redirect_uri
        if state:
            self.oauth_state = state
            params['state'] = state

        uri = self.auth_base_url + 'authorize?' + urllib.urlencode(params)
        log.info('Authorization URI: ' + uri)

        return uri

    @staticmethod
    def parse_authorization_response(uri, state_to_check=None):

        """Parse the OAuth authorization response and returns the *Authorization Code* and *State*.

        If a *redirect uri* parameter was provided to :meth:`get_authorization_uri`, the Authorization Server
        redirect the user to that URI including the result of the authorization process as query parameters.
        This method will parse that URI and returns the *authorization code* needed to get the access token and
        the *state* provided to :meth:`get_authorization_uri`,
        if any.

        :param uri: the URI where the Authorization Server redirected the user after the authorization process.
        :param state_to_check: (optional) if provided, this value will be checked against the value included in
            the parsed URI, if any. If they don't match a :exc:`AuthResponseError` exception will be raised.
        :returns: The *authorization code* to be used to call :meth:`get_access_token`, or a tuple containing the
            *authorization code* and the *state* if it was included in the parsed URI.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> uri = 'https://mydomain.com/authorization_response?code=TANf0C&state=3829167f-7f5e-42b7-944d-469f9662e738'
            >>> auth_code, state = bluevia_client.parse_authorization_response(uri)
            >>> print auth_code
            TANf0C

        .. seealso:: OAuth 2.0 specification: `Authorization Response <http://tools.ietf.org/html/rfc6749#section-4.1.2>`_.

        """

        url_parts = urlparse.urlparse(uri)
        query_params = urlparse.parse_qs(url_parts.query, keep_blank_values=True, strict_parsing=False)

        if 'code' in query_params:
            code = query_params['code']
            if len(code) > 1:
                raise AuthResponseError("More than one value for 'code' parameter")
            else:
                code = code[0]

            if 'state' in query_params:
                state = query_params['state']
                if len(state) > 1:
                    raise AuthResponseError("More than one value for 'state' parameter")
                else:
                    state = state[0]
            else:
                state = None

            if state_to_check and state_to_check != state:
                raise AuthResponseError("'state' does not match")

            if state:
                return code, state
            else:
                return code

        elif 'error' in query_params:
            error = query_params['error'][0]
            if 'error_description' in query_params:
                error += ' (' + query_params['error_description'][0] + ')'

            raise AuthResponseError('Authorization Server error: {0}'.format(error))

        else:
            raise AuthResponseError('Authorization Server response does not conform to OAuth 2.0')

    def get_access_token(self, authorization_code, redirect_uri=None):

        """Exchange the given *authorization code* for an *access token*.

        :param authorization_code: the *authorization code* returned by :meth:`parse_authorization_response` or
            provided to your app by other means (for those apps not providing a *redirect uri* parameter to
            :meth:`get_authorization_uri`).
        :param redirect_uri: (optional) if provided, it must be the same passed to :meth:`get_authorization_uri`.
            If not provided pyBlueVia remembers the one passed to :meth:`get_authorization_uri`, if any.
        :returns: The *access token* to be used to call BlueVia APIs, valid for the requested *scopes*. The returned
            access token is also stored in the :attr:`access_token` attribute.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> access_token = bluevia_client.get_access_token('TANf0C')
            >>> print access_token
            079b8f16c9a159c0d7e2fb0fcfe58d40

        .. seealso:: OAuth 2.0 specification: `Access Token Request <http://tools.ietf.org/html/rfc6749#section-4.1.3>`_
               and `Access Token Response <http://tools.ietf.org/html/rfc6749#section-4.1.4>`_.

        """

        redirect_uri = redirect_uri or self.oauth_redirect_uri

        url = self.base_url + self.PATHS['access_token']

        data = {'grant_type': 'authorization_code',
                'code': authorization_code}

        if redirect_uri:
            data['redirect_uri'] = redirect_uri

        resp = self._make_request(url, data, url_encoded=True, basic_auth=True)

        access_token = resp['access_token']
        self.access_token = access_token  # Calls property on BaseApi class

        return access_token

    def send_sms(self, to, message, callback_url=None):
        """Send an SMS.

        :param to: the phone number (or obfuscated identity) to where the SMS will be sent.
        :param message: the SMS text.
        :param callback_url: (optional) if included, BlueVia will send delivery status notifications to
            that URL, that could be parsed using :meth:`parse_delivery_status`.
        :returns: A unique id representing the sent SMS. It can be used to call :meth:`get_sms_delivery_status`.

        .. note:: This method needs an *access token*.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
            >>> sms_id = bluevia_client.send_sms(to='34600000000', message='Hello world!',
            ...                                  callback_url='https://mydomain.com/delivery_status')

        """
        return BaseApi.send_sms(self, from_=None, to=to, message=message, callback_url=callback_url)

    def get_sms_delivery_status(self, sms_id):
        """Ask for the delivery status of a sent SMS.

        :param sms_id: the SMS id returned by :meth:`send_sms`.
        :returns: A dictionary with the following keys:

            * *address*: phone number (or obfuscated identity) to which the message was sent.
            * *status*: delivery status.

        .. note:: This method needs an *access token*.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
            >>> sms_id = bluevia_client.send_sms(to='34600000000', message='Hello world!')
            >>> delivery_status = bluevia_client.get_sms_delivery_status(sms_id)
            >>> print delivery_status
            {u'status': u'delivered', u'address': u'34600000000'}

        """
        return BaseApi.get_sms_delivery_status(self, sms_id=sms_id)

    def get_incoming_sms(self):
        """Get the list of incoming SMS that have not been retrieved yet.

        Incoming SMS are those sent to a BlueVia short number using your app's keyword as the first word
        in the text. Once those SMS has been retrieved they are deleted from the server.

        :returns: A list of dictionaries (one per SMS) with the following keys:

            * *id*: SMS id.
            * *from*: phone number (or obfuscated identity) from which the SMS was sent.
            * *obfuscated*: a ``bool`` indicating whether the ``from`` is obfuscated or not.
            * *to*: short number to which the SMS was sent.
            * *message*: SMS text, including the keyword.
            * *timestamp*: date and time of when the SMS was sent.

        If there are no incoming SMS to be returned, this method returns an empty list.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> sms_list = bluevia_client.get_incoming_sms()
            >>> print sms_list
            [{u'obfuscated': False, u'from': u'34600000000', u'timestamp': datetime.datetime(2012, 12, 27, 16, 17, 42, 418000), u'to': u'34217040', u'message': u'keyword First SMS', u'id': u'97286813874922402286'},
            {u'obfuscated': False, u'from': u'34600000000', u'timestamp': datetime.datetime(2012, 12, 27, 16, 18, 26, 845000), u'to': u'34217040', u'message': u'keyword Second SMS', u'id': u'87728496828692402123'}]

        """
        return BaseApi.get_incoming_sms(self)

    def send_mms(self, to, subject, attachments, callback_url=None):
        """Send a MMS.

        :param to: the phone number (or obfuscated identity) to where the MMS will be sent.
        :param subject: the MMS subject.
        :param attachments: a list of attachments to be sent inside the MMS. Each attachment can be:

            * A string, if the attachment is textual content.
            * A file-like object.
            * A tuple with two elements:

              * A string with the attachment's *content type*.
              * The attachment's binary content.

        :param callback_url: (optional) if included, BlueVia will send delivery status notifications to
            that URL, that could be parsed using :meth:`parse_delivery_status`.
        :returns: A unique id representing the sent MMS. It can be used to call :meth:`get_mms_delivery_status`.

        .. note:: This method needs an *access token*.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
            >>> mms_id = bluevia_client.send_mms(to='34600000000', subject='Hello world!',
            ...                                  callback_url='https://mydomain.com/delivery_status',
            ...                                  attachments=('Look at this pictures',
            ...                                               open('picture.gif', 'rb'),
            ...                                               ('image/gif', 'GIF89a[...]')))

        """
        return BaseApi.send_mms(self, from_=None, to=to, subject=subject,
                                attachments=attachments, callback_url=callback_url)

    def get_mms_delivery_status(self, mms_id):
        """Ask for the delivery status of a sent MMS.

        :param mms_id: the MMS id returned by :meth:`send_mms`.
        :returns: A dictionary with the following keys:

            * *address*: phone number (or obfuscated identity) to which the message was sent.
            * *status*: delivery status.

        .. note:: This method needs an *access token*.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
            >>> mms_id = bluevia_client.send_mms(to='34600000000', subject='Hello world!',
            ...                                  callback_url='https://mydomain.com/delivery_status',
            ...                                  attachments=('Look at this pictures',
            ...                                               open('picture.gif', 'rb'),
            ...                                               ('image/gif', 'GIF89a[...]')))
            >>> delivery_status = bluevia_client.get_mms_delivery_status(mms_id)
            >>> print delivery_status
            {u'status': u'delivered', u'address': u'34600000000'}

        """
        return BaseApi.get_mms_delivery_status(self, mms_id=mms_id)

    def get_incoming_mms(self):
        """Get the list of incoming MMS that have not been retrieved yet.

        Incoming MMS are those sent to a BlueVia short number using your app's keyword as the first word
        in the subject (or in the first text attachment). Once those MMS has been retrieved they are deleted
        from the server.

        :returns: A list of MMS id. The actual content of each MMS must be retrieved with
            :meth:`get_incoming_mms_details`.

        If there are no incoming MMS to be returned, this method returns an empty list.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> mms_list = bluevia_client.get_incoming_mms()
            >>> print mms_list
            [u'97286813874922402286',u'87728496828692402123']

        """
        return BaseApi.get_incoming_mms(self)

    def get_incoming_mms_details(self, mms_id):
        """Get the content (metadata and attachment) of an incoming MMS.

        :param mms_id: the MMS id returned by :meth:`get_incoming_mms`.
        :returns: A dictionary with the following keys:

            * *id*: MMS id.
            * *from*: phone number (or obfuscated identity) from which the MMS was sent.
            * *obfuscated*: a ``bool`` indicating whether the ``from`` is obfuscated or not.
            * *to*: short number to which the MMS was sent.
            * *subject*: MMS subject, including the keyword.
            * *timestamp*: date and time of when the MMS was sent.
            * *attachments*: an array of tuples (one per attachment) containing:

              * the attachment's *content type*.
              * the attachment's binary content.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> mms_list = bluevia_client.get_incoming_mms()
            >>> mms = bluevia_client.get_incoming_mms_details(mms_list[0])
            >>> print mms
            {u'obfuscated': False, u'from': u'34600000000', u'attachments': [('text/plain', 'Look at this picture'), ('image/gif', 'GIF89a[...]')], u'timestamp': datetime.datetime(2012, 12, 28, 10, 39, 5, 242000), u'to': u'34217040', u'id': u'2515357468066729', u'subject': u'keyword Photo'}

        """
        return BaseApi.get_incoming_mms_details(self, mms_id=mms_id)
