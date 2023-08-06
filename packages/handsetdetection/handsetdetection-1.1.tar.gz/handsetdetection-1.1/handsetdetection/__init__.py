"""A Python package for accessing Handset Detection's APIv2

The easiest way to use this package is to use the convenience functions:
set_v2_apikey, set_credentials, detect, model, track() and vendor().

set_v2_apikey(apikey)
    Set a new API key.  This is only necessary if you wish you use a new API
    key or have modified this package in a significant way.
set_credentials(username, secret)
    Your username is the e-mail address you used when you signed up at
    handsetdetection.com.

    The secret is the secret shown in your profile.  It's your API version
    2.0 secret - not your API version 1.0 APIKey.
detect(data, options)
    Get device information and capabilities given sufficient idenifying
    information, such as a user-agent or x-wap-profile.
model(vendor)
    Get a list of models for a given vendor.
track(data)
    Track a series of requests from a user.  Tracking requests allows you to
    get better statistics from handsetdetection.com.
vendor()
    Get a list of handset vendors.

.. note:
   Setting your user name and secret are necessary for access to the Handset
   Detection API.  A ValueError will be thrown if they are not set before
   calling the other functions.

If you need to do more complex things with the API, you can also instantiate
an object of your own for the class::

HandsetDetection(username, secret)
    Create a HandsetDetection object.  All the functions described above are
    available as methods on HandsetDetection objects.

Several exceptions may be raised by API calls.  These are documented on `the
API web page`_::

    * UnknownRequestTypeError
    * CredentialsFailedError
    * UnmatchedDigestError
    * ApiKeyError
    * MaxQueriesError
    * MalformedXmlError
    * MalformedJsonError
    * NoDataError
    * VendorMissingError
    * ApiKeyNotSetError
    * UserAgentOrProfileMissingWarning
    * DeviceNotFoundError

Each of these inherits from HandsetDetectionBaseError so the following code
should trap any of these errors::

    import handsetdetection as hd
    hd.set_credentials("me@example.com", "0000000000")
    try:
        vendor_list = hd.vendor()
    except hd.HandsetDetectionBaseError, err:
        pass # or handle the exception...
        
.. _`the API web page`: http://www.handsetdetection.com/cms/resources/api/
"""
# Copyright (c) 2009 Teleport Corp Pty Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Written by Troy Farrell <troy@entheossoft.com>
# Created: 20090806

from handsetdetection.exceptions import (
        HandsetDetectionBaseError,
        UnknownRequestTypeError,
        CredentialsFailedError,
        UnmatchedDigestError,
        ApiKeyError,
        MaxQueriesError,
        MalformedXmlError,
        MalformedJsonError,
        NoDataError,
        VendorMissingError,
        ApiKeyNotSetError,
        UserAgentOrProfileMissingWarning,
        DeviceNotFoundError,
       )

from handsetdetection.hdapiv2 import HandsetDetection

# Used in convenience functions
_APIOBJECT = None
if _APIOBJECT is None:
    _APIOBJECT      = HandsetDetection()
    # It doesn't make sense to expose set_class_v2_apikey as a convenience
    # function since these functions explicitly avoid addressing the class.
    set_credentials = _APIOBJECT.set_credentials
    set_v2_apikey   = _APIOBJECT.set_v2_apikey
    # Actual API functions...
    detect          = _APIOBJECT.detect
    model           = _APIOBJECT.model
    track           = _APIOBJECT.track
    vendor          = _APIOBJECT.vendor
# vim:set bomb et sw=4 ts=4 tw=79:
