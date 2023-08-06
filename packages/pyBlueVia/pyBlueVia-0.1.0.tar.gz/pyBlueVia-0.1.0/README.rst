pyBlueVia: A Python wrapper around the BlueVia API
==================================================

---------------------------------------------

**pyBlueVia** is an Apache2 Licensed library, written in Python, for making
easier the usage of `BlueVia <http://bluevia.com>`_ API.

**pyBlueVia** implements an ``Api`` class which wraps the BlueVia API,
offering methods for:

* Managing OAuth 2.0 authorization process for APIs which need an *access token*.
* Sending SMS and MMS.
* Asking for the delivery status of sent SMS/MMS.
* Retrieve SMS/MMS sent to your app.
* Parsing notifications (delivery status and incoming SMS/MMS) coming from BlueVia.

Installation
------------

To install **pyBlueVia**:

.. code-block:: bash

    $ pip install pyBlueVia


Examples
--------

Those are a couple of examples about how to use **pyBlueVia** to send an SMS and query
its delivery status:

.. code-block:: python

    # Create the API wrapper
    bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)

    # Send an SMS
    sms_id = bluevia_client.send_sms(to='34600000000', message='Hello world!')

    # Ask for the delivery status of the sent SMS
    delivery_status = bluevia_client.get_sms_delivery_status(sms_id)
    print 'Delivery status for the SMS sent to {0}: {1}'.format(delivery_status['address'],
                                                                delivery_status['status'])

You can see more usage examples `here <https://github.com/telefonicaid/pyBlueVia/tree/master/examples>`_.

Take a look to the whole documentation at https://pybluevia.readthedocs.org/.

