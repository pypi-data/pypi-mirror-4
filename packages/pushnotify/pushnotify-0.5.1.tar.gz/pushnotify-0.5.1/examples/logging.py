#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Jeffrey Goettsch and other contributors.
#
# This file is part of py-pushnotify.
#
# py-pushnotify is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# py-pushnotify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with py-pushnotify.  If not, see <http://www.gnu.org/licenses/>.

"""A simple example of how to make use of logging.

For more information about logging in Python,
see: http://docs.python.org/library/logging.html

"""

import logging
import pushnotify
from pushnotify import get_client


def main():
    """The output should be something like:

    pushnotify.nma.Client-DEBUG: _post sending data: \
        application=pushnotify+examples&apikey=0123456789012345678901234\
        56789012345678901234567&event=logging+example&description=\
        testing+the+logging+capabilities+of+the+pushnotify+package
    pushnotify.nma.Client-DEBUG: _post sending to url: \
        https://www.notifymyandroid.com/publicapi/notify
    pushnotify.nma.Client-INFO: _post received response: \
        <?xml version="1.0" encoding="UTF-8"?><nma><error code="401" >\
        None of the API keys provided were valid.</error></nma>

    """

    logger = logging.getLogger('pushnotify')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s-%(levelname)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # an obviously invalid API Key

    apikey = '012345678901234567890123456789012345678901234567'

    client = get_client('nma', application='pushnotify examples')
    client.add_key(apikey)

    event = 'logging example'
    desc = 'testing the logging capabilities of the pushnotify package'

    # this will raise an exception because the API Key is invalid

    try:
        client.notify(desc, event, split=True)
    except pushnotify.exceptions.ApiKeyError:
        pass


if __name__ == '__main__':
    main()
