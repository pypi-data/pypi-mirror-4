#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Unit tests.

copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""


import imp
import os
import unittest

from pushnotify import abstract
from pushnotify import get_client
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


class PushnotifyTest(unittest.TestCase):

    def setUp(self):

        pass

    def test_get_client_nma(self):
        """Test get_client for type='nma'.

        """

        client = get_client('nma', NMA_DEVELOPER_KEY, 'pushnotify unit tests')
        self.assertTrue(client._type == 'nma')
        self.assertTrue(isinstance(client, nma.Client))

    def test_get_client_prowl(self):
        """Test get_client for type='prowl'.

        """

        client = get_client('prowl', PROWL_PROVIDER_KEY,
                            'pushnotify unit tests')
        self.assertTrue(client._type == 'prowl')
        self.assertTrue(isinstance(client, prowl.Client))

    def test_get_client_pushover(self):
        """Test get_client for type='pushover'.

        """

        client = get_client('pushover', PUSHOVER_TOKEN,
                            'pushnotify unit tests')
        self.assertTrue(client._type == 'pushover')
        self.assertTrue(isinstance(client, pushover.Client))


class AbstractClientTest(unittest.TestCase):
    """Test the AbstractClient class.

    """

    def setUp(self):

        self.client = abstract.AbstractClient()

    def test_add_key_apikey(self):
        """Test the add_key method with an apikey.

        """

        apikey = 'foo'
        self.assertTrue(apikey not in self.client.apikeys.keys())

        self.client.add_key(apikey)
        self.assertTrue(apikey in self.client.apikeys.keys())

    def test_add_key_device_key(self):
        """Test the add_key method with a device_key.

        """

        apikey = 'foo'
        self.client.add_key('foo')

        device_key = 'bar'
        self.assertTrue(device_key not in self.client.apikeys[apikey])

        self.client.add_key(apikey, device_key)
        self.assertTrue(device_key in self.client.apikeys[apikey])

    def test_del_key_apikey(self):

        apikey = 'foo'
        self.client.add_key(apikey)
        self.assertTrue(apikey in self.client.apikeys.keys())

        self.client.del_key(apikey)
        self.assertTrue(apikey not in self.client.apikeys.keys())

    def test_del_key_device_key(self):

        apikey = 'foo'
        device_key = 'bar'
        self.client.add_key(apikey, device_key)
        self.assertTrue(device_key in self.client.apikeys[apikey])

        self.client.del_key(apikey, device_key)
        self.assertTrue(device_key not in self.client.apikeys[apikey])


class NMATest(unittest.TestCase):
    """Test the Notify my Android client.

    """

    def setUp(self):

        self.client = get_client('nma', NMA_DEVELOPER_KEY,
                                 'pushnotify unit tests')

        for key in NMA_API_KEYS:
            self.client.add_key(key)

        self.event = 'unit test: test_notify'
        self.desc = 'valid notification test for pushnotify'

    def test_notify_valid(self):
        """Test nma.Client.notify with a valid notification.

        """

        html_desc = '<h1>{0}</h1><p>{1}<br>{2}</p>'.format(
            self.client.application, self.desc, self.event)
        priority = 0
        url = nma.NOTIFY_URL

        self.client.notify(html_desc, self.event, split=False,
                           kwargs={'priority': priority, 'url': url,
                                   'content-type': 'text/html'})

    def test_notify_valid_split(self):
        """Test nma.Client.notify with a valid notification, splitting
        up a long description.

        """

        long_desc = 'a' * 10101
        self.client.notify(long_desc, self.event, split=True)

    def test_notify_invalid_apikey(self):
        """Test nma.Client.notify with an invalid API key.

        """

        char = self.client.apikeys.keys()[0][0]
        apikey = self.client.apikeys.keys()[0].replace(char, '_')
        self.client.apikeys = {}
        self.client.add_key(apikey)
        self.client.developerkey = ''

        self.assertRaises(exceptions.ApiKeyError,
                          self.client.notify, self.desc, self.event)

    def test_notify_invalid_argument_lengths(self):
        """Test nma.Client.notify with invalid argument lengths.

        """

        long_desc = 'a' * 10001
        self.assertRaises(exceptions.FormatError,
                          self.client.notify, long_desc, self.event,
                          split=False)

    def test_verify_user_valid(self):
        """Test nma.Client.verify_user with a valid API key.

        """

        self.assertTrue(self.client.verify_user(self.client.apikeys.keys()[0]))

    def test_verify_user_invalid_apikey(self):
        """Test nma.Client.verify_user with an invalid API key.

        """

        char = self.client.apikeys.keys()[0][0]
        apikey = self.client.apikeys.keys()[0].replace(char, '_')

        self.assertFalse(self.client.verify_user(apikey))


class ProwlTest(unittest.TestCase):
    """Test the Prowl client.

    """

    def setUp(self):

        self.client = get_client('prowl', PROWL_PROVIDER_KEY,
                                 'pushnotify unit tests')

        for key in PROWL_API_KEYS:
            self.client.add_key(key)

        self.event = 'unit test: test_notify'
        self.desc = 'valid notification test for pushnotify'

    def test_notify_valid(self):
        """Test prowl.Client.notify with valid notifications.

        """

        self.client.notify(self.desc, self.event, split=False,
                           kwargs={'priority': 0, 'url': 'http://google.com/'})

    def test_notify_valid_split(self):
        """Test nma.Client.notify with a valid notification, splitting
        up a long description.

        """

        long_desc = 'a' * 10101
        self.client.notify(long_desc, self.event, split=True)

    def test_notify_invalid_apikey(self):
        """Test prowl.Client.notify with an invalid API key.

        """

        char = self.client.apikeys.keys()[0][0]
        apikey = self.client.apikeys.keys()[0].replace(char, '_')
        self.client.apikeys = {}
        self.client.add_key(apikey)
        self.client.developerkey = ''

        self.assertRaises(exceptions.ApiKeyError,
                          self.client.notify, self.desc, self.event)

    def test_notify_invalid_argument_lengths(self):
        """Test prowl.Client.notify with invalid argument lengths.

        """

        bad_desc = 'a' * 10001
        self.assertRaises(exceptions.FormatError,
                          self.client.notify, bad_desc, self.event, False)

    def test_retrieve_apikey_valid(self):
        """Test prowl.Client.retrieve_apikey with a valid token.

        """

        apikey = self.client.retrieve_apikey(PROWL_REG_TOKEN)
        self.assertTrue(apikey)
        self.assertIs(type(apikey), str)

    def test_retrieve_apikey_invalid_reg_token(self):
        """Test prowl.Client.retrieve_apikey with an invalid
        registration token.

        """

        self.assertRaises(exceptions.PermissionDenied,
                          self.client.retrieve_apikey, PROWL_REG_TOKEN[0:-1])

    def test_retrieve_apikey_invalid_developerkey(self):
        """Test prowl.Client.retrieve_apikey with an invalid developer
        key.

        """

        self.client.developerkey = self.client.developerkey[0:-1]
        self.assertRaises(exceptions.ProviderKeyError,
                          self.client.retrieve_apikey, PROWL_REG_TOKEN)

    def test_retrieve_token_valid(self):
        """Test prowl.Client.retrieve_token with a valid developer key.

        """

        token = self.client.retrieve_token()
        self.assertTrue(token)
        self.assertEqual(len(token), 2)
        self.assertIs(type(token[0]), str)
        self.assertIs(type(token[1]), str)

    def test_retrieve_token_invalid(self):
        """Test prowl.Client.retrieve_token with an invalid providerkey.

        """

        self.client.developerkey = self.client.developerkey[0:-1]
        self.assertRaises(exceptions.ProviderKeyError,
                          self.client.retrieve_token)

    def test_verify_user_valid(self):
        """Test prowl.Client.verify_user with a valid API key.

        """

        self.assertTrue(self.client.verify_user(self.client.apikeys.keys()[0]))

    def test_verify_user_invalid(self):
        """Test prowl.Client.verify_user with invalid API keys.

        """

        char = self.client.apikeys.keys()[0][0]
        apikey = self.client.apikeys.keys()[0].replace(char, '_')

        self.assertFalse(self.client.verify_user(apikey))


class PushoverTest(unittest.TestCase):
    """Test the Pushover client.

    """

    def setUp(self):

        self.client = get_client('pushover', PUSHOVER_TOKEN, '')

        for key in PUSHOVER_USER.keys():
            self.client.add_key(key, PUSHOVER_USER[key][0])

        self.event = 'pushnotify unit tests'
        self.desc = 'valid notification test for pushnotify'

    def test_notify_valid(self):
        """Test pushover.Client.notify with a valid notification.

        """

        self.client.notify(self.desc, self.event, split=False,
                           kwargs={'priority': 1, 'url': 'http://google.com/',
                                   'url_title': 'Google'})

    def test_notify_valid_split(self):
        """Test pushover.Client.notify with a valid notification,
        splitting up a long description.

        """

        long_desc = 'a' * 513
        self.client.notify(long_desc, self.event, split=True)

    def test_notify_invalid_developerkey(self):
        """Test pushover.Client.notify with an invalid developer key.

        """

        self.client.developerkey = '_' + self.client.developerkey[1:]

        self.assertRaises(exceptions.ApiKeyError, self.client.notify,
                          self.desc, self.event)

    def test_notify_invalid_apikey(self):
        """Test pushover.Client.notify with an invalid API key.

        """

        apikey = self.client.apikeys.keys()[0]
        device_key = self.client.apikeys[apikey][0]

        apikey = '_' + apikey[1:]

        self.client.apikeys = {}
        self.client.add_key(apikey, device_key)

        self.assertRaises(exceptions.ApiKeyError, self.client.notify,
                          self.desc, self.event)

    def test_notify_invalid_device_key(self):
        """Test pushover.Client.notify with an invalid device key.

        """

        apikey = self.client.apikeys.keys()[0]

        self.client.apikeys = {}
        self.client.add_key(apikey, 'foo')

        self.assertRaises(exceptions.ApiKeyError, self.client.notify,
                          self.desc, self.event)

    def test_notify_invalid_argument_lengths(self):
        """Test pushover.Client.notify with invalid argument lengths.

        """

        # as of 2012-09-18, this is not returning a 4xx status code as
        # per the Pushover API docs, but instead chopping the delivered
        # messages off at 512 characters

        desc = 'a' * 513

        try:
            self.client.notify(desc, self.event, False)
        except exceptions.FormatError:
            pass

    def test_verify_user_valid(self):
        """Test pushover.Client.verify_user with a valid API key.

        """

        self.assertTrue(self.client.verify_user(self.client.apikeys.keys()[0]))

    def test_verify_user_invalid(self):
        """Test pushover.Client.verify_user with an invalid API key.

        """

        self.assertFalse(self.client.verify_user('foo'))

    def test_verify_device_valid(self):
        """Test pushover.Client.verify_device with a valid device key.

        """

        apikey = self.client.apikeys.keys()[0]
        device_key = self.client.apikeys[apikey][0]

        self.assertTrue(self.client.verify_device(apikey, device_key))

    def test_verify_device_invalid(self):
        """Test pushover.Client.verify_device with an invalid device
        key.

        """

        apikey = self.client.apikeys.keys()[0]

        self.assertFalse(self.client.verify_device(apikey, 'foo'))

    def test_verify_device_invalid_apikey(self):
        """Test pushover.Client.verify_device with an invalid API key.

        """

        apikey = self.client.apikeys.keys()[0]
        device_key = self.client.apikeys[apikey][0]

        self.assertRaises(exceptions.ApiKeyError, self.client.verify_device,
                          'foo', device_key)


if __name__ == '__main__':
    pass
