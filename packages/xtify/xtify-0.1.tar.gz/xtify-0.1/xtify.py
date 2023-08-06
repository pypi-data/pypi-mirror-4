# -*- coding: utf-8 -*-

"""Python module for interacting with Xtify webservice API"""

import httplib

try:
    import json
except ImportError:
    import simplejson as json  # flake8 ignores this redefinition # NOQA

__all__ = ['PushNotification', 'PushAction', 'PushRichContent', 'PushContent']

BASE_URL = 'api.xtify.com'
PUSH_URL = '/2.0/push'


class Unauthorized(Exception):
    """Raised when a 401 is returned from the server"""


class XtifyFailure(Exception):
    """Raised when an error response is returned from the server.

    args: (status, response)
    """


class PushAction(dict):
    """
    Inititalizes a Xtify push notification action class
    *indicates a required attribute

    *type - [String] Simple Notifications {URL|RICH|CUSTOM|PHONE|DEFAULT|NONE}
                     Rich Notifications {WEB|PHN|CST|DEFAULT|NONE}
    data - [String] Data value for corresponding action type
    label - [String] Text label for selected action
    """

    def __init__(self, type='DEFAULT', data=None, label=None):
        self.type = type
        self.data = data
        self.label = label

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class PushRichContent(dict):
    """
    Inititalizes a Xtify push notification rich content class

    subject - [String] Message header (Android Only)
    message - [String] Primary message content
    action - [PushAction]
    """

    def __init__(self, subject=None, message=None, action=None):
        self.subject = subject
        self.message = message
        if action is None:
            action = PushAction()
        self.action = action

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class PushContent(dict):
    """
    Inititalizes a Xtify push notification content class

    subject - [String] Message header (Android Only)
    message - [String] Primary message content
    action - [PushAction]
    rich - [PushRichContent] Nested content doc with subject/message/actions
    payload - [JSON] JSON data supplied by app. For C2DM usage only
    sound - [String] iOS sounds file to play on receipt of message
    badge - [String] ("X"),increment("+X"),deincrement("-X") iOS badge w/string
    """

    def __init__(self, subject=None, message=None, action=None, rich=None,
            payload=None, sound=None, badge=None):
        self.subject = subject
        self.message = message
        if action is None:
            action = PushAction()
        self.action = action
        if rich is None:
            rich = PushRichContent()
        self.rich = rich
        self.payload = payload
        self.sound = sound
        self.badge = badge

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class PushNotification(dict):
    """
    Inititalizes a Xtify push notification class
    *indicates a required attribute

    *apiKey - [String] API key can be generated with Xtify developer console.
    *appKey - [String] Application to target with the content
    xids - [Array] Xids corresponding to device receiving this message
    hasTags - [Array] All users with these tags will receive the message
    notTags - [Array] All users without these tags will receive this message
    sendAll - [Boolean] Send message to all users of the app
    inboxOnly - [Boolean] Inbox only indication for rich messages
    *content - [PushContent] Content of push message
    """

    def __init__(self, apiKey, appKey, xids=[], hasTags=[],
            notTags=[], sendAll=False, inboxOnly=False, content=None):
        self.apiKey = apiKey
        self.appKey = appKey
        self.xids = xids
        self.hasTags = hasTags
        self.notTags = notTags
        self.sendAll = sendAll
        self.inboxOnly = inboxOnly
        if content is None:
            content = PushContent()
        self.content = content

    def __request(self, method, body, url, content_type=None, debug=False):
        h = httplib.HTTPConnection(BASE_URL)

        if debug == True:
            h.set_debuglevel(1)

        headers = {
            'Accept': '*/*'
        }
        if content_type:
            headers['Content-Type'] = content_type

        h.request(method, url, body=body, headers=headers)
        resp = h.getresponse()

        if resp.status == 401:
            raise Unauthorized

        return resp.status, resp.read()

    def push(self, debug=False):
        """Send the PushNotification to the specified device xids and tags."""

        body = json.dumps(self)
        status, response = self.__request(
                'POST', body, PUSH_URL, 'application/json', debug)

        if not status == 202:
            raise XtifyFailure(status, response)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
