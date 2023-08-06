"""Handset Detection API implementation

The HandsetDetection class provides easy access to the Handset Detections HTTP
API version 2.

HandsetDetectionRequest encapsulates calls to urllib2 to make the request.
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

# Author: Troy Farrell <troy@entheossoft.com>
# Created: 20090806

# The JSON library simplejson became part of the Python Standard Library with
# Python 2.6.  If it's available, we'll use it.  Otherwise, we'll use XML.
try:
    import json
    JSON_FOUND = True
except ImportError:
    try:
        import simplejson as json
        JSON_FOUND = True
    except ImportError:
        JSON_FOUND = False

import urllib2
# If a JSON library is found, xml.sax is not used.  The test suite tests the
# XML code, so importing it is a good idea anyway.  Commment it out if you are
# using JSON and concerned about performance.
import xml.sax.handler
import xml.sax.saxutils

from handsetdetection.wsseut import WSSEUserTokenHeaderGenerator
import handsetdetection.exceptions as exceptions

class HandsetDetection(object):
    "An object for accessing the Handset Detection API v2.0"

    _baseUrl = "http://api.handsetdetection.com"
    # This API key is the key for this Python module. You should create a new
    # key if you substially modify this code.  You can set a new key with
    # set_v2_api_key.
    _apikey = "f923560d264b752bcd84c2cd0b0695e7"

    # Initialization

    def __init__(self, username=None, secret=None):
        "Initialize the api object."
        self._usertoken = None
        self._usejson = JSON_FOUND

        self.set_credentials(username, secret)

    # Public methods

    def set_credentials(self, username, secret):
        """Set the username and generate the user token.
        
        username - your registered e-mail address
        secret - the auto-generated API version 2 secret
        """
        if None not in [secret, username]:
            self._usertoken = WSSEUserTokenHeaderGenerator(username,
                                                           secret)
        else:
            self._usertoken = None

    def set_v2_apikey(self, apikey):
        """Set the API key used by the object.

        This does not modify the API key of newly constructed objects.  To do
        that, change the value on the class:

        HandsetDetection.set_class_v2_apikey(my_apikey)
        """
        self._apikey = apikey

    @classmethod
    def set_class_v2_apikey(cls, apikey):
        "Set the API key used on all new HandsetDetection instances."
        cls._apikey = apikey

    def detect(self, data, options):
        """Detect a handset with the User-Agent and/or other information.

        data - a dictionary containing a User-Agent, IP address, x-wap-profile,
               and any other information that may be useful in identifying the
               handset
        options - a string or list of options to be returned from your query,
                  e.g., "geoip,product_info,display" or ["geoip",
                  "product_info"], etc.
        """
        self._check_usertoken()
        assert isinstance(data, dict)

        if isinstance(options, list):
            options = ",".join(options)
        data["options"] = options
        result = self._do_request("detect", data)
        deviceinformation = HandsetDetectionDeviceInformation(result)
        deviceinformation.pop("status")
        deviceinformation.pop("message")
        return deviceinformation

    def model(self, vendorname):
        "Returns a list of models for the given vendor."
        self._check_usertoken()

        data = {"vendor": vendorname}
        # Yes, that's supposed to be "models"
        result = self._do_request("models", data)
        return "model" in result and result["model"] or []

    def track(self, data):
        """Track a user's requests.
        data - a dictionary containing a User-Agent, IP address, x-wap-profile,
               and any other information that may be useful in identifying the
               handset
        """
        self._check_usertoken()

        self._do_request("track", data)
        # There's nothing to return when this works.
        return None

    def vendor(self):
        "Returns a list of vendors."
        self._check_usertoken()

        data = {}
        # Yes, that's supposed to be "vendors"
        result = self._do_request("vendors", data)
        return "vendor" in result and result["vendor"] or []

    # Private methods

    def _build_headers(self):
        "Send the request to Handset Detection."
        # Headers
        # Authorization headers
        headers = self._usertoken.next()
        # ApiKey header
        headers["ApiKey"] = self._apikey
        # Content-type header
        contenttype = self._usejson and "application/json" or "text/xml"
        headers["Content-type"] = contenttype
        return headers

    def _build_url(self, method):
        "Build the url for a request."
        # Yes, models and vendors are supposed to be plural...
        assert method in ["detect", "models", "track", "vendors"]

        import urlparse

        parts = {}
        parts["method"] = method
        parts["suffix"] = self._usejson and "json" or "xml"
        urlpath = "/devices/%(method)s.%(suffix)s" % parts
        url = urlparse.urljoin(self._baseUrl, urlpath)
        return url

    @staticmethod
    def _check_status(data):
        "Raise the appropriate error if status != '0'."
        status = int(data["status"])
        if 0 != status:
            exception = {
                    100: exceptions.UnknownRequestTypeError,
                    200: exceptions.CredentialsFailedError,
                    201: exceptions.UnmatchedDigestError,
                    202: exceptions.ApiKeyError,
                    203: exceptions.MaxQueriesError,
                    204: exceptions.MalformedXmlError,
                    205: exceptions.MalformedJsonError,
                    206: exceptions.NoDataError,
                    207: exceptions.VendorMissingError,
                    # This doesn't support version 1.0.
                    #208: exceptions.ApiKeyNotFoundError,
                    209: exceptions.ApiKeyNotSetError,
                    300: exceptions.UserAgentOrProfileMissingWarning,
                    301: exceptions.DeviceNotFoundError,
                }.get(status, ValueError)
            raise exception(status, data["message"], data)
        else:
            return None

    def _check_usertoken(self):
        "Raise a ValueError if the module is not initialized before use."
        if not isinstance(self._usertoken, WSSEUserTokenHeaderGenerator):
            raise ValueError("Call set_credentials() before calling API "
                             "functions.")

    def _do_request(self, method, data):
        "Send the request to Handset Detection."
        headers = self._build_headers()
        url = self._build_url(method)
        postdata = self._serialize_data(data)

        request = HandsetDetectionRequest(url, postdata, headers)
        response = request.send()
        if response.code == 200:
            data = self._parse_data(method, response)
            self._check_status(data)
            return data
        else:
            assert False, ("response.code != 200 - urllib2 should have thrown "
                           "an exception.")

    def _parse_data(self, method, response):
        "Convert the server's response into something meaningful."
        if self._usejson:
            result = self._parse_json(response)
        else:
            result = self._parse_xml(method, response)
        return result

    @staticmethod
    def _parse_json(response):
        "Convert JSON into meaningful data."
        result = json.load(response)
        return result

    def _parse_xml(self, method, response):
        "Convert XML into meaningful data."

        class _ModelVendorHandler(xml.sax.handler.ContentHandler):
            "A content handler for HD API's XML."
            ignoretags = ["reply"]
            sequencetags = ["model", "vendor"]

            def __init__(self):
                "Initialize the ModelVendorHandler."
                xml.sax.handler.ContentHandler.__init__(self)
                self.newelement = False
                self.currentelement = None
                self.result = {}

            def startElement(self, name, attrs):
                "Entering an element"
                self.currentelement = name
                if (name not in self.ignoretags and
                    name in self.sequencetags):
                    self.newelement = True
                    if name not in self.result:
                        self.result[name] = []

            def characters(self, data):
                "Encountered character data"
                # Ignore cases where data == "\n"
                if self.currentelement not in self.ignoretags and data.strip():
                    if self.currentelement in self.sequencetags:
                        if self.newelement:
                            self.result[self.currentelement].append(data)
                        else:
                            sequence = self.result[self.currentelement]
                            if len(sequence) > 0:
                                oldstring = sequence[-1]
                                sequence[-1] = u"".join([oldstring, data])
                            else:
                                self.result[self.currentelement].append(data)
                        self.newelement = False   
                    else:
                        self.result[self.currentelement] = data

        class _DetectTrackHandler(xml.sax.handler.ContentHandler):
            "A content handler for HD API's XML."
            ignoretags = ["reply"]
            grouptags = ["product_info",
                         "wml_ui",
                         "chtml_ui",
                         "xhtml_ui",
                         "ajax",
                         "markup",
                         "cache",
                         "display",
                         "image_format",
                         "bugs",
                         "wta",
                         "security",
                         "bearer",
                         "storage",
                         "object_download",
                         "drm",
                         "streaming",
                         "wap_push",
                         "mms",
                         "sms",
                         "j2me",
                         "sound_format",
                         "flash_lite",
                         "geoip"
                        ]

            def __init__(self):
                "Initialize the DetectTrackHandler."
                xml.sax.handler.ContentHandler.__init__(self)
                self.currentelement = None
                self.elementlist = []
                self.result = {}

            def startElement(self, name, attrs):
                "Entering an element"
                self.elementlist.append(name)
                if (name not in self.ignoretags and
                    name not in self.result and
                    name in self.grouptags):
                    self.result[name] = {}

            def endElement(self, name):
                "Leaving an element"
                self.elementlist.pop()

            def characters(self, data):
                "Encountered character data"
                name = self.elementlist and self.elementlist[-1] or None
                parent = (len(self.elementlist) > 1 and self.elementlist[-2]
                                                    or None)
                # Ignore cases where data == "\n"
                if name not in self.ignoretags and data.strip():
                    if parent in self.grouptags:
                        groupdictionary = self.result[parent]
                        groupdictionary[name] = data
                    else:
                        self.result[name] = data

        # Now, parse the data
        parser = xml.sax.make_parser()
        if method in ["models", "vendors"]:
            contenthandler = _ModelVendorHandler()
        elif method in ["detect", "track"]:
            contenthandler = _DetectTrackHandler()
        else:
            raise ValueError("No handler for a %r method." % method)
        parser.setContentHandler(contenthandler)
        parser.parse(response)
        return contenthandler.result

    def _serialize_data(self, data):
        "Convert the data structure into something that can be posted."
        if self._usejson:
            result = self._serialize_json(data)
        else:
            result = self._serialize_xml(data)
        return result

    @staticmethod
    def _serialize_json(data):
        "Convert data into meaningful JSON."
        return json.dumps(data)

    @staticmethod
    def _serialize_xml(data):
        "Convert data into meaningful XML."
        # There is no document sent for empty data
        if not data:
            return ""

        import StringIO

        resultio = StringIO.StringIO()
        xmlgenerator = xml.sax.saxutils.XMLGenerator(resultio, "UTF-8")
        xmlgenerator.startDocument()
        # Start request element
        xmlgenerator.startElement(u"request", {})
        # Fill in all the data
        for key, value in data.items():
            xmlgenerator.startElement(key, {})
            valuetext = xml.sax.saxutils.escape(value)
            xmlgenerator.characters(valuetext)
            xmlgenerator.endElement(key)
        # End request element
        xmlgenerator.endElement(u"request")
        xmlgenerator.endDocument()
        return resultio.getvalue()

class HandsetDetectionRequest(object):
    "An HTTP request for Handset Detection"

    def __init__(self, url, data, headers):
        self._url = url
        self._data = data
        self._headers = headers
        self._request = urllib2.Request(url, data, headers)

    def send(self):
        "Send the request"
        try:
            response = urllib2.urlopen(self._request)
            return response
        except urllib2.HTTPError, err:
            raise exceptions.HttpError(err.filename,
                                       err.code,
                                       err.msg,
                                       err.hdrs)

class HandsetDetectionDeviceInformation(dict):
    "Detected device information"

    def get_click_to_call(self):
        "Get the click-to-call string."
        if ("xhtml_ui" in self and
            "xhtml_make_phone_call_string" in self["xhtml_ui"]):
            callstring = self["xhtml_ui"]["xhtml_make_phone_call_string"]
            return u"none" != callstring and callstring or None
        return None

    def get_send_sms(self):
        "Get the send-SMS string."
        if ("xhtml_ui" in self and
            "xhtml_send_sms_string" in self["xhtml_ui"]):
            smsstring = self["xhtml_ui"]["xhtml_send_sms_string"]
            return u"none" != smsstring and smsstring or None
        return None

# vim:set bomb et sw=4 ts=4 tw=79:
