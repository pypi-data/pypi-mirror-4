"""copyright: Copyright (c) Jeffrey Goettsch and other contributors.
license: BSD, see LICENSE for details.

"""

import logging

import nma
import prowl
import pushover


logger = logging.getLogger(__package__)


def get_client(type_, developerkey='', application=''):
    """Get a pushnotify client of the specified type.

    Args:
        type_: A string containing the type of client to get. Valid
            types are 'nma,' 'prowl,', and 'pushover,' for Notify My
            Android, Prowl, and Pushover clients, respectively.
        developerkey: A string containing a valid developer key for the
            given type_ of client.
        application: A string containing the name of the application on
            behalf of whom the client will be sending messages.

    Returns:
        An nma.Client, prowl.Client, or pushover.Client.

    """

    type_ = type_.lower()

    if type_ == 'nma':
        return nma.Client(developerkey, application)
    elif type_ == 'prowl':
        return prowl.Client(developerkey, application)
    elif type_ == 'pushover':
        return pushover.Client(developerkey, application)


if __name__ == '__main__':
    pass
