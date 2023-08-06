#!/usr/bin/env python
"A CGI script listing mobile device vendors."
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

import cgi
import sys

# If you installed handsetdetection as a Python egg outside of the normal
# Python path, put that path in sys.path:
#sys.path.append("/PATH/TO/handsetdetection-1.0-pyPYTHONVERSION.egg")

import handsetdetection

def get_vendor():
    "Get a vendor from the query string or prompt for one."
    formdata = cgi.FieldStorage()
    vendor = formdata.getfirst("vendor", None)
    if vendor is None:
        # Return a form to prompt the user.
        result = """Content-type: text/html;charset=UTF-8

<!DOCTYPE html>
<html>
    <head>
        <title>Mobile Device Models</title>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    </head>
    <body>
        <form method="get">
            <fieldset>
                <legend>Handset Vendor</legend>
                    <label>
                        Vendor
                        <input type="text" name="vendor" id="vendor" />
                    </label>
                <input type="submit" />
            </fieldset>
        </form>
    </body>
</html>"""
        sys.stdout.write(result)
        sys.exit(0)
    else:
        return vendor

def list_models(vendor, modeldata):
    "Return a response to the browser."
    data = {}
    data["vendor"] = vendor
    items = ["<li>%s</li>" % cgi.escape(i) for i in modeldata]
    models = "\n            ".join(items)
    data["models"] = models
    result = """Content-type: text/html;charset=UTF-8

<!DOCTYPE html>
<html>
    <head>
        <title>Mobile Device Models For %(vendor)s</title>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    </head>
    <body>
        <p>
            This is a list of models for %(vendor)s.
        </p>
        <ul>
            %(models)s
        </ul>
    </body>
</html>""" % data
    sys.stdout.write(result)

def main():
    "Show a list of mobile device vendors."
    # First, get the information to pass to Handset Detection.
    vendor = get_vendor()

    hd = handsetdetection
    hd.set_credentials("demo@handsetdetection.com", "demo")
    try:
        result = hd.model(vendor)
        list_models(vendor, result)
    except handsetdetection.HandsetDetectionBaseError, err:
        # Handle the exception
        # In this script, cgitb will handle it, so raise it again.
        raise err

if "__main__" == __name__:
    main()

# Some CGI handlers don't know what to do with a byte-order mark ("bomb").
# vim:set nobomb et sw=4 ts=4 tw=79:
