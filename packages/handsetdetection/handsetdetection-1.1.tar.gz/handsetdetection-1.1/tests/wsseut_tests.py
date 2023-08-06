"""Tests for the WSSE UserToken implementation for the Handset Detection Python
API Kit."""
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

import unittest

#import handsetdetection.wsseut as wsseut
# The next few lines make the import work if the test is run from the tests
# directory.
import testutils
handsetdetection = testutils.importModule("handsetdetection.wsseut")
wsseut = handsetdetection.wsseut
del handsetdetection

class HandsetDetectionWSSEUsernameTokenTests(unittest.TestCase):
    "Tests for WSSE support"

    def testWSSEUTHeaders(self):
        "Test password digest generation."
        authHeader='WSSE profile="UsernameToken"'
        wsseHeader=('UsernameToken Username="bob", '
        'PasswordDigest="quR/EWLAV4xLf9Zqyw4pDmfV9OY=", '
        'Nonce="ZDM2ZTMxNjI4Mjk1OWE5ZWQ0Yzg5ODUxNDk3YTcxN2Y=", '
        'Created="2003-12-15T14:43:07Z"')
        ut = wsseut.WSSEUserTokenHeaderGenerator(
                "bob",
                "taadtaadpstcsm",
                "d36e316282959a9ed4c89851497a717f",
                "2003-12-15T14:43:07Z")
        headers = ut.next()
        self.assertEquals(headers["X-WSSE"], wsseHeader)
        self.assertEquals(headers["Authorization"], authHeader)
        # Verify that we can get them a second time.
        headers = ut.get_headers()
        self.assertEquals(headers["X-WSSE"], wsseHeader)
        self.assertEquals(headers["Authorization"], authHeader)
        # Verify that next generates a new nonce and datetime
        headers = ut.next()
        self.assertNotEquals(headers["X-WSSE"], wsseHeader)
        self.assertEquals(headers["Authorization"], authHeader)

    def testWSSEUTIteration(self):
        "Test that a single UserTokenHeaderGenerator can work several times."
        ut = wsseut.WSSEUserTokenHeaderGenerator("bob", "taadtaadpstcsm")
        headers = set()
        for headerpair in ut:
            i = headerpair.items() # [("foo", 1), ("bar, 2),...]
            i.sort()               # Sort by the key
            t = tuple(i)           # Create tuple because lists are not
                                   # hashable and cannot be put in sets.
            self.assert_(t not in headers, "Generated duplicate headers!")
            headers.add(t)
            if len(headers) > 4:
                break

if "__main__" == __name__:
    unittest.main()

# vim:set bomb et sw=4 ts=4 tw=79:
