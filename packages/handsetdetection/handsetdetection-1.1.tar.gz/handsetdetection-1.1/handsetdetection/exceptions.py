"Handset Detection API Exceptions."
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

# Author: Troy Farrell <troy@entheossoft.com>
# Created: 20090806

class HandsetDetectionBaseError(Exception):
    "The base for all HandsetDetection exceptions"
    def __init__(self, status, message, data=None, *args, **kwargs):
        # In Python 2.4, Exception is a classic class, so super() doesn't work
        if hasattr(Exception, "__class__"):
            super(HandsetDetectionBaseError, self).__init__(*args, **kwargs)
        else:
            Exception.__init__(self)
        self._status = int(status)
        self._message = message

        # A property
        self._data = None
        self.data = data

    def __str__(self):
        return "<Error %d: %s>" % (self._status, self._message)

    def get_data(self):
        "Get data associated with the exception."
        return self._data

    def set_data(self, data):
        "Set data associated with the exception."
        self._data = data

    data = property(get_data, set_data)

class UnknownRequestTypeError(HandsetDetectionBaseError):
    "Raised when a request uses an unknown content-type header; status=100"

# Version 2.0 only
class CredentialsFailedError(HandsetDetectionBaseError):
    "Raised when a request uses a bad username/secret combination; status=200"

# Version 2.0 only
class UnmatchedDigestError(HandsetDetectionBaseError):
    "Raised when the digest in a request does not match; status=201"

class ApiKeyError(HandsetDetectionBaseError):
    "Raised when the ApiKey is unknown, inactive, or suspended; status=202"

class MaxQueriesError(HandsetDetectionBaseError):
    """Raised when the maximum query limit is reached or the account is
    suspended; status=203"""

class MalformedXmlError(HandsetDetectionBaseError):
    "Raised when the server cannot decipher the request XML; status=204"

class MalformedJsonError(HandsetDetectionBaseError):
    "Raised when the server cannot decipher the request JSON; status=205"

class NoDataError(HandsetDetectionBaseError):
    "Raised when no data is received by the server; status=206"

class VendorMissingError(HandsetDetectionBaseError):
    "Raised when no vendor is supplied for a model query; status=207"

# Version 1.0 only
#class ApiKeyNotFoundError(HandsetDetectionBaseError):
#    "Raised when no ApiKey is found; status=208"

# Version 2.0 only
class ApiKeyNotSetError(HandsetDetectionBaseError):
    "Raised when no ApiKey is set; status=209"

class UserAgentOrProfileMissingWarning(HandsetDetectionBaseError):
    "Raised when the User-Agent or x-wap-profile is missing; status=300"

class DeviceNotFoundError(HandsetDetectionBaseError):
    "Raised when the device is not found in the database; status=301"

class HttpError(HandsetDetectionBaseError):
    "Raised when the HTTP request returns a code other than 200"

    def __init__(self, url, code, message, headers, *args, **kwargs):
        "Initialize the Exception."
        # Use None instead of self.code here because it is an HTTP code instead
        # of an API code.
        super(HttpError, self).__init__(None, message, *args, **kwargs)
        self.url = self.filename = url
        self.code = code
        self.message = message
        self.headers = headers

    def __str__(self):
        "Return a string representation."
        return "<HttpError %d: %s>" % (self._code, self._message)

# vim:set bomb et sw=4 ts=4 tw=79:
