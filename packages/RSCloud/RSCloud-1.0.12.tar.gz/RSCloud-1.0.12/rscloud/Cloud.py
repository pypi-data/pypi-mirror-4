#!/usr/bin/python
        
# Copyright 2012 Rackspace Hosting {{{
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
# }}}

from Auth2 import *
from bin._Globals import *
import time as tm

class Cloud(object):
  
    #properties{{{

    publicURL = None
    internalURL = None
    cdnURL = None
    auth = None
    env = None
    region = None
    pd = os.path.dirname(os.path.realpath(__file__))
    endpoint = None
    postData = {}
    soLogFlg = None
    
    #logging info for request
    reqHeaders = None
    reqVerb = None
    reqEndpoint = None
    reqData = None
    reqDataType = None
    respHeaders = None
    
    #properties }}}
    def __init__(self, env, region=None):
        """
        Initialization of Cloud object.  Defaults to LON or ORD based on env.
        
        Arguments:
        env -- us or uk etc
        region -- LON, DFW or ORD
        """

        if not re.search("us", env, re.IGNORECASE) and not re.search("uk", env, re.IGNORECASE):
            log.warning("Valid env needs to be us/uk and not %s in Cloud.__init__()" % env)
        
        self.auth = Auth2(env) #re-validate
        self.env = env.upper()
        
        #soLog (temporary stdout handling)
        self.soLogFlg = soLog

        try:
            f = file(os.path.expanduser("~/.cloudServices%s.yml" % self.env), 'r')
            services = load(f)
            f.close
        
            for service in services:
                if service['name'] == "cloud"+self.service:
                    if region is None:
                        self.publicURL = service['endpoints'][0]['publicURL']
                        if 'internalURL' in service['endpoints'][0]:
                            self.internalURL = service['endpoints'][0]['internalURL']
                    else:
                        self.region = region
                        for endpoint in service['endpoints']:
                            if 'region' not in endpoint or re.search(region, endpoint['region'], re.IGNORECASE):
                                self.publicURL = endpoint['publicURL']
                                if 'internalURL' in endpoint:
                                    self.internalURL = endpoint['internalURL']
                #if cloudFiles service, grab cdnURL
                if self.service == "Files" and service['name'] == 'cloudFilesCDN':
                    if region is None:
                        self.cdnURL = service['endpoints'][0]['publicURL']
                    else:
                        for endpoint in service['endpoints']:
                            if re.search(region, endpoint['region'], re.IGNORECASE):
                                self.cdnURL = endpoint['publicURL']
        except:
            log.warning("Unhandled exception caught in Cloud.__init__()")
            
        if self.publicURL is None:
            log.warning("publicURL value cannot be None in Cloud.__init__()") 
        
    @innerCls
    class run(object):

        #properties {{{
        
        results = None
        startTime = None
        duration = None
        soLogFlg = None
        #dbLogFlg = None
        
        #properties }}}
        def __init__(self, tMethod, eResults, tArgs=None, resultsLoc=None, timeout=None, dbLogFlg=True, soLogFlg=None):
            if soLogFlg is None:
                self.soLogFlg = soLog
            else:
                self.soLogFlg = soLogFlg
            if timeout is not None: #async request
                self.async(tMethod, eResults, tArgs, resultsLoc, timeout)
            else:
                self.sync(tMethod, eResults, tArgs, resultsLoc)
            
        def sync(self, tMethod, eResults, tArgs, resultsLoc, timeout=None):
            
            if self.soLogFlg:
                print "\nSync: %s" % tMethod
            try:
            #if True:
                if self.startTime is None:
                    self.startTime = time()
                func = getattr(self.outer, tMethod)
                if tArgs is not None:
                    args = []
                    kwargs = {}
                    for arg in tArgs:
                        args.append(arg)
                    self.results = func(*args, **kwargs)
                else:
                    self.results = func()
                self.setDuration()
            #try:
            #    foo=1
            except Exception as e:
                self.setDuration()
                print e.args #debug info
                type_,value_,traceback_ = e.args[0]
                tb = traceback.format_exception(type_, value_, traceback_)
                if timeout is not None:
                    raise Exception

            except:
                self.setDuration()
                print "Unhandled exception caught in api()"
                type_, value_, traceback_ = sys.exc_info()
                tb = traceback.format_exception(type_, value_, traceback_)
                if timeout is not None:
                    raise Exception
                    
            if resultsLoc is None:
                if (type(self.results) is int and (self.results >= 200 and self.results <= 299)) or (type(self.results) is str and (re.search(eResults,str(self.results)))):
                    foo=1
                else:
                    print self.results
                    print "Failed %s in %s seconds" % (tMethod, str(self.duration))
                    return True
            else:
                if re.search(r"'?%s'?: '?%s'?" % (resultsLoc, eResults), str(self.results), re.IGNORECASE):
                    if timeout is not None:
                        return True #async flag
                else:
                    if re.search("'%s': 'ERROR'" % resultsLoc, str(self.results), re.IGNORECASE):
                        print "Failed on %s with ERROR on key %s" % (tMethod, resultsLoc)
                    if timeout is not None:
                        return False
                    elif resultsLoc=='...' and eResults=='...':
                        foo=1;
                    else:
                        print "Failed to match key %s with value %s" % (resultsLoc, eResults)
                        print self.results
                    
        def async(self, tMethod, eResults, tArgs, resultsLoc, timeout):
            """
            Loop api() for expected results w/ timeout
            """

            if self.soLogFlg:
                print "\nAsync: %s" % tMethod
            try:
                loopStart = time()
                found = False
                while ((time() - loopStart) < int(timeout)) and not found:
                    found = self.sync(tMethod, eResults, tArgs, resultsLoc, timeout)
                    if not found:
                        sleep(30)
                if not found:
                    print "Timeout - Unable to find '%s': '%s' in results" % (resultsLoc, eResults)

            except Exception:
                print "-- Exception caught in async, check log --"
                
            
        def setDuration(self):
            self.duration = time() - self.startTime
            
        
    def apiRequest(self,endpoint, apiType, data=None, returnResults=False, dataType='json'):
        """
        Makes api request to the specified endpoint with the provided details
        
        Arguments:
        #obj -- Calling object
        endpoint -- Api endpoint(string)
        apiType -- GET, POST, PUT, DELETE etc.(string)
        data -- Python dict data for endpoint
        returnResults -- True: returns JSON results as Python Dict. False returns status code
        
        Returns:
        Results or status code
        """
        
        #debugging
        with open("/var/log/all.log", "a") as allLog:
            loctime = tm.localtime();
            timeString = tm.strftime("%Y%m%d%H%M%S", loctime)
            allLog.write(endpoint+":("+apiType+")\n")
            allLog.write(str(data)+"\n")
        #debugging

        #if True:
        try:
            self.auth.validate()
        
            if re.search("GET", apiType.upper()):
                r = requests.get(endpoint, headers=self.auth.headers, timeout=timeout)
                #chk = True
                #while chk:
                #    #temporary hack
                #    try:
                #        r = requests.get(endpoint, headers=self.auth.headers, timeout=timeout)
                #        chk  = False
                #    except IOError: 
                #        print "Retrying: due to closed connection (54)"
                #        time.sleep(5)
            elif re.search("DELETE", apiType.upper()):
                r = requests.delete(endpoint, headers=self.auth.headers, timeout=timeout)
            elif re.search("HEAD", apiType.upper()):
                r = requests.head(endpoint, headers=self.auth.headers, timeout=timeout)
            elif re.search("POST", apiType.upper()) and data is not None:
                r = requests.post(endpoint, data=json.dumps(data), headers=self.auth.headers, timeout=timeout)
            elif re.search("POST", apiType.upper()) and data is None:
                r = requests.post(endpoint, headers=self.auth.headers, timeout=timeout)
            elif re.search("PUT", apiType.upper()) and data is None:
                r = requests.put(endpoint, headers=self.auth.headers, timeout=timeout)
            elif re.search("PUT", apiType.upper()) and data is not None and dataType == "json":
                r = requests.put(endpoint, data=json.dumps(data), headers=self.auth.headers, timeout=timeout)
            elif re.search("PUT", apiType.upper()) and data is not None and dataType == "file":
                r = requests.put(endpoint, data=data, headers = self.auth.headers, timeout=timeout)
            else:
                log.warning('Invalid apiType(verb) or data in _Globals.apiRequest()')
        
            #log data
            self.reqHeaders = self.auth.headers
            self.reqVerb = apiType
            self.reqEndpoint = endpoint
            self.reqDataType = dataType
            if dataType == 'json':
                self.reqData = data
            self.respHeaders = r.headers
        
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
                log.debug(self.postData)
                log.debug("endpoint:")
                log.debug(self.endpoint)
                log.debug(results)
                logging.error("Error: %s" % results)
                return results
        #try:
        #    foo=1
        except requests.exceptions.RequestException as error:
            #log the error
            e = "Error when processing request %s to %s - check logs" % (apiType, endpoint)
            print "---"
            print e
            print "postData:"
            print self.postData
            print "endpoint:"
            print self.endpoint
            print "---"
            logging.error(e)
            #format the trace and log
            type_, value_, traceback_ = sys.exc_info()
            tb = traceback.format_exception(type_, value_, traceback_)
            logging.error(tb)
            #re-raise
            raise Exception(sys.exc_info())
        except:
            e = "Unexpected error from request %s to %s - check logs" % (apiType, endpoint)
            print e
            logging.error(e)
            type_, value_, traceback_ = sys.exc_info()
            tb = traceback.format_exception(type_, value_, traceback_)
            logging.error(tb)
            raise Exception(sys.exc_info())
        
    def baseURL(self, base):
        """
        Updates endpoint with publicURL and base.
        """
        self.postData={}
        #check to see if the full url is there (ie: Async cmd), otherwise use publicURL
        if re.search('https://',str(base).lower()) or re.search('http://',str(base).lower()):
            self.endpoint = "%s?" % (str(base))
        else:
            self.endpoint = "%s/%s?" % (self.publicURL,str(base))
        
    def _baseURL(self, base):
        """
        Updates endpoint with publicURL and base. (uri)
        """
        base = self.uri(base)
        self.baseURL(base)
        
    def basecdnURL(self, base):
        """
        Updates endpoint with cdnURL and base.
        """
        self.postData={}
        #check to see if the full url is there (ie: Async cmd), otherwise use publicURL
        if re.search('https://',str(base).lower()) or re.search('http://',str(base).lower()):
            self.endpoint = "%s?" % (str(base))
        else:
            self.endpoint = "%s/%s?" % (self.cdnURL,str(base))
        
    def _basecdnURL(self, base):
        """
        Updates endpoint with publicURL and base. (uri)
        """
        base = self.uri(base)
        self.basecdnURL(base)
        
    def queryVar(self, key, val):
        """
        Updates endpoint with key and val.
        """
        if val is not None:
            self.endpoint = self.endpoint + "%s=%s&" % (str(key),str(val))
        
    def _queryVar(self, key, val):
        """
        Updates endpoint with key and val. (uri)
        """
        val = self.uri(val)
        self.queryVar(var,val)
        
    def queryDictVar(self,key,attrKey=None):
        """
        Updates endpoint with a dictionary key and the key's val.
        """
        if attrKey is None:
            attrKey=key
        if attrKey in self.attrDict and self.attrDict[attrKey] is not None:
            self.endpoint = "%s=%s&" % (str(key),str(self.attrDict[attrKey]))
        
    def attrDictDefaultKeyVal(self,attrKey,attrVal):
        """
        Updates attrDict key with a default val (if == None).
        """
        if attrKey not in self.attrDict or self.attrDict[attrKey] is None:
            self.attrDict[attrKey] = attrVal
        
    def postVar(self,key,val):
        """
        Updates post data with key and val.
        """
        if val is not None:
            self.postData[str(key)] = val
        
    def postDictVar(self,key,attrKey=None):
        """
        Updates post data with a dictionary key and the key's val.
        """
        if attrKey is None:
            attrKey = key
        if attrKey in self.attrDict and self.attrDict[attrKey] is not None:
            self.postData[str(key)] = str(self.attrDict[attrKey])
    def postDict(self):
        """
        Updates post data with all discovered dictionary keys + vals.
        """
        if self.attrDict is not None:
            for key,value in self.attrDict.items():
                if value is not None:
                    self.postData[str(key)] = value
        
    def postKeyVar(self,key,val):
        """
        Updates post data with key and val.
        """
        if str(self.postKey) not in self.postData:
            self.postData[str(self.postKey)] = {}
        self.postData[str(self.postKey)][str(key)] = val
        
    def postKeyDictVar(self,key,attrKey=None):
        """
        Updates post data with a dictionary key and the key's val.
        """
        if attrKey is None:
            attrKey = key
        if str(self.postKey) not in self.postData:
            self.postData[str(self.postKey)] = {}
        if self.attrDict is not None and attrKey in self.attrDict and self.attrDict[attrKey] is not None:
            self.postData[str(self.postKey)][str(key)] = self.attrDict[attrKey]
    def postKeyDict(self):
        """
        Updates post data with all discovered dictionary keys + vals.
        """
        #print "fljljl"
        #print "---"
        #print self.attrDict
        #print "---"
        #print "ljsdljfsljsdfl"
        if self.attrDict is not None and self.attrDict != {}:
            if str(self.postKey) not in self.postData:
                self.postData[str(self.postKey)] = {}
            if self.attrDict is not None:
                for key,value in self.attrDict.items():
                    if value is not None:
                        self.postData[str(self.postKey)][str(key)] = value
        
    def postKeyListDict(self):
        """
        Updates post data with a list of all discovered dictionaries and their keys + vals.
        """
        if str(self.postKey) not in self.postData:
            self.postData[str(self.postKey)] = []
        if self.attrList is not None:
            for d in self.attrList:
                tmpDict = {} 
                for key,value in d.items():
                    if value is not None:
                        tmpDict[str(key)] = value
                self.postData[str(self.postKey)].append(tmpDict)
        
    def queryDict(self):
        """
        Updates endpoint with all discovered dictionary keys + vals.
        """
        if self.attrDict is not None:
            for key,value in self.attrDict.items():
                self.endpoint = self.endpoint + "%s=%s&" % (str(key),str(value))
        
    def _queryDict(self):
        """
        Updates endpoint with all discovered dictionary keys + vals. (uri)
        """
        if self.attrDict is not None:
            for key,value in self.attrDict.items():
                value = self.uri(value)
                self.endpoint = self.endpoint + "%s=%s&" % (str(key),str(value))
        
    def uri(self,val):
        """
        Convert string to uri compliance.
        """
        return unicode(quote(str(val)), 'utf-8')
        
    def so_chk1(self):
        """
        For testing.
        """
        if self.soLogFlg:
            print "endpoint: "+self.endpoint 
            print "postData: "+str(self.postData)

#eof
