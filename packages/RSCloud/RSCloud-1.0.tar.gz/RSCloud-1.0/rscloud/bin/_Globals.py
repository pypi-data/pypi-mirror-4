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

import requests
import re
import os
import simplejson as json
import traceback
import sys
import logging

#make log dir if doesn't exist
if not os.path.exists("log"):
    os.makedirs("log")
    
#setup root logger. Valid levels (DEBUG,INFO,WARNING,ERROR,CRITICAL)
logging.basicConfig(
    filename='log/RSCloud.log',
    level=logging.DEBUG,
    format='%(levelname)s %(name)s %(asctime)s %(message)s'
    )

#setup scheduler logger.  Logging levels (DEBUG,INFO,WARNING,ERROR).
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def apiRequest(obj, endpoint, apiType, data=None, returnResults=False, dataType='json'):
    """
    Makes api request to the specified endpoint with the provided details
    
    Arguments:
    obj -- Calling object
    endpoint -- Api endpoint(string)
    apiType -- GET, POST, PUT, DELETE etc.(string)
    data -- Python dict data for endpoint
    returnResults -- True: returns JSON results as Python Dict. False returns status code
    
    Returns:
    Results or status code
    """
    try:
        obj.auth.validate()
        
        if re.search("GET", apiType.upper()):
            r = requests.get(endpoint, headers=obj.auth.headers)
        elif re.search("DELETE", apiType.upper()):
            r = requests.delete(endpoint, headers=obj.auth.headers)
        elif re.search("HEAD", apiType.upper()):
            r = requests.head(endpoint, headers=obj.auth.headers)
        elif re.search("POST", apiType.upper()) and data is not None:
            r = requests.post(endpoint, data=json.dumps(data), headers=obj.auth.headers)
        elif re.search("POST", apiType.upper()) and data is None:
            r = requests.post(endpoint, headers=obj.auth.headers)
        elif re.search("PUT", apiType.upper()) and data is None:
            r = requests.put(endpoint, headers=obj.auth.headers)
        elif re.search("PUT", apiType.upper()) and data is not None and dataType == "json":
            r = requests.put(endpoint, data=json.dumps(data), headers=obj.auth.headers)
        elif re.search("PUT", apiType.upper()) and data is not None and dataType == "file":
            r = requests.put(endpoint, data=data, headers = obj.auth.headers)
        else:
            raise RSException('apiRequest', 'Invalid api type or data')
        
        if re.search("HEAD", apiType.upper()):
            resultType='headers'
            results = r.headers
        elif returnResults:
            if returnResults == "raw":
                resultType='status_code'
                results = r.status_code
            elif returnResults == "headers":
                resultType='headers'
                results = r.headers
            else:
                resultType='json'
                results = json.loads(json.dumps(json.loads(r.text)))
        else:
            resultType = 'status_code'
            results = r.status_code
        
        if int(r.status_code) >= 200 and int(r.status_code) <= 299:
            logging.debug("Success: %s" % results)    
            if returnResults == "raw":
                results = r.content
            elif returnResults == "headers":
                results = r.headers
            return results
        else:
            log.debug("error: %s" % resultType)
            log.debug("postData:")
            log.debug(obj.postData)
            log.debug("endpoint:")
            log.debug(obj.endpoint)
            log.debug(results)
            logging.error("Error: %s" % results)
            return results
    except requests.exceptions.RequestException as error:
        #log the error
        e = "Error when processing request %s to %s - check logs" % (apiType, endpoint)
        print "---"
        print e
        print "postData:"
        print obj.postData
        print "endpoint:"
        print obj.endpoint
        print "---"
        logging.error(e)
        #format the trace and log
        type_, value_, traceback_ = sys.exc_info()
        tb = traceback.format_exception(type_, value_, traceback_)
        logging.error(tb)
        #re-raise
        raise Exception(e)
    except:
        e = "Unexpected error from request %s to %s - check logs" % (apiType, endpoint)
        print e
        logging.error(e)
        type_, value_, traceback_ = sys.exc_info()
        tb = traceback.format_exception(type_, value_, traceback_)
        logging.error(tb)
        raise Exception(e)

#eof

