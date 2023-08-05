==========
pushnotify
==========

pushnotify is a package for sending push notifications. It currently
supports Android devices running Notify My Android and Pushover, and iOS
devices running Pushover and Prowl.

See

* https://www.notifymyandroid.com/
* https://pushover.net/ and
* http://www.prowlapp.com/

for more details about these applications.

Development
-----------

All development for pushnotify takes place on bitbucket:

* https://bitbucket.org/jgoettsch/py-pushnotify/

To get started you can do the following::

    $ hg clone https://bitbucket.org/jgoettsch/py-pushnotify/
    $ cd py-pushnotify
    $ pip install -r requirements_dev.txt

If you discover a bug, please create an issue ticket:

* https://bitbucket.org/jgoettsch/py-pushnotify/issues/new

To run the test suite, you will have to create three modules:

* pushnotify/tests/nmakeys.py:

    This file must contain two global variables: API_KEYS and
    DEVELOPER_KEY. API_KEYS is a list containing at least one valid API
    key as a string. DEVELOPER_KEY is a string containing a valid
    developer key.
    
* pushnotify/tests/prowlkeys.py:

    This file must contain two global variables: API_KEYS and
    PROVIDER_KEY. API_KEYS is a list containing at least one valid API
    key as a string. PROVIDER_KEY is a string containing a valid
    provider key. REG_TOKEN is a valid registration token that has
    already been validated through the retrieve_token/retrieve_apikey
    process.

* pushnotify/tests/pushoverkeys.py:

    This file must contain three global variables: TOKEN, USER, and
    DEVICE. TOKEN is a string containing a valid API token. USER is a
    string containing a valid user identifier. DEVICE is a string
    containing a valid device identifier for the given user.