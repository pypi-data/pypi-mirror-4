# -*- coding: utf-8 -*-

"""
bluevia.utils
~~~~~~~~~~~~~

This module contains a set of classes and functions internally used by pyBlueVia.

"""

import logging
import json
import re
#import os.path
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
import email
import mimetypes

from requests.auth import AuthBase

from .exceptions import ContentTypeError


log = logging.getLogger(__name__)


class OAuth2(AuthBase):

    """This is a very very simple implementation of OAuth2 to attach an
    OAuth2 bearer token Authorization header to the given Request object.

    """

    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.access_token
        return r


def build_mms_body(metadata, attachments):

    """Build a MMS body based on metadata and attachments.

    MMS body is built as a multipart/mixed body whose first part is the metadata's JSON representation
    and the other parts are the attachments.

    """

    body = MIMEMultipart(_subtype='mixed')

    # Add MMS metadata (root fields) as a json part
    part = MIMENonMultipart(_maintype='application', _subtype='json')
    part.add_header('Content-Transfer-Encoding', '8bit')
    part.set_payload(payload=json.dumps(metadata, ensure_ascii=False))
    del(part['MIME-Version'])
    body.attach(part)

    for attachment in attachments:
        # Textual attachments
        if isinstance(attachment, basestring):
            part = MIMENonMultipart(_maintype='text', _subtype='plain')
            part.add_header('Content-Transfer-Encoding', '8bit')
            part.set_payload(payload=attachment, charset='utf-8')
            del(part['MIME-Version'])
            body.attach(part)

        # Binary attachments (image, audio or video)
        elif isinstance(attachment, (file, tuple, list)):
            if isinstance(attachment, file):
                mimetype = mimetypes.guess_type(attachment.name, strict=False)[0]
                payload = attachment.read()
            else:
                mimetype = attachment[0]
                payload = attachment[1]
            if not mimetype or not '/' in mimetype:
                error_str = "Invalid Content-Type '{0}' in attachment #{1}"
                raise ContentTypeError(error_str.format(mimetype, attachments.index(attachment)))
            maintype, subtype = mimetype.split('/')
            if not maintype in ('image', 'audio', 'video'):
                error_str = ("Unsupported Content-Type '{0}' in attachment #{1} "
                             "(only image, audio or video are supported)")
                raise ContentTypeError(error_str.format(mimetype, attachments.index(attachment)))
            part = MIMENonMultipart(_maintype=maintype, _subtype=subtype)
            part.add_header('Content-Transfer-Encoding', 'binary')
            part.add_header('Content-Disposition', 'attachment')  # , filename=os.path.basename(attachment.name))
            part.set_payload(payload=payload)
            del(part['MIME-Version'])
            body.attach(part)

    return body


def parse_mms_body(content_type, body):

    """Parse a MMS body passed as a multipart/mixed body and returns metadata and attachments.  """

    mime_header = 'Content-Type: ' + content_type + '\n'\
                  'MIME-Version: 1.0\n\n'
    body = email.message_from_string(mime_header + body)

    if not body.is_multipart():
        raise ContentTypeError('Non-multipart body')

    parts = body.get_payload()

    # First part MUST convey MMS metadata (root fields)
    metadata = parts[0]
    content_type = metadata.get_content_type().lower()
    metadata = metadata.get_payload(decode=True)
    if content_type == 'application/json':
        try:
            metadata = json.loads(metadata)
        except ValueError:
            raise ValueError('Bad JSON content in MMS metadata')
    elif content_type == 'application/xml':
        try:
            metadata = xml_to_dict(metadata, ('id', 'from', 'to', 'subject', 'timestamp'))
        except KeyError:
            raise ValueError('Bad XML content in MMS metadata')
    else:
        raise ContentTypeError("Unsupported Content-Type '{0}' in MMS metadata "
                               "(only application/json and application/xml are supported".format(content_type))

    # Go through the rest of parts, which are the MMS attachments
    attachments = [(part.get_content_type(),
                    part.get_payload(decode=True)) for part in parts[1:]]

    return metadata, attachments


def xml_to_dict(xml, keys):

    """Parse an XML document and returns a dictionary containing the specified keys.

    This is not a generic XML to dict parser, but a simpel implementation that search a set of specific
    XML tags that become dictionary keys.

    """

    try:
        if not isinstance(xml, unicode):
            xml = unicode(xml, 'utf-8')

        dict_ = {}
        for key in keys:
            if not isinstance(key, unicode):
                key = unicode(key, 'utf-8')
            dict_[key] = re.search('<.*' + key + '>(.*)</.*' + key + '>', xml).group(1)

        return dict_
    except AttributeError:
        raise KeyError('XML does not contain the key: ' + key)


def sanitize(output):

    """Sanitize a dictionary or a list of dictionaries as follows:

       * remove 'tel:+'/'alias:' prefixes from 'to'/'from'/'address' keys' values
       * add 'obfuscated' key when 'from' key is present
       * convert 'timestamp' keys' values to datetime object

    """

    if isinstance(output, dict):
        for (k, v) in output.items():
            if k in ('from', 'to', 'address'):
                obfuscated = v.startswith('alias:')
                output[k] = v[6:] if obfuscated else v[5:]
                if k == 'from':
                    output[u'obfuscated'] = obfuscated
            elif k == 'timestamp':
                output[k] = datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f+0000')

        return output
    elif isinstance(output, list):
        return [sanitize(item) for item in output]
    else:
        return output
