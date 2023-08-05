#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Module for sending push notifications to Android devices that have
Notify My Android installed. See www.notifymyandroid.com/ for more
information.

copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""


import logging
import urllib
import urllib2
try:
    from xml.etree import cElementTree
    ElementTree = cElementTree
except ImportError:
    from xml.etree import ElementTree

from pushnotify import exceptions


PUBLIC_API_URL = u'https://www.notifymyandroid.com/publicapi'
VERIFY_URL = u'/'.join([PUBLIC_API_URL, 'verify'])
NOTIFY_URL = u'/'.join([PUBLIC_API_URL, 'notify'])


class Client(object):
    """Client for sending push notificiations to Android devices with
    the Notify My Android application installed.

    Member Vars:
        apikeys: A list of strings, each containing a 48 character api
            key.
        developerkey: A string containing a 48 character developer key.

    """

    def __init__(self, apikeys=None, developerkey=None):
        """Initialize the Notify My Android client.

        Args:
            apikeys:  A list of strings, each containing a valid api
                key.
            developerkey: A string containing a valid developer key.

        """

        self.logger = logging.getLogger('{0}.{1}'.format(
            self.__module__, self.__class__.__name__))

        self._browser = urllib2.build_opener(urllib2.HTTPSHandler())
        self._last_type = None
        self._last_code = None
        self._last_message = None
        self._last_remaining = None
        self._last_resettimer = None

        self.apikeys = [] if apikeys is None else apikeys
        self.developerkey = developerkey

    def _get(self, url):

        self.logger.debug('_get requesting url: {0}'.format(url))

        request = urllib2.Request(url)
        response_stream = self._browser.open(request)
        response = response_stream.read()

        self.logger.info('_get received response: {0}'.format(response))

        return response

    def _parse_response(self, xmlresp, verify=False):

        root = ElementTree.fromstring(xmlresp)

        self._last_type = root[0].tag.lower()
        self._last_code = root[0].attrib['code']

        if self._last_type == 'success':
            self._last_message = None
            self._last_remaining = root[0].attrib['remaining']
            self._last_resettimer = root[0].attrib['resettimer']
        elif self._last_type == 'error':
            self._last_message = root[0].text
            self._last_remaining = None
            self._last_resettimer = None

            if (not verify or
                    (self._last_code != '400' and self._last_code != '401')):
                self._raise_exception()
        else:
            raise exceptions.UnrecognizedResponseError(xmlresp, -1)

        return root

    def _post(self, url, data):

        self.logger.debug('_post sending data: {0}'.format(data))
        self.logger.debug('_post sending to url: {0}'.format(url))

        request = urllib2.Request(url, data)
        response_stream = self._browser.open(request)
        response = response_stream.read()

        self.logger.info('_post received response: {0}'.format(response))

        return response

    def _raise_exception(self):

        if self._last_code == '400':
            raise exceptions.FormatError(self._last_message,
                                         int(self._last_code))
        elif self._last_code == '401':
            raise exceptions.ApiKeyError(self._last_message,
                                         int(self._last_code))
        elif self._last_code == '402':
            raise exceptions.RateLimitExceeded(self._last_message,
                                               int(self._last_code))
        elif self._last_code == '500':
            raise exceptions.ServerError(self._last_message,
                                         int(self._last_code))
        else:
            raise exceptions.UnknownError(self._last_message,
                                          int(self._last_code))

    def notify(self, app, event, desc, kwargs=None):
        """Send a notification to each apikey in self.apikeys.

        Args:
            app: A string of up to 256 characters containing the name
                of the application sending the notification.
            event: A string of up to 1000 characters containing the
                event that is being notified (i.e. subject or brief
                description.)
            desc: A string of up to 10000 characters containing the
                notification text.
            kwargs: A dictionary with any of the following strings as
                    keys:
                priority: An integer between -2 and 2, indicating the
                    priority of the notification. -2 is the lowest, 2 is
                    the highest, and 0 is normal.
                url: A string of up to 2000 characters containing a URL
                    to attach to the notification.
                content_type: A string containing "text/html" (without
                    the quotes) that then allows some basic HTML to be
                    used while displaying the notification.
                (default: None)

        Raises:
            pushnotify.exceptions.FormatError
            pushnotify.exceptions.ApiKeyError
            pushnotify.exceptions.RateLimitExceeded
            pushnotify.exceptions.ServerError
            pushnotify.exceptions.UnknownError
            pushnotify.exceptions.UnrecognizedResponseError

        """

        data = {'apikey': ','.join(self.apikeys),
                'application': app,
                'event': event,
                'description': desc}

        if self.developerkey:
            data['developerkey'] = self.developerkey

        if kwargs:
            data.update(kwargs)

        data = urllib.urlencode(data)

        response = self._post(NOTIFY_URL, data)
        self._parse_response(response)

    def verify(self, apikey):
        """Verify an API key.

        Args:
            apikey: A string of 48 characters containing an API key.

        Raises:
            pushnotify.exceptions.RateLimitExceeded
            pushnotify.exceptions.ServerError
            pushnotify.exceptions.UnknownError
            pushnotify.exceptions.UnrecognizedResponseError

        Returns:
            A boolean containing True if the API key is valid, and False
            if it is not.

        """

        data = {'apikey': apikey}

        if self.developerkey:
            data['developerkey'] = self.developerkey

        querystring = urllib.urlencode(data)
        url = '?'.join([VERIFY_URL, querystring])

        response = self._get(url)
        self._parse_response(response, True)

        return self._last_code == '200'

if __name__ == '__main__':
    pass
