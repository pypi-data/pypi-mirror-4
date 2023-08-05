#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Module for sending push notificiations to Android and iOS devices
that have Pushover installed. See https://pushover.net/ for more
information.

copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""


import json
import logging
import time
import urllib
import urllib2

from pushnotify import exceptions


PUBLIC_API_URL = u'https://api.pushover.net/1'
VERIFY_URL = u'/'.join([PUBLIC_API_URL, u'users/validate.json'])
NOTIFY_URL = u'/'.join([PUBLIC_API_URL, u'messages.json'])


class Client(object):
    """Client for sending push notifications to Android and iOS devices
    with the Pushover application installed.

    Member Vars:
        token: A string containing a valid API token.

    """

    def __init__(self, token, users=None):
        """Initialize the Pushover client.

        Args:
            token: A string of 30 characters containing a valid API
                token.
            users: A list containing 1 or 2-item tuples, where the first
                item is a string of 30 characters containing a user
                token, and the second is an optional string of up to 25
                characters containing a device name for the given user.
                (default: None)

        """

        self.logger = logging.getLogger('{0}.{1}'.format(
            self.__module__, self.__class__.__name__))

        self._browser = urllib2.build_opener(urllib2.HTTPSHandler())
        self._last_code = None
        self._last_device = None
        self._last_errors = None
        self._last_status = None
        self._last_token = None
        self._last_user = None

        self.token = token
        self.users = [] if users is None else users

    def _parse_response(self, stream, verify=False):

        response = stream.read()
        self.logger.info('received response: {0}'.format(response))

        response = json.loads(response)

        self._last_code = stream.code
        if 'device' in response.keys():
            self._last_device = response['device']
        else:
            self._last_device = None
        if 'errors' in response.keys():
            self._last_errors = response['errors']
        else:
            self._last_errors = None
        if 'status' in response.keys():
            self._last_status = response['status']
        else:
            self._last_status = None
        if 'token' in response.keys():
            self._last_token = response['token']
        if 'user' in response.keys():
            self._last_user = response['user']
        else:
            self._last_user = None

        return self._last_status

    def _post(self, url, data):

        self.logger.debug('_post sending data: {0}'.format(data))
        self.logger.debug('_post sending to url: {0}'.format(url))

        request = urllib2.Request(url, data)
        try:
            response_stream = self._browser.open(request)
        except urllib2.HTTPError, exc:
            return exc
        else:
            return response_stream

    def _raise_exception(self):

        msg = ''
        if self._last_errors:
            messages = []
            for key, value in self._last_errors.items():
                messages.append('{0} {1}'.format(key, value[0]))
            msg = '; '.join(messages)

        if self._last_device and 'invalid' in self._last_device:
            raise exceptions.ApiKeyError('device invalid', self._last_code)

        elif self._last_token and 'invalid' in self._last_token:
            raise exceptions.ApiKeyError('token invalid', self._last_code)

        elif self._last_user and 'invalid' in self._last_user:
            raise exceptions.ApiKeyError('user invalid', self._last_code)

        elif self._last_code == 429:
            # TODO: what is actually returned when the rate limit is hit?

            msg = 'too many messages sent this month' if not msg else msg
            raise exceptions.RateLimitExceeded(msg, self._last_code)

        elif self._last_code >= 500 and self._last_code <= 599:
            raise exceptions.ServerError(msg, self._last_code)

        elif self._last_errors:
            raise exceptions.FormatError(msg, self._last_code)

        else:
            raise exceptions.UnrecognizedResponseError(msg, self._last_code)

    def notify(self, title, message, kwargs=None):
        """Send a notification to each user/device in self.users.

        As of 2012-09-18, this is not returning a 4xx status code as
        per the Pushover API docs, but instead chopping the delivered
        messages off at 512 characters.

        Args:
            title: A string of up to 100 characters containing the
                title of the message (i.e. subject or brief description)
            message: A string of up to 512 characters containing the
                notification text.
            kwargs: A dictionary with any of the following strings as
                    keys:
                priority: The integer 1, which will make the
                    notification display in red and override any set
                    quiet hours.
                url: A string of up to 500 characters containing a URL
                    to attach to the notification.
                url_title: A string of up to 50 characters containing a
                    title to give the attached URL.
                (default: None)

        Raises:
            pushnotify.exceptions.ApiKeyError
            pushnotify.exceptions.FormatError
            pushnotify.exceptions.RateLimitExceeded
            pushnotify.exceptions.ServerError
            pushnotify.exceptions.UnrecognizedResponseError

        """

        """Here we match the behavior of Notify My Android and Prowl:
        raise a single exception if and only if every notification
        fails"""

        raise_exception = False

        if not self.users:
            self.logger.warn('notify called with no users set')

        for user in self.users:
            data = {'token': self.token,
                    'user': user[0],
                    'title': title,
                    'message': message,
                    'timestamp': int(time.time())}

            if user[1]:
                data['device'] = user[1]

            if kwargs:
                data.update(kwargs)

            data = urllib.urlencode(data)

            response = self._post(NOTIFY_URL, data)
            status = self._parse_response(response)
            if not status:
                raise_exception = not status

        if raise_exception:
            self._raise_exception()

    def verify_user(self, user):
        """Verify a user token.

        Args:
            user: A string containing a valid user token.

        Returns:
            A boolean containing True if the user token is valid, and
            False if it is not.

        """

        data = {'token': self.token, 'user': user}

        data = urllib.urlencode(data)
        response_stream = self._post(VERIFY_URL, data)

        self._parse_response(response_stream, True)

        return self._last_status

    def verify_device(self, user, device):
        """Verify a device for a user.

        Args:
            user: A string containing a valid user token.
            device: A string containing a device name.

        Raises:
            pushnotify.exceptions.ApiKeyError

        Returns:
            A boolean containing True if the device is valid, and
            False if it is not.

        """

        data = {'token': self.token, 'user': user, 'device': device}

        data = urllib.urlencode(data)
        response_stream = self._post(VERIFY_URL, data)

        self._parse_response(response_stream, True)

        if self._last_user and 'invalid' in self._last_user.lower():
            self._raise_exception()

        return self._last_status


if __name__ == '__main__':
    pass
