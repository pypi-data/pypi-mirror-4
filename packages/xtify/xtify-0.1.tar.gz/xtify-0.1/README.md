About
=====

Python library for using the `Xtify
<http://xtify.com/>`_ web service API for mobile push notifications.

Requirements
============

Tested using Python 2.7, it will probably work on older versions. For versions
of Python 2.5 or earlier``simplejson`` will need to be installed.

Functionality
=============

As of version 0.1 only the Xtify Push API 2.0 is implemented. Mostly because it
was the only one I needed, at least for now....

Available Classes:
PushNotification, PushContent, PushAction, PushRichContent

Usage Examples
==============

    >>> import xtify
    >>> pushNotif = xtify.PushNotification(appKey='myAppKey', apiKey='myApiKey)
    >>> pushNotif.sendAll=True
    >>> pushNotif.content.subject='greetings earthling'
    >>> pushNotif.content.message='take me to your leader'
    >>> pushNotif.push()

    >>> import xtify
    >>> pushContent = xtify.PushContent(
        subject='greetings earthling', message='take me to your leader')
    >>> pushNotif = xtify.pushNotification(
        appKey='myAppKey', apiKey='myApiKey', sendall=True, content=pushContent)
    >>> pushNotif.push()
