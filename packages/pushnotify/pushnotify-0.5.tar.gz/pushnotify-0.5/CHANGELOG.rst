Changelog
---------

version 0.5

* **backwards-incompatible change:** each client now conforms to a
  standard interface, and can be instantiated with the get_client
  factory method

version 0.4

* each client now logs HTTP GET and POST operations

version 0.3.1

* Prowl.Client.retrieve_token and Prowl.Client.retrieve_apikey now
  raise a pushnotify.exceptions.ProviderKeyError if the specified
  Provider Key is invalid

version 0.3

* added support for Prowl: http://www.prowlapp.com/

version 0.2.1

* fixed an issue where developer keys were not being sent with Notify My
  Android verifications

version 0.2

* added support for Pushover: https://pushover.net/

version 0.1

* added support for Notify My Android: https://www.notifymyandroid.com/
