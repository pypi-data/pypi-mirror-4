jmbo-everlytic
==============

jmbo-everlytic provides integration with the everlytic (pMailer) API.
The only functionality supported is adding and removing members from a
mailing list subscription.

The communication protocol with the everlytic service is xmlrpc.

Requirements
------------

System libraries
****************
- libxml2-dev

Python packages
***************
- xmlrpclib

Usage
-----

`everlytic.api` contains functions for subscribing and unsubscribing to a
mailing list. A local everlytic profile is stored to keep track of the
member id on everlytic.

Settings
********
The following settings must be added to settings.py:
::
    EVERLYTIC = {
        'URL': 'http://your-host.pmailer.net/api/1.0'
        'USERNAME': 'xxxxx',
        'PASSWORD': 'xxxxx',
        'API_KEY': 'your_api_key',
        'LIST_ID': 0    # set to a valid integer
    }
::

