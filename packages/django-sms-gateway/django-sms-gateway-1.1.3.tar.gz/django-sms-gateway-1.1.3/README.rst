django-sms-gateway
====================

Easily send SMS messages through a web gateway from django.

This code is quite stable, and has been in use for about 2 years, with thousands of messages sent per week, to a variety of gateways, and a number of different countries.

Installation
-------------

  * Install the package into your project's virtual environment:
  
    ``pip install django-sms-gateway``

  * Add ``sms`` to your project's ``settings.INSTALLED_APPS``.

  * Run ``./manage.py migrate`` or ``./manage.py syncdb``
  
Configuration
--------------

There are three django models: ``sms.Message``, ``sms.Gateway``, and ``sms.Reply``.

Before you are able to send any messages, you will need to configure at least one gateway. There is some sample data for some gateway providers. You can adapt one of these for your own purposes.

Usage
------

Create a message, ready to be sent::

    msg = Message.objects.create(
      recipient_number="123456789", 
      content="Test message",
      sender=user,
      billee=user
    )

Note that you must provide at least these fields. ``recipient_number`` must include the international prefix (or your gateway must be configured to add it). ``content`` should be ASCII, some gateways reject unicode. ``sender`` must be an ``auth.User``, but ``billee`` may be any object.

This does not send the message::

    >>> msg
    <Message: [Unsent] Sent to 123456789 by matt at None [1]>

To send it, you need to provide a gateway::

    msg.send(gateway)


Status/Reply Callback
----------------------

If your gateway supports it, you can have it hit your server whenever there are status updates on any message. You can use the included views, in your urlpatterns::

    urlpatterns = patterns('',
      (r'^sms/', include('sms.urls')),
    )

This would mean that you would need to enter something like::

    http://example.com/sms/status_postback/

In your gateway's settings.

The status can be updated, and a status message can be provided. This is all parsed using the content of the status update request to your server, and the status_mapping data.

The same applies for replies, if you have a 2-way gateway, but using ``/sms/reply_postback/`` instead.

Reply callback functions
~~~~~~~~~~~~~~~~~~~~~~~~~

When you send a message, you can store a ``reply_callback`` function in the object. This function will be called, with the reply object passed in as the parameter. The reply object has access to it's original message (as well as it could be matched).


Billing
--------

Since SMSs are generally billable through web gateways, there is the requirement that a billee is provided, and there is a billed flag on each message. This allows you to bill after-the-fact. If you wanted to only allow sending of messages to people with credits remaining, then you would need to validate this before attempting to send.

Since a message may be longer than one segment, there is a helper property on ``sms.Message``, ``.length``, which calculates how many segments would be required.

Future
--------
Currently, all sending happens in-process. There is a preliminary celery task, but it has not been extensively tested as yet.

