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

from yaml import load
from simplejson import loads,dumps
from Auth2 import *
from bin._Globals import *
from bin._Exceptions import *
from urllib import quote

#setup stdout debug logging (True/False) 
#NOTE: This is just for showing in stdout clearly where the test outputs start and stop.
try:
    with open('soLog') as f:
        soLog = True
except IOError as e:
    soLog = False

class Cloud(object):
  
    #attributes{{{

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
    
    #}}}
    def __init__(self, env, region=None):
        """
        Initialization of Cloud object.  Defaults to LON or ORD based on env.
        
        Arguments:
        env -- us or uk etc
        region -- LON, DFW or ORD
        """

        if not re.search("us", env, re.IGNORECASE) and not re.search("uk", env, re.IGNORECASE):
            raise RSException("__init__", "Valid env needs to be us/uk")
        
        self.auth = Auth2(env) #re-validate
        self.env = env.upper()
        
        #soLog (temporary stdout handling)
        self.soLogFlg = soLog

        try:
            f = file(os.path.join(self.pd,".cloudServices%s.yml" % self.env), 'r')
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
            raise RSException("__init__")
            
        if self.publicURL is None:
            raise RSException("__init__", "publicURL value cannot be None") 
        
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
