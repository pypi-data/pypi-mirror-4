"Utilities to make tests friendly"
# Copyright (c) 2009 Troy Farrell
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
# Created: 20090727

import os.path
import sys

def importModule(moduleName):
    "Import a module, modifying sys.path if necessary."
    try:
        return __import__(moduleName)
    except ImportError:
        # Get some paths for reference.
        thisModuleDirectoryPath = getTestDirectoryPath()
        parentDirectoryPath, thisModuleDirectory = \
 os.path.split(thisModuleDirectoryPath)
        # If the module name has dots, we need to find the first one.
        if "." in moduleName:
            baseModuleName = moduleName.split(".", 1)[0]
            modulePath = os.path.join(parentDirectoryPath, baseModuleName)
        else:
            modulePath = os.path.join(parentDirectoryPath, moduleName)

        if (os.path.isfile(modulePath + ".py") or \
            os.path.isfile(modulePath) or  \
            os.path.isdir(modulePath)) and \
            parentDirectoryPath not in sys.path:
            sys.path.append(parentDirectoryPath)
            return __import__(moduleName)
        else:
            assert False, "Unable to import %r" % moduleName

def getTestDirectoryPath():
    "Return the full path to the test directory."
    # We do this rigamarole in the event the current directory is not the test
    # directory (i.e., where "empty" resides.)
    thisFilePath = os.path.abspath(__file__)
    testDirectoryPath, thisFileName = os.path.split(thisFilePath)
    return testDirectoryPath

# vim:set bomb et sw=4 ts=4 tw=79:
