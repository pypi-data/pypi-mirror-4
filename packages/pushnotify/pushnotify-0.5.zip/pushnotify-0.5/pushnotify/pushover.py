#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Module for sending push notificiations to Android and iOS devices
that have Pushover installed. See https://pushover.net/ for more
information.

copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""


import json
import time

from pushnotify import abstract
from pushnotify import exceptions


PUBLIC_API_URL = u'https://api.pushover.net/1'
VERIFY_URL = u'/'.join([PUBLIC_API_URL, u'users/validate.json'])
NOTIFY_URL = u'/'.join([PUBLIC_API_URL, u'messages.json'])

DESC_LIMIT = 512


class Client(abstract.AbstractClient):
    """Client for sending push notifications to Android and iOS devices
    with the Pushover application installed.

    Member Vars:
        developerkey: A string containing a valid token for the Pushover
            application.
        application: A string containing the name of the application on
            behalf of whom the Pushover client will be sending messages.
            Not used by this client.
        apikeys: A dictionary where the keys are strings containing
            valid user identifier, and the values are lists of strings,
            each containing a valid device identifier.

    """

    def __init__(self, developerkey, application=''):
        """Initialize the Pushover client.

        Args:
            developerkey: A string containing a valid token for the
                Pushover application.
            application: A string containing the name of the application
                on behalf of whom the Pushover client will be sending
                messages. Not used by this client. (default: '')

        """

        super(self.__class__, self).__init__(developerkey, application)

        self._type = 'pushover'
        self._urls = {'notify': NOTIFY_URL, 'verify': VERIFY_URL}

    def _parse_response_stream(self, stream, verify=False):

        response = stream.read()
        self.logger.info('received response: {0}'.format(response))

        response = json.loads(response)

        self._last['code'] = stream.code
        if 'device' in response.keys():
            self._last['device'] = response['device']
        else:
            self._last['device'] = None
        if 'errors' in response.keys():
            self._last['errors'] = response['errors']
        else:
            self._last['errors'] = None
        if 'status' in response.keys():
            self._last['status'] = response['status']
        else:
            self._last['status'] = None
        if 'token' in response.keys():
            self._last['token'] = response['token']
        else:
            self._last['token'] = None
        if 'user' in response.keys():
            self._last['user'] = response['user']
        else:
            self._last['user'] = None

        return self._last['status']

    def _raise_exception(self):

        msg = ''
        if self._last['errors']:
            messages = []
            for key, value in self._last['errors'].items():
                messages.append('{0} {1}'.format(key, value[0]))
            msg = '; '.join(messages)

        if self._last['device'] and 'invalid' in self._last['device']:
            raise exceptions.ApiKeyError('device invalid', self._last['code'])

        elif self._last['token'] and 'invalid' in self._last['token']:
            raise exceptions.ApiKeyError('token invalid', self._last['code'])

        elif self._last['user'] and 'invalid' in self._last['user']:
            raise exceptions.ApiKeyError('user invalid', self._last['code'])

        elif self._last['code'] == 429:
            # TODO: what is actually returned when the rate limit is hit?

            msg = 'too many messages sent this month' if not msg else msg
            raise exceptions.RateLimitExceeded(msg, self._last['code'])

        elif self._last['code'] >= 500 and self._last['code'] <= 599:
            raise exceptions.ServerError(msg, self._last['code'])

        elif self._last['errors']:
            raise exceptions.FormatError(msg, self._last['code'])

        else:
            raise exceptions.UnrecognizedResponseError(msg, self._last['code'])

    def notify(self, description, event, split=True, kwargs=None):
        """Send a notification to each user/device combintation in
        self.apikeys.

        As of 2012-09-18, this is not returning a 4xx status code as
        per the Pushover API docs, but instead chopping the delivered
        messages off at 512 characters.

        Args:
            description: A string of up to DESC_LIMIT characters
                containing the notification text.
            event: A string of up to 100 characters containing a
                subject or brief description of the event.
            split: A boolean indicating whether to split long
                descriptions among multiple notifications (True) or to
                possibly raise an exception (False). (default True)
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

        def send_notify(desc_list, event, kwargs, apikey, device_key=''):
            all_successful = True

            for description in desc_list:
                data = {'token': self.developerkey,
                        'user': apikey,
                        'title': event,
                        'message': description,
                        'timestamp': int(time.time())}

                if device_key:
                    data['device'] = device_key

                if kwargs:
                    data.update(kwargs)

                response_stream = self._post(self._urls['notify'], data)
                this_successful = self._parse_response_stream(response_stream)

                all_successful = all_successful and this_successful

            return all_successful

        if not self.apikeys:
            self.logger.warn('notify called with no users set')
            return

        desc_list = []
        if split:
            while description:
                desc_list.append(description[0:DESC_LIMIT])
                description = description[DESC_LIMIT:]
        else:
            desc_list = [description]

        # Here we match the behavior of Notify My Android and Prowl:
        # raise a single exception if and only if every notification
        # fails

        all_ok = True

        for apikey, device_keys in self.apikeys.items():
            if not device_keys:
                this_ok = send_notify(desc_list, event, kwargs,
                                                   apikey)
            else:
                for device_key in device_keys:
                    this_ok = send_notify(
                        desc_list, event, kwargs, apikey, device_key)

            all_ok = all_ok and this_ok

        if not all_ok:
            self._raise_exception()

    def verify_user(self, apikey):
        """Verify a user identifier.

        Args:
            apikey: A string containing a user identifer.

        Returns:
            A boolean containing True if apikey is valid, and
            False if it is not.

        """

        data = {'token': self.developerkey, 'user': apikey}

        response_stream = self._post(self._urls['verify'], data)

        self._parse_response_stream(response_stream, True)

        return self._last['status']

    def verify_device(self, apikey, device_key):
        """Verify a device identifier for the user given by apikey.

        Args:
            apikey: A string containing a user identifer.
            device_key: A string containing a device identifier.

        Raises:
            pushnotify.exceptions.ApiKeyError

        Returns:
            A boolean containing True if device_key is valid for
            apikey, and False if it is not.

        """

        data = {'token': self.developerkey, 'user': apikey,
                'device': device_key}

        response_stream = self._post(self._urls['verify'], data)

        self._parse_response_stream(response_stream, True)

        if self._last['user'] and 'invalid' in self._last['user'].lower():
            self._raise_exception()

        return self._last['status']


if __name__ == '__main__':
    pass
