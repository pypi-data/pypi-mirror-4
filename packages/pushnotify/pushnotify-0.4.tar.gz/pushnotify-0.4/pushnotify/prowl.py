#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Module for sending push notifications to iOS devices that have
Prowl installed. See http://www.prowlapp.com/ for more
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


PUBLIC_API_URL = u'https://api.prowlapp.com/publicapi'
VERIFY_URL = u'/'.join([PUBLIC_API_URL, 'verify'])
NOTIFY_URL = u'/'.join([PUBLIC_API_URL, 'add'])
RETRIEVE_TOKEN_URL = u'/'.join([PUBLIC_API_URL, 'retrieve', 'token'])
RETRIEVE_APIKEY_URL = u'/'.join([PUBLIC_API_URL, 'retrieve', 'apikey'])


class Client(object):
    """Client for sending push notificiations to iOS devices with
    the Prowl application installed.

    Member Vars:
        apikeys: A list of strings, each containing a 40 character api
            key.
        providerkey: A string containing a 40 character provider key.

    """

    def __init__(self, apikeys=None, providerkey=None):
        """Initialize the Prowl client.

        Args:
            apikeys:  A list of strings of 40 characters each, each
                containing a valid api key.
            providerkey: A string of 40 characters containing a valid
                provider key.

        """

        self.logger = logging.getLogger('{0}.{1}'.format(
            self.__module__, self.__class__.__name__))

        self._browser = urllib2.build_opener(urllib2.HTTPSHandler())
        self._last_type = None
        self._last_code = None
        self._last_message = None
        self._last_remaining = None
        self._last_resetdate = None
        self._last_token = None
        self._last_token_url = None
        self._last_apikey = None

        self.apikeys = [] if apikeys is None else apikeys
        self.providerkey = providerkey

    def _get(self, url):

        self.logger.debug('_get requesting url: {0}'.format(url))

        request = urllib2.Request(url)
        try:
            response_stream = self._browser.open(request)
        except urllib2.HTTPError, exc:
            return exc
        else:
            return response_stream

    def _parse_response(self, response, verify=False):

        xmlresp = response.read()
        self.logger.info('received response: {0}'.format(xmlresp))

        root = ElementTree.fromstring(xmlresp)

        self._last_type = root[0].tag.lower()
        self._last_code = root[0].attrib['code']

        if self._last_type == 'success':
            self._last_message = None
            self._last_remaining = root[0].attrib['remaining']
            self._last_resetdate = root[0].attrib['resetdate']
        elif self._last_type == 'error':
            self._last_message = root[0].text
            self._last_remaining = None
            self._last_resetdate = None

            if (not verify or
                    (self._last_code != '400' and self._last_code != '401')):
                self._raise_exception()
        else:
            raise exceptions.UnrecognizedResponseError(xmlresp, -1)

        if len(root) > 1:
            if root[1].tag.lower() == 'retrieve':
                if 'token' in root[1].attrib:
                    self._last_token = root[1].attrib['token']
                    self._last_token_url = root[1].attrib['url']
                    self._last_apikey = None
                elif 'apikey' in root[1].attrib:
                    self._last_token = None
                    self.last_token_url = None
                    self._last_apikey = root[1].attrib['apikey']
                else:
                    raise exceptions.UnrecognizedResponseError(xmlresp, -1)
            else:
                raise exceptions.UnrecognizedResponseError(xmlresp, -1)

        return root

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

        if self._last_code == '400':
            raise exceptions.FormatError(self._last_message,
                                         int(self._last_code))
        elif self._last_code == '401':
            if 'provider' not in self._last_message.lower():
                raise exceptions.ApiKeyError(self._last_message,
                                             int(self._last_code))
            else:
                raise exceptions.ProviderKeyError(self._last_message,
                                                  int(self._last_code))
        elif self._last_code == '406':
            raise exceptions.RateLimitExceeded(self._last_message,
                                               int(self._last_code))
        elif self._last_code == '409':
            raise exceptions.PermissionDenied(self._last_message,
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
            event: A string of up to 1024 characters containing the
                event that is being notified (i.e. subject or brief
                description.)
            desc: A string of up to 10000 characters containing the
                notification text.
            kwargs: A dictionary with any of the following strings as
                    keys:
                priority: An integer between -2 and 2, indicating the
                    priority of the notification. -2 is the lowest, 2 is
                    the highest, and 0 is normal.
                url: A string of up to 512 characters containing a URL
                    to attach to the notification.
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

        if self.providerkey:
            data['providerkey'] = self.providerkey

        if kwargs:
            data.update(kwargs)

        data = urllib.urlencode(data)

        response = self._post(NOTIFY_URL, data)
        self._parse_response(response)

    def retrieve_apikey(self, token):
        """Get an API key for a given token.

        Once a user has approved you sending them push notifications,
        you can supply the returned token here and get an API key.

        Args:
            token: A string containing a registration token returned
                from the retrieve_token method.

        Raises:
            pushnotify.exceptions.ProviderKeyError

        Returns:
            A string containing the API key.

        """

        data = {'providerkey': self.providerkey,
                'token': token}

        querystring = urllib.urlencode(data)
        url = '?'.join([RETRIEVE_APIKEY_URL, querystring])

        response = self._get(url)
        self._parse_response(response)

        return self._last_apikey

    def retrieve_token(self):
        """Get a registration token and approval URL.

        A user follows the URL and logs in to the Prowl website to
        approve you sending them push notifications. If you've
        associated a 'Retrieve success URL' with your provider key, they
        will be redirected there.

        Raises:
            pushnotify.exceptions.ProviderKeyError

        Returns:
            A two-item tuple where the first item is a string containing
            a registration token, and the second item is a string
            containing the associated URL.
        """

        data = {'providerkey': self.providerkey}

        querystring = urllib.urlencode(data)
        url = '?'.join([RETRIEVE_TOKEN_URL, querystring])

        response = self._get(url)
        self._parse_response(response)

        return self._last_token, self._last_token_url

    def verify_user(self, apikey):
        """Verify an API key for a user.

        Args:
            apikey: A string of 40 characters containing an API key.

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

        if self.providerkey:
            data['providerkey'] = self.providerkey

        querystring = urllib.urlencode(data)
        url = '?'.join([VERIFY_URL, querystring])

        response = self._get(url)
        self._parse_response(response, True)

        return self._last_code == '200'

if __name__ == '__main__':
    pass
