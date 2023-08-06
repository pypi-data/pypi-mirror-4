HandsetDetection Python API kit
===============================

:Author: Troy Farrell <troy@entheossoft.com>
:Copyright: 2009, 2013 Teleport Corp Pty Ltd.
:License: see the file LICENSE

This is a Python module exposing the Handset Detection API version 2.0.  If you
aren't sure what that means, please visit http://handsetdetection.com/ and then
read this document.

API
---

The API for handsetdetection.com is quite simple.  There are four available
methods: detect, model, track, and vendor.

detect(data, options)
    Get device information and capabilities given sufficient idenifying
    information, such as a user-agent or x-wap-profile.

    data - a dictionary containing a User-Agent, IP address, x-wap-profile,
           and any other information that may be useful in identifying the
           handset
    options - a string or list of options to be returned from your query,
              e.g., "geoip,product_info,display" or ["geoip",
              "product_info"], etc.

model(vendor)
    Get a list of models for a given vendor.

track(data)
    Track a series of requests from a user.  Tracking requests allows you to
    get better statistics from handsetdetection.com.

    data - a dictionary containing a User-Agent, IP address, x-wap-profile,
           and any other information that may be useful in identifying the
           handset

vendor()
    Get a list of handset vendors.

You should also know about two methods of this API interface:

set_v2_apikey(apikey)
    Set a new API key.  This is only necessary if you wish you use a new API
    key or have modified this package in a significant way.

set_credentials(username, secret)
    Your username is the e-mail address you used when you signed up at
    handsetdetection.com.

    The secret is the secret shown in your profile.  It's your API version
    2.0 secret - not your API version 1.0 APIKey.

For convenience, these methods are exposed as functions on the handsetdetection
package.  Should you desire additional flexibility, use the methods on the
handsetdetection.HandsetDetection class.

Examples
--------

There are four examples describing the module's use in the examples directory::

detect.py
    Detect a mobile device and display the click-to-call and send-sms strings
    for the device.
detect_and_redirect.py
    Detect a mobile device and redirect it to a new URL.
model.py
    For a given mobile device vendor, display known models.
vendor.py
    Display known mobile device vendors.

Developing This Package
-----------------------

The following tools may be helpful to anyone furthering the development of this Python package::

    * docutils
    * Nose (nosetests)
    * pylint
    * setuptools

.. vim:set et sw=4 ts=4 tw=79:
