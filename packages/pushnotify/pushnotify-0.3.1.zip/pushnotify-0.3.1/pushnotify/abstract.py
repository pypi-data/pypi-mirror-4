#!/usr/bin/env python
# vim: set fileencoding=utf-8


class AbstractClient(object):
    """classdocs

    """

    def __init__(self, application):
        """Constructor

        """

    def notify(self, message, title, kwargs=None):

        raise NotImplementedError

    def verify_device(self, user, device):

        raise NotImplementedError

    def verify_user(self, user):

        raise NotImplementedError
