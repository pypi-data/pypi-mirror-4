#!/usr/bin/env python
"A CGI script demonstrating redirection of mobile devices."
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
# Created: 20090811

# This makes debugging errors easier.
import cgitb
cgitb.enable()

import os
import sys

# If you installed handsetdetection as a Python egg outside of the normal
# Python path, put that path in sys.path:
#sys.path.append("/PATH/TO/handsetdetection-1.0-pyPYTHONVERSION.egg")

import handsetdetection

MOBILE_URL = "http://m.example.com/"

def get_client_and_server_data():
    "Get environment data."
    data = {}
    data["HTTP_REFERER"] = os.environ.get("HTTP_REFERER", "")
    data["HTTP_USER_AGENT"] = os.environ.get("HTTP_USER_AGENT", "")
    data["REMOTE_ADDR"] = os.environ.get("REMOTE_ADDR", "")
    data["REQUEST_URI"] = os.environ.get("REQUEST_URI", "")
    data["SERVER_ADDR"] = os.environ.get("SERVER_ADDR", "")
    data["SERVER_NAME"] = os.environ.get("SERVER_NAME", "")
    return data

def redirect_or_welcome(data):
    "Return a response to the browser."
    if data is None:
        result = """Content-type: text/html;charset=UTF-8

<!DOCTYPE html>
<html>
    <head>
        <title>Welcome to our web site</title>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    </head>
    <body>
        <p>Welcome to our web site.  Mobile users should not see this.</p>
    </body>
</html>"""
    else:
        result = """Refresh: 0;url=%s
Content-type: "text/html;charset=UTF-8

<!DOCTYPE html>
<html>
    <head>
        <title>Loading our mobile web site</title>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    </head>
    <body>
        <p>
            In a moment, you will be redirected to our mobile web site at %s.
        </p>
    </body>
</html>""" % (MOBILE_URL, MOBILE_URL)
    sys.stdout.write(result)

def main():
    "Redirect mobile users to MOBILE_URL"
    # First, get the information to pass to Handset Detection.
    hd = handsetdetection
    hd.set_credentials("demo@handsetdetection.com", "demo")
    data = get_client_and_server_data()
    try:
        result = hd.detect(data, "product_info")
        redirect_or_welcome(result)
    except handsetdetection.DeviceNotFoundError, err:
        # Mobile device not detected.
        redirect_or_welcome(None)
    except handsetdetection.HandsetDetectionBaseError, err:
        # Handle the exception
        # In this script, cgitb will handle it, so raise it again.
        raise err

if "__main__" == __name__:
    main()

# Some CGI handlers don't know what to do with a byte-order mark ("bomb").
# vim:set nobomb et sw=4 ts=4 tw=79:
