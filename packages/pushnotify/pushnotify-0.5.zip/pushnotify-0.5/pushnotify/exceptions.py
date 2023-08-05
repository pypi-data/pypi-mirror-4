#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""Module for exceptions.

copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""


class PushNotifyError(Exception):
    """Base exception for all pushnotify errors.

    Args:
        args[0]: A string containing a message.
        args[1]: An integer containing an error.

    """

    def __init__(self, *args):

        super(PushNotifyError, self).__init__()
        self.args = [arg for arg in args]


class ApiKeyError(PushNotifyError):
    """Raised when a provided API key is invalid

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """

    pass


class FormatError(PushNotifyError):
    """Raised when a request is not in the expected format.

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """

    pass


class PermissionDenied(PushNotifyError):
    """Raised when a request had not been approved.

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """

    pass


class ProviderKeyError(PushNotifyError):
    """Raised when a provided Provider key is invalid.

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """
    pass


class RateLimitExceeded(PushNotifyError):
    """Raised when too many requests are submitted in too small a time
    frame.

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """

    pass


class ServerError(PushNotifyError):
    """Raised when the notification server experiences an internal error.

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """

    pass


class UnknownError(PushNotifyError):
    """Raised when the notification server returns an unknown error.

    Args:
        args[0]: A string containing a message from the server.
        args[1]: An integer containing an error code from the server.

    """

    pass


class UnrecognizedResponseError(PushNotifyError):
    """Raised when the notification server returns an unrecognized
    response.

    Args:
        args[0]: A string containing the response from the server.
        args[1]: -1.

    """

    pass


if __name__ == '__main__':
    pass
