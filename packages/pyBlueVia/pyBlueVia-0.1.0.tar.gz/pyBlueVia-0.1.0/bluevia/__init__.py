# -*- coding: utf-8 -*-

#                  ____  _         __      ___
#                 |  _ \| |        \ \    / (_)
#      _ __  _   _| |_) | |_   _  __\ \  / / _  __ _
#     | '_ \| | | |  _ <| | | | |/ _ \ \/ / | |/ _` |
#     | |_) | |_| | |_) | | |_| |  __/\  /  | | (_| |
#     | .__/ \__, |____/|_|\__,_|\___| \/   |_|\__,_|
#     | |     __/ |
#     |_|    |___/
#


"""
pyBlueVia: A Python wrapper around the BlueVia API.

pyBlueVia implements an Api class which wraps the BlueVia APIs. It offers methods for:

* Managing OAuth 2.0 authorization process for APIs which need an *access token*.
* Sending SMS and MMS.
* Asking for the delivery status of sent SMS/MMS.
* Retrieve SMS/MMS sent to your app.
* Parsing notifications (delivery status and incoming SMS/MMS) coming from BlueVia.

More info about BlueVia APIs at http://bluevia.com

:copyright: (c) 2013 Telefonica Investigación y Desarrollo, S.A.U.
:license: Apache 2.0, see LICENSE for more details.

"""

__title__ = u'pyBlueVia'
__version__ = u'0.1.0'
__author__ = u'Jose Antonio Rodríguez'
__email__ = u'jarf@tid.es'
__license__ = u'Apache 2.0'
__copyright__ = u'2013 Telefonica Investigación y Desarrollo, S.A.U'


from .api import Api
from .api import SMS_MT, MMS_MT
from .exceptions import *

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


def add_stderr_logger(level=logging.DEBUG):
    """Helper for quickly adding a StreamHandler to the logger. Useful for debugging.

    Returns the handler after adding it.

    """
    # This method needs to be in this __init__.py to get the __name__ correct
    # even if pyBlueVia is vendored within another package.
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug('Added an stderr logging handler to logger: {0}'.format(__name__))
    return handler
