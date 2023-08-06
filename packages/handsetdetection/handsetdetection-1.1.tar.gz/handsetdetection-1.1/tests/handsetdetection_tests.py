"Tests for the Handset Detection Python API Kit."
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

import StringIO
import unittest

# The next few lines make the import work if the test is run from the tests
# directory.
import testutils
handsetdetection = testutils.importModule("handsetdetection")
import handsetdetection.exceptions as exceptions
from handsetdetection.hdapiv2 import HandsetDetectionDeviceInformation

class HandsetDetectionAuthenticationTests(unittest.TestCase):
    "Tests for handsetdetection authentication"

    def test_usertoken(self):
        "Test HandsetDetection.set_credentials()."
        # Constructor 
        hd = handsetdetection.HandsetDetection("foo", "bar")
        self.assertNotEqual(hd._usertoken, None)

        # Convenience functions
        self.assertRaises(ValueError, handsetdetection.vendor)
        self.assert_(handsetdetection._APIOBJECT._usertoken is None)
        handsetdetection.set_credentials("foo", "bar")
        self.assert_(handsetdetection._APIOBJECT._usertoken != None)

class HandsetDetectionRequestsTests(unittest.TestCase):
    "Tests for handsetdetection API calls"

    # The _request and _result values are all seriously truncated.
    detect_request = {"User-Agent": ("Amoi-A310/Plat-F-VIM/WAP2.0/MIDP1.0/"
                                     "CLDC1.0 UP.Browser/6.2.2.7.c.1.102 "
                                     "(GUI) MMP/1.0"),
                      "ipaddress": "247.135.228.143",
                      "options": ("chtml_ui,xhtml_ui,cache,image_format,"
                                  "security,bearer,storage,object_download,"
                                  "drm,mms,j2me,flash_lite"),
                      "HTTP_HOST": "192.168.1.30",
                      "HTTP_ACCEPT_LANGUAGE": "en-us,en;q=0.5",
                      "HTTP_REFERER": ("http://192.168.1.30/test.php?"
                                       "action=detect"),
                      "PATH": "/sbin:/usr/sbin:/bin:/usr/bin",
                      "SERVER_SIGNATURE": ("<address>Apache/2.2.2 (Fedora) "
                                           "Server at 192.168.1.30 Port 80"
                                           "</address>\n"),
                      "SERVER_SOFTWARE": "Apache/2.2.2 (Fedora)",
                      "SERVER_NAME": "192.168.1.30",
                      "SERVER_ADDR": "192.168.1.30"}
    detect_result = {"message":"OK",
                     "status":"0",
                     "chtml_ui":{"chtml_display_accesskey": False,
                                 "emoji": False,
                                },
                     "xhtml_ui":{"xhtml_honors_bgcolor": False,
                                 "xhtml_supports_forms_in_table": False
                                },
                     "cache":{"total_cache_disable_support": False,
                              "time_to_live_support": False
                             }
                    }
    detect_result_json = ('{"message": "OK", "status": "0", "xhtml_ui": {"xhtm'
                          'l_supports_forms_in_table": false, "xhtml_honors_bg'
                          'color": false}, "cache": {"time_to_live_support": f'
                          'alse, "total_cache_disable_support": false}, "chtml'
                          '_ui": {"chtml_display_accesskey": false, "emoji": f'
                          'alse}}')
    detect_result_xml = """<?xml version="1.0" encoding="UTF-8"?>
<reply>
<message>OK</message>
<status>0</status>
<chtml_ui>
<chtml_display_accesskey>0</chtml_display_accesskey>
<emoji>0</emoji>
</chtml_ui>
<xhtml_ui>
<xhtml_honors_bgcolor>0</xhtml_honors_bgcolor>
<xhtml_supports_forms_in_table>0</xhtml_supports_forms_in_table>
</xhtml_ui>
<cache>
<total_cache_disable_support>0</total_cache_disable_support>
<time_to_live_support>0</time_to_live_support>
</cache>
</reply>"""

    model_request = {"vendor": "Sagem"}
    model_result = {"message": "OK",
                    "status": "0",
                    "model": ["3000",
                              "3016",
                              "3XXX",
                              "910",
                              "912",
                              # ...
                              "946"
                             ]
                   }
    model_request_json = '{"vendor": "Sagem"}'
    model_request_xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<request><ve'
                         'ndor>Sagem</vendor></request>')
    model_result_json = ('{"message":"OK","status":"0","model":["3000","3016",'
                         '"3XXX","910","912","946"]}')
    model_result_xml = """<?xml version="1.0" encoding="UTF-8"?>
<reply>
<message>OK</message>
<status>0</status>
<model>3000</model>
<model>3016</model>
<model>3XXX</model>
<model>910</model>
<model>912</model>
<model>946</model>
</reply>"""


    track_request = {"User-Agent": "MOT-V51",
                     "ipaddress": "96.215.44.9",
                     "options": ("geoip,wml_ui,xhtml_ui,markup,cache,display,"
                                 "security,bearer,object_download,drm,"
                                 "streaming,mms,j2me,sms,sound_format"),
                     "HTTP_HOST": "192.168.1.30",
                     "HTTP_ACCEPT_LANGUAGE": "en-us,en;q=0.5",
                     "HTTP_REFERER": ("http://192.168.1.30/test.php?"
                                      "action=detect"),
                     "REQUEST_URI": "/test.php?action=track"
                    }
    track_result = {"message": "OK",
                    "status": "0"}
    track_result_json = '{"message":"OK","status":"0"}'
    track_result_xml = """<?xml version="1.0" encoding="UTF-8"?>
<reply>
<message>OK</message>
<status>0</status>
</reply>
"""
    vendor_request = {}
    vendor_result = {"message": "OK",
                     "status": "0",
                     "vendor": ["Access",
                                "Acer",
                                "Aiko",
                                # ...
                                "Android",
                                "AnexTek",
                                "Apple",
                                "ARCELIK"
                               ]
                    }
    vendor_request_json = '{}'
    vendor_request_xml = ""
    vendor_result_json = ('{"message":"OK","status":"0","vendor":["Access","Ac'
                          'er","Aiko","Android","AnexTek","Apple","ARCELIK"]}')
    vendor_result_xml = """<?xml version="1.0" encoding="UTF-8"?>
<reply>
<message>OK</message>
<status>0</status>
<vendor>Access</vendor>
<vendor>Acer</vendor>
<vendor>Aiko</vendor>
<vendor>Android</vendor>
<vendor>AnexTek</vendor>
<vendor>Apple</vendor>
<vendor>ARCELIK</vendor>
</reply>"""

    def setUp(self):
        "Make a handsetdetection object ready for testing."
        import types

        def fake_do_request(self, method, data):
            "Replace the do_request method of HandsetDetection."
            assert self.testresult
            self.testrequest = {"method": method,
                                "data"  : data,
                               }
            result = self.testresult
            return result

        self.hd = handsetdetection.HandsetDetection("foo", "bar")
        self.hd._do_request = types.MethodType(fake_do_request, self.hd)

    def test_vendor(self):
        "Test the vendor() API call."
        self.hd.testresult = self.vendor_result.copy()

        result = self.hd.vendor()
        request = self.hd.testrequest

        self.assertEquals(request, {"method": "vendors",
                                    "data": self.vendor_request})
        self.assert_("Android" in result)
        self.assert_("Apple" in result)

    def test_model(self):
        "Test the model() API call."
        self.hd.testresult = self.model_result.copy()

        result = self.hd.model("Sagem")
        request = self.hd.testrequest

        self.assertEquals(request, {"method": "models",
                                    "data": self.model_request})
        self.assert_("3000" in result)
        self.assert_("912" in result)

    def test_model2(self):
        "Test the model() API call again."
        self.hd.testresult = {"status": "0",
                              "message": "OK"}

        result = self.hd.model("Foo!")
        request = self.hd.testrequest

        self.assertEquals(request, {"method": "models",
                                    "data": {"vendor": "Foo!"}})
        self.assertEquals([], result)

    def test_detect(self):
        "Test the detect() API call."
        self.hd.testresult = self.detect_result.copy()

        request = self.detect_request.copy()
        request.pop("options")
        options = ["chtml_ui",
                   "xhtml_ui",
                   "cache",
                   "image_format",
                   "security",
                   "bearer",
                   "storage",
                   "object_download",
                   "drm",
                   "mms",
                   "j2me",
                   "flash_lite",
                  ]

        result = self.hd.detect(request, options)
        request = self.hd.testrequest

        self.assertEquals(request, {"method": "detect",
                                    "data": self.detect_request})
        self.assertEquals(False, result["xhtml_ui"]["xhtml_honors_bgcolor"])
        self.assertEquals(False, result["cache"]["time_to_live_support"])

    def test_detect2(self):
        "Test the detect() API call with an options string."
        self.hd.testresult = self.detect_result.copy()

        request = self.detect_request.copy()
        request.pop("options")
        options = ("chtml_ui,xhtml_ui,cache,image_format,security,bearer,"
                   "storage,object_download,drm,mms,j2me,flash_lite")

        result = self.hd.detect(request, options)
        request = self.hd.testrequest

        self.assertEquals(request, {"method": "detect",
                                    "data": self.detect_request})
        self.assertEquals(False, result["xhtml_ui"]["xhtml_honors_bgcolor"])
        self.assertEquals(False, result["cache"]["time_to_live_support"])

    def test_track(self):
        "Test the track() API call."
        self.hd.testresult = self.track_result.copy()

        result = self.hd.track(self.track_request)
        request = self.hd.testrequest

        self.assertEquals(request, {"method": "track",
                                    "data": self.track_request})
        self.assertEquals(None, result)

    def test_parse_json(self):
        "Test the JSON parsing."
        io = StringIO.StringIO(self.detect_result_json)
        result = self.hd._parse_json(io)
        self.assertEqual(result, self.detect_result)

        io = StringIO.StringIO(self.model_result_json)
        result = self.hd._parse_json(io)
        self.assertEqual(result, self.model_result)

        io = StringIO.StringIO(self.track_result_json)
        result = self.hd._parse_json(io)
        self.assertEqual(result, self.track_result)

        io = StringIO.StringIO(self.vendor_result_json)
        result = self.hd._parse_json(io)
        self.assertEqual(result, self.vendor_result)

    def test_parse_xml(self):
        "Test the XML parsing."

        # The XML parser has no knowledge of the XML schema and makes no
        # attempt to coerce the strings into other data types.  makeFalse
        # changes u'0' to False so assertEqual is happy.
        def makeFalse(data):
            "Replace u'0' with False."
            for k, v in data.items():
                if "0" == v:
                    data[k] = False

        io = StringIO.StringIO(self.detect_result_xml)
        result = self.hd._parse_xml("detect", io)
        map(makeFalse, (result["xhtml_ui"],
                        result["chtml_ui"],
                        result["cache"]))
        self.assertEqual(result, self.detect_result)

        io = StringIO.StringIO(self.model_result_xml)
        result = self.hd._parse_xml("models", io)
        self.assertEqual(result, self.model_result)

        io = StringIO.StringIO(self.track_result_xml)
        result = self.hd._parse_xml("track", io)
        self.assertEqual(result, self.track_result)

        io = StringIO.StringIO(self.vendor_result_xml)
        result = self.hd._parse_xml("vendors", io)
        self.assertEqual(result, self.vendor_result)

    def test_parse_xml_bug1(self):
        "This was a bug."
        xmldata = ('<?xml version="1.0" encoding="UTF-8" ?><reply><geoip><coun'
                   'try>United States</country><city>Austin</city><countrycode'
                   '>US</countrycode><region>TX</region><latitude>30.384</lati'
                   'tude><longitude>-97.7073</longitude><isp></isp><company></'
                   'company></geoip><message>Not Found</message><status>301</s'
                   'tatus></reply>')
        desiredresult = {u'geoip': { u'city': u'Austin',
                                    u'countrycode': u'US',
                                    u'country': u'United States',
                                    u'region': u'TX',
                                    u'longitude': u'-97.7073',
                                    u'latitude': u'30.384'},
                         u'status': u'301',
                         u'message': u'Not Found'}

        io = StringIO.StringIO(xmldata)
        result = self.hd._parse_xml("detect", io)
        self.assertEqual(result, desiredresult)

    def test_parse_xml_bug2(self):
        "This was another bug."
        xmldata = ('<?xml version="1.0" encoding="UTF-8" ?><reply><message>OK<'
                   '/message><status>0</status><vendor>Mobile &amp; Wireless G'
                   'roup</vendor></reply>')
        desiredresult = {u"message": u"OK",
                         u"status": u"0",
                         u"vendor": [u"Mobile & Wireless Group"]
                        }
        io = StringIO.StringIO(xmldata)
        result = self.hd._parse_xml("vendors", io)
        self.assertEqual(result, desiredresult)

    def test_serialize_json(self):
        "Test the JSON serialization."
# Because the order of keys in a dictionary is not easily calculated, the
# complex requests get tested differently.
        result = self.hd._serialize_json(self.detect_request)
#        self.assertEqual(result, self.detect_request_json)
        ua = ('"User-Agent": "Amoi-A310\/Plat-F-VIM\/WAP2.0\/MIDP1.0\/CLDC1.0 '
              'UP.Browser\/6.2.2.7.c.1.102 (GUI) MMP\/1.0",')
        options = ('"options": "chtml_ui,xhtml_ui,cache,image_format,security,'
                   'bearer,storage,object_download,drm,mms,j2me,flash_lite",')
        # In JSON, escaping slashes with backslashes is optional.
        # The simplejson library escapes them.  The json module in Python 2.6
        # doesn't.
        self.assert_(ua in result or ua.replace("\\", "") in result)
        self.assert_(options in result)

        result = self.hd._serialize_json(self.model_request)
        self.assertEqual(result, self.model_request_json)

        result = self.hd._serialize_json(self.track_request)
#        self.assertEqual(result, self.track_request_json)
        ua = '"User-Agent": "MOT-V51",'
        ip = '"ipaddress": "96.215.44.9",'
        options = ('"options": "geoip,wml_ui,xhtml_ui,markup,cache,display,sec'
                   'urity,bearer,object_download,drm,streaming,mms,j2me,sms,so'
                   'und_format",')
        self.assert_(ua in result)
        self.assert_(ip in result)
        self.assert_(options in result)

        result = self.hd._serialize_json(self.vendor_request)
        self.assertEqual(result, self.vendor_request_json)

    def test_serialize_xml(self):
        "Test the XML serialization."
# Because the order of keys in a dictionary is not easily calculated, the
# complex requests get tested differently.
        result = self.hd._serialize_xml(self.detect_request)
#        self.assertEqual(result, self.detect_request_xml)
        ua = ('<User-Agent>Amoi-A310/Plat-F-VIM/WAP2.0/MIDP1.0/CLDC1.0 UP.Brow'
              'ser/6.2.2.7.c.1.102 (GUI) MMP/1.0</User-Agent>')
        options = ('<options>chtml_ui,xhtml_ui,cache,image_format,security,bea'
                   'rer,storage,object_download,drm,mms,j2me,flash_lite</optio'
                   'ns>')
        self.assert_(ua in result)
        self.assert_(options in result)


        result = self.hd._serialize_xml(self.model_request)
        self.assertEqual(result, self.model_request_xml)

        result = self.hd._serialize_xml(self.track_request)
#        self.assertEqual(result, self.track_request_xml)
        ua = '<User-Agent>MOT-V51</User-Agent>'
        ip = '<ipaddress>96.215.44.9</ipaddress>'
        options = ('<options>geoip,wml_ui,xhtml_ui,markup,cache,display,securi'
                   'ty,bearer,object_download,drm,streaming,mms,j2me,sms,sound'
                   '_format</options>')
        self.assert_(ua in result)
        self.assert_(ip in result)
        self.assert_(options in result)

        result = self.hd._serialize_json(self.vendor_request)
        self.assertEqual(result, self.vendor_request_json)

        result = self.hd._serialize_xml(self.vendor_request)
        self.assertEqual(result, self.vendor_request_xml)

    def test_build_headers(self):
        "Test _build_headers."
        headers = self.hd._build_headers()
        self.assert_("ApiKey" in headers)
        self.assert_("Authorization" in headers)
        self.assert_("Content-type" in headers)
        self.assert_("X-WSSE" in headers)

        self.assert_(headers["Content-type"] in ["text/xml",
                                                 "application/json"])
        self.assert_(headers["ApiKey"] == self.hd._apikey)

    def test_build_url(self):
        "Test _build_url."
        url = self.hd._build_url("detect")
        expectedurl = "http://api.handsetdetection.com/devices/detect."
        self.assert_(url.startswith(expectedurl))
        if "json" in url:
            self.assert_(url.endswith("json"))
        elif "xml" in url:
            self.assert_(url.endswith("xml"))
        else:
            self.fail()

    def test_set_v2_apikey(self):
        "Test set_v2_apikey and set_class_v2_apikey."
        # First, change the instance
        apikey = self.hd._apikey
        foo = "foo"
        self.hd.set_v2_apikey(foo)
        builtapikey = self.hd._build_headers()["ApiKey"]
        self.assertEquals(builtapikey, foo)
        self.assertEquals(self.hd.__class__._apikey, apikey)

        # Now, change the class
        bar = "bar"
        self.hd.set_class_v2_apikey(bar)
        hd2 = handsetdetection.HandsetDetection("foo", "bar")
        builtapikey = self.hd._build_headers()["ApiKey"]
        builtapikey2 = hd2._build_headers()["ApiKey"]
        self.assertEquals(builtapikey, foo)
        self.assertEquals(builtapikey2, bar)

    def test_get_click_to_call(self):
        "Test get_click_to_call"
        data = {"xhtml_ui": {"xhtml_make_phone_call_string" : "Wahoo!"}}
        devinfo = HandsetDetectionDeviceInformation(data)
        self.assertEqual(devinfo.get_click_to_call(),
                         data["xhtml_ui"]["xhtml_make_phone_call_string"])

        data = {"xhtml_ui": {"xhtml_make_phone_call_string" : "none"}}
        devinfo = HandsetDetectionDeviceInformation(data)
        self.assertEqual(devinfo.get_click_to_call(), None)

    def test_get_send_sms(self):
        "Test get_send_sms"
        data = {"xhtml_ui": {"xhtml_send_sms_string" : "Wahoo!"}}
        devinfo = HandsetDetectionDeviceInformation(data)
        self.assertEqual(devinfo.get_send_sms(),
                         data["xhtml_ui"]["xhtml_send_sms_string"])

        data = {"xhtml_ui": {"xhtml_send_sms_string" : "none"}}
        devinfo = HandsetDetectionDeviceInformation(data)
        self.assertEqual(devinfo.get_send_sms(), None)


class HandsetDetectionExceptionTests(unittest.TestCase):
    "Tests for the handsetdetection exceptions"

    def setUp(self):
        "Make a handsetdetection object ready for testing."
        self.hd = handsetdetection.HandsetDetection("foo", "bar")

    def test_UnknownRequestTypeError(self):
        "Status == 100"
        data = {"status": "100",
                "message": "Unknown request type – please use xml or json"}
        self.assertRaises(exceptions.UnknownRequestTypeError,
                          self.hd._check_status,
                          data)

    def test_CredentialsFailedError(self):
        "Status == 200"
        data = {"status": "200",
                "message": "Bad username/secret combination."}
        self.assertRaises(exceptions.CredentialsFailedError,
                          self.hd._check_status,
                          data)

    def test_UnmatchedDigestError(self):
        "Status == 201"
        data = {"status": "201",
                "message": "Unmatched digest"}
        self.assertRaises(exceptions.UnmatchedDigestError,
                          self.hd._check_status,
                          data)

    def test_ApiKeyError(self):
        "Status == 202"
        data = {"status": "202",
                "message": "ApiKey unknown, Inactive or Suspended"}
        self.assertRaises(exceptions.ApiKeyError,
                          self.hd._check_status,
                          data)

    def test_MaxQueriesError(self):
        "Status == 203"
        data = {"status": "203",
                "message": "Maximum query limit reached or account suspended"}
        self.assertRaises(exceptions.MaxQueriesError,
                          self.hd._check_status,
                          data)

    def test_MalformedXmlError(self):
        "Status == 204"
        data = {"status": "204",
                "message": "Can not decipher your XML"}
        self.assertRaises(exceptions.MalformedXmlError,
                          self.hd._check_status,
                          data)

    def test_MalformedJsonError(self):
        "Status == 205"
        data = {"status": "205",
                "message": "Can not decipher your JSON"}
        self.assertRaises(exceptions.MalformedJsonError,
                          self.hd._check_status,
                          data)

    def test_NoDataError(self):
        "Status == 206"
        data = {"status": "206",
                "message": "No data in payload"}
        self.assertRaises(exceptions.NoDataError,
                          self.hd._check_status,
                          data)

    def test_VendorMissingError(self):
        "Status == 207"
        data = {"status": "207",
                "message": ("Vendor missing! You must supply a vendor to get a "
                            "model list")}
        self.assertRaises(exceptions.VendorMissingError,
                          self.hd._check_status,
                          data)

    def test_ApiKeyNotSetError(self):
        "Status == 209"
        data = {"status": "209",
                "message": "ApiKey not set – you must set an apikey header"}
        self.assertRaises(exceptions.ApiKeyNotSetError,
                          self.hd._check_status,
                          data)

    def test_UserAgentOrProfileMissingWarning(self):
        "Status == 300"
        data = {"status": "300",
                "message": "User-Agent or x-wap-profile missing in request"}
        self.assertRaises(exceptions.UserAgentOrProfileMissingWarning,
                          self.hd._check_status,
                          data)

    def test_DeviceNotFoundError(self):
        "Status == 301"
        data = {"status": "301",
                "message": "Not Found"}
        self.assertRaises(exceptions.DeviceNotFoundError,
                          self.hd._check_status,
                          data)

    def test_BaseError(self):
        "Testing HandsetDetectionBaseError."
        data = {"status": "-1",
                "message": "No such error"}
        e = exceptions.HandsetDetectionBaseError(int(data["status"]), 
                                                 data["message"],
                                                 data)
        self.assertEqual(str(e), "<Error -1: No such error>")
        self.assertEqual(e.data, data)

if "__main__" == __name__:
    unittest.main()

# vim:set bomb et sw=4 ts=4 tw=79:
