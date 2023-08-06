#!/usr/bin/python

#{{{
# Copyright 2012 Rackspace Hosting
#
# Contact - Nate House nathan.house@rackspace.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   ----
#}}}

import logging
import traceback
import sys

"""  
exception classes
"""

class Error(StandardError):
    """
    Base class for all errors and exceptions
    """
    pass
    
class RSException(Error):
    """
    Raised on a 
    """
    def __init__(self, methodName=None, desc=None):
        if methodName is None: 
            pass
        elif desc is None:
            e = "RSException error from %s" % methodName
            print e
            logging.error(e)
            type_, value_, traceback_ = sys.exc_info()
            tb = traceback.format_exception(type_, value_, traceback_)
            logging.error(tb)
        else:
            e = "RSException error from %s - %s" % (methodName, desc)
            print e
            logging.error(e)
            type_, value_, traceback_ = sys.exc_info()
            tb = traceback.format_exception(type_, value_, traceback_)
            logging.error(tb)

#eof
