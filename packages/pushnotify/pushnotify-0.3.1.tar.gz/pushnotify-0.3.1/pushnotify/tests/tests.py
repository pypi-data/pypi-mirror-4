#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Unit tests.

copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""


import imp
import os
import unittest

from pushnotify import exceptions
from pushnotify import nma
from pushnotify import prowl
from pushnotify import pushover

try:
    imp.find_module('nmakeys', [os.path.dirname(__file__)])
except ImportError:
    NMA_API_KEYS = []
    NMA_DEVELOPER_KEY = ''
else:
    from pushnotify.tests.nmakeys import API_KEYS as NMA_API_KEYS
    from pushnotify.tests.nmakeys import DEVELOPER_KEY as NMA_DEVELOPER_KEY
try:
    imp.find_module('prowlkeys', [os.path.dirname(__file__)])
except ImportError:
    PROWL_API_KEYS = []
    PROWL_PROVIDER_KEY = ''
    PROWL_REG_TOKEN = ''
else:
    from pushnotify.tests.prowlkeys import API_KEYS as PROWL_API_KEYS
    from pushnotify.tests.prowlkeys import PROVIDER_KEY as PROWL_PROVIDER_KEY
    from pushnotify.tests.prowlkeys import REG_TOKEN as PROWL_REG_TOKEN
try:
    imp.find_module('pushoverkeys', [os.path.dirname(__file__)])
except ImportError:
    PUSHOVER_TOKEN = ''
    PUSHOVER_USER = ''
    PUSHOVER_DEVICE = ''
else:
    from pushnotify.tests.pushoverkeys import TOKEN as PUSHOVER_TOKEN
    from pushnotify.tests.pushoverkeys import USER as PUSHOVER_USER
    from pushnotify.tests.pushoverkeys import DEVICE as PUSHOVER_DEVICE


class NMATest(unittest.TestCase):
    """Test the Notify my Android client.

    """

    def setUp(self):

        self.client = nma.Client(NMA_API_KEYS, NMA_DEVELOPER_KEY)

        self.app = 'pushnotify unit tests'
        self.event = 'unit test: test_notify'
        self.desc = 'valid notification test for pushnotify'

    def test_notify_valid(self):
        """Test notify with valid notifications.

        """

        # valid notification

        self.client.notify(self.app, self.event, self.desc)

        # valid notification, extra arguments, html

        html_desc = '<h1>{0}</h1><p>{1}<br>{2}</p>'.format(
            self.app, self.event, self.desc)
        priority = 0
        url = nma.NOTIFY_URL

        self.client.notify(self.app, self.event, html_desc,
                           kwargs={'priority': priority, 'url': url,
                                   'content-type': 'text/html'})

    def test_notify_invalid(self):
        """Test notify with invalid notifications.

        """

        # invalid API key

        char = self.client.apikeys[0][0]
        apikey = self.client.apikeys[0].replace(char, '_')
        self.client.apikeys = [apikey, ]
        self.client.developerkey = ''

        self.assertRaises(exceptions.ApiKeyError,
                          self.client.notify, self.app, self.event, self.desc)

        self.client.apikeys = NMA_API_KEYS
        self.client.developerkey = NMA_DEVELOPER_KEY

        # invalid argument lengths

        bad_app = 'a' * 257
        self.assertRaises(exceptions.FormatError,
                          self.client.notify, bad_app, self.event, self.desc)

    def test_verify_valid(self):
        """Test verify with a valid API key.

        """

        self.assertTrue(self.client.verify(self.client.apikeys[0]))

    def test_verify_invalid(self):
        """Test verify with invalid API keys.

        """

        # invalid API key of incorrect length

        apikey = u'{0}{1}'.format(self.client.apikeys[0], '1')

        self.assertFalse(self.client.verify(apikey))

        # invalid API key of correct length

        char = self.client.apikeys[0][0]
        apikey = self.client.apikeys[0].replace(char, '_')

        self.assertFalse(self.client.verify(apikey))


class ProwlTest(unittest.TestCase):
    """Test the Prowl client.

    """

    def setUp(self):

        self.client = prowl.Client(PROWL_API_KEYS, PROWL_PROVIDER_KEY)

        self.app = 'pushnotify unit tests'
        self.event = 'unit test: test_notify'
        self.desc = 'valid notification test for pushnotify'

    def test_notify_valid(self):
        """Test notify with a valid notification.

        """

        self.client.notify(self.app, self.event, self.desc,
                           kwargs={'priority': 0, 'url': 'http://google.com/'})

    def test_notify_invalid(self):
        """Test notify with invalid notifications.

        """

        # invalid API key

        char = self.client.apikeys[0][0]
        apikey = self.client.apikeys[0].replace(char, '_')
        self.client.apikeys = [apikey, ]
        self.client.developerkey = ''

        self.assertRaises(exceptions.ApiKeyError,
                          self.client.notify, self.app, self.event, self.desc)

        self.client.apikeys = NMA_API_KEYS
        self.client.developerkey = NMA_DEVELOPER_KEY

        # invalid argument lengths

        bad_app = 'a' * 257
        self.assertRaises(exceptions.FormatError,
                          self.client.notify, bad_app, self.event, self.desc)

    def test_retrieve_apikey_valid(self):
        """Test retrieve_apikey with a valid token.

        """

        apikey = self.client.retrieve_apikey(PROWL_REG_TOKEN)
        self.assertTrue(apikey)
        self.assertIs(type(apikey), str)

    def test_retrieve_apikey_invalid(self):
        """Test retrieve_apikey with an invalid token and provider key.

        """

        # invalid registration token

        self.assertRaises(exceptions.PermissionDenied,
                          self.client.retrieve_apikey, PROWL_REG_TOKEN[0:-1])

        # invalid providerkey

        self.client.providerkey = self.client.providerkey[0:-1]
        self.assertRaises(exceptions.ProviderKeyError,
                          self.client.retrieve_apikey, PROWL_REG_TOKEN)

    def test_retrieve_token_valid(self):
        """Test retrieve_token with a valid providerkey.

        """

        token = self.client.retrieve_token()
        self.assertTrue(token)
        self.assertEqual(len(token), 2)
        self.assertIs(type(token[0]), str)
        self.assertIs(type(token[1]), str)

    def test_retrieve_token_invalid(self):
        """Test retrieve_token with an invalid providerkey.

        """

        self.client.providerkey = self.client.providerkey[0:-1]
        self.assertRaises(exceptions.ProviderKeyError,
                          self.client.retrieve_token)

    def test_verify_user_valid(self):
        """Test verify_user with a valid API key.

        """

        self.assertTrue(self.client.verify_user(self.client.apikeys[0]))

    def test_verify_user_invalid(self):
        """Test verify_user with invalid API keys.

        """

        # invalid API key of incorrect length

        apikey = u'{0}{1}'.format(self.client.apikeys[0], '1')

        self.assertFalse(self.client.verify_user(apikey))

        # invalid API key of correct length

        char = self.client.apikeys[0][0]
        apikey = self.client.apikeys[0].replace(char, '_')

        self.assertFalse(self.client.verify_user(apikey))


class PushoverTest(unittest.TestCase):
    """Test the Pushover client.

    """

    def setUp(self):

        self.client = pushover.Client(PUSHOVER_TOKEN,
                                      [(PUSHOVER_USER, PUSHOVER_DEVICE)])

        self.title = 'pushnotify unit tests'
        self.message = 'valid notification test for pushnotify'

    def test_notify_valid(self):
        """Test notify with a valid notification.

        """

        self.client.notify(self.title, self.message,
                           kwargs={'priority': 1, 'url': 'http://google.com/',
                                   'url_title': 'Google'})

    def test_notify_invalid_token(self):
        """Test notify with an invalid token.

        """

        char = self.client.token[0]
        bad_token = self.client.token.replace(char, '_')
        self.client.token = bad_token

        self.assertRaises(exceptions.ApiKeyError, self.client.notify,
                          self.title, self.message)

    def test_notify_invalid_user(self):
        """Test notify with an invalid user.

        """

        char = self.client.users[0][0][0]
        bad_users = (self.client.users[0][0].replace(char, '_'),
                     PUSHOVER_DEVICE)
        self.client.users = bad_users

        self.assertRaises(exceptions.ApiKeyError, self.client.notify,
                          self.title, self.message)

    def test_notify_invalid_device(self):
        """Test notify with an invalid device.

        """

        char = self.client.users[0][1][0]
        bad_users = (PUSHOVER_USER, self.client.users[0][1].replace(char, '_'))
        self.client.users = bad_users

        self.assertRaises(exceptions.ApiKeyError, self.client.notify,
                          self.title, self.message)

    def test_notify_invalid_args(self):
        """Test notify with invalid argument lengths.

        """

        # as of 2012-09-18, this is not returning a 4xx status code as
        # per the Pushover API docs, but instead chopping the delivered
        # messages off at 512 characters

        msg = 'a' * 513

        try:
            self.client.notify(self.title, msg)
        except exceptions.FormatError:
            pass

    def test_verify_user_valid(self):
        """Test veriy_user with a valid user token.

        """

        self.assertTrue(self.client.verify_user(PUSHOVER_USER))

    def test_verify_user_invalid(self):
        """Test verify_user with an invalid user token.

        """

        self.assertFalse(self.client.verify_user('foo'))

    def test_verify_device_valid(self):
        """Test verify_device with a valid device string.

        """

        self.assertTrue(self.client.verify_device(PUSHOVER_USER,
                                                  PUSHOVER_DEVICE))

    def test_verify_device_invalid(self):
        """Test verify_device with an invalid device string.

        """

        self.assertFalse(self.client.verify_device(PUSHOVER_USER, 'foo'))

    def test_verify_device_invalid_user(self):
        """Test verify_device with an invalid user token.

        """

        self.assertRaises(exceptions.ApiKeyError, self.client.verify_device,
                          'foo', PUSHOVER_DEVICE)


if __name__ == '__main__':
    pass
