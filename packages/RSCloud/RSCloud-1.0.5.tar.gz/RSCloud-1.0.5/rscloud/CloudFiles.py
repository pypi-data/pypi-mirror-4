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

from Cloud import *

class CloudFiles(Cloud):
    """
    A class to interface into Rackspace Cloud Files.
    """

    service = "Files"

    #Storage Account Services{{{

    def getAccountMeta(self):
        """
        Retrieves the number of containers and the total bytes stored in Cloud Files for the account. 
        
        Returns:
        Results header as string
        """
        return apiRequest(self, self.publicURL, "HEAD")
        
    def setAccountMeta(self, metaDict):
        """
        Allows for metadata entries to an account(TempURL or form posts etc)
        
        Arguments:
        metaDict -- Python dictionary of key/value pairs to be added.
        
        Returns:
        status code
        """
        
        try:
            self.auth.headers = dict(self.auth.headers.items() + metaDict.items())
            return apiRequest(self, self.publicURL, "POST")
        except:
            raise RSException('setAccountMeta')
        
    def getContainers(self, attrDict={}): #limit=None, marker=None, format='json'):
        """
        Lists the available containers in the Cloud Files account.
        
        Arguments:
        attrDict --
            limit -- For an integer value n, limits the number of results to n values. (Optional)
            marker -- Given a string value x, return object names greater in value than the marker. (Optional)
            format -- Specify either json or xml to return the respective serialized response. (Optional)
        """
        
        self.baseURL('')
        if format not in attrDict:
            attrDict['format'] = 'json'
        self.attrDict = attrDict
        self._queryDict()
        #self.queryVar('format',format)
        #if limit is not None:
        #    self.queryVar('limit',limit)
        #if marker is not None:
        #    self._queryVar('marker',marker)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    #}}}
    #Storage Container Services{{{

    def createContainer(self, container, metaDict=None):
        """
        Create a container at the root of the CF account.
        
        Arguments:
        container -- container name (string)
        metaDict -- A python dictionary with key/value pairs for metadata tags and desc etc.  
            Must be valid UTF-8 http header and take the format X-Container-Meta- etc.
        
        Returns:
        status code
        """
        self._baseURL(container)
        try:
            if metaDict is not None:
                self.auth.validate() #make sure new headers don't get overwritten
                self.auth.headers = dict( self.auth.headers.items() + metaDict.items() )
            return apiRequest(self, self.endpoint, "PUT")

        except:
            raise RSException('setContainer')
        
    def deleteContainer(self, container):
        """
        Permanently remove a container.  Must be empty
        
        Arguments:
        container --
        
        Returns:
        status code
        """
        self._baseURL(container)
        return apiRequest(self, self.endpoint, "DELETE")
        
    def getContainerMeta(self, container):
        """
        Retrieves metadata for a specified container.
        
        Arguments:
        container --
        
        Returns:
        Header info as string
        """
        self._baseURL(container)
        return apiRequest(self, self.endpoint, "HEAD")
        
    def setContainerMeta(self, container, metaDict):
        """
        Create or update metadata on a container.
        
        Arguments:
        container --
        metaDict -- A python dictionary with key/value pairs for metadata tags and desc etc.  
            Must be valid UTF-8 http header and take the format X-Container-Meta- etc.
        
        Returns:
        status code            
        """
        self._baseURL(container)
        try:
            if metaDict is not None:
                self.auth.validate() #make sure new headers don't get overwritten
                self.auth.headers = dict( self.auth.headers.items() + metaDict.items() )
            return apiRequest(self, self.endpoint, "POST")
        except:
            raise RSException('setContainerMeta')
        
    def getObjects(self, container, attrDict={}): 
        """
        Retrieves a list of objects stored in the container. Additionally, there are a number of optional 
        query parameters that can be used to refine the list results.
        
        Arguments:
        container --
        attrDict --
            limit -- For an integer value n, limits the number of results to n values. (Optional)
            marker -- Return object names greater in value than the specified marker. (Optional)
            prefix -- Causes the results to be limited to object names beginning with the substring (Optional)
            format -- Specify either json or xml to return the respective serialized response. Default json (Optional)
            path -- Return the object names nested in the pseudo path.  (Optional)
            delimiter -- Return all the object names nested in the container with given delimiter (Optional)
        
        Returns:
        JSON results as python dict
        """
        self._baseURL(container)
        if format not in attrDict:
            attrDict['format'] = 'json'
        self.attrDict = attrDict
        self._queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    #}}}
    #Storage Object Services{{{

    def getObject(self, container, myObject, headersList=None):
        """
        Retrieves CF objects data.
        
        Arguments:
        container --
        myObject --
        headersList -- HTTP headers as documented in RFC 2616 as key/value in python dictionary. See api docs.
        
        Returns:
        Binary content on success or status code on failure.
        """
        self._baseURL(self.uri(container)+"/"+self.uri(myObject))
        try:
            if headersList is not None:
                self.auth.validate()
                self.auth._setHeaders(noType=True)
                self.auth.headers = dict( self.auth.headers.items() + headersList.items() )
            return apiRequest(self, self.endpoint, "GET", returnResults='raw')
        except:
            raise RSException('getObject')
        
    def createObject(self, container, myObject, data, headersList=None):
        """
        PUT object into CF container.
        
        Arguments:
        container --
        myObject -- Object name(string)
        data -- File object
        headersList -- HTTP headers as documented in RFC 2616 as key/value in python dictionary. See api docs. (Optional)
        
        Returns:
        Header results
        """
        self.baseURL(self.uri(container)+"/"+self.uri(myObject))
        self.postData = data
        try:
            if headersList is not None:
                self.auth.validate()
                self.auth._setHeaders(noType=True)
                self.auth.headers = dict( self.auth.headers.items() + headersList.items() )
            return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults='headers', dataType='file')
        except:
            raise RSException('setObject')
        
    def copyObject(self, sourceContainer, sourceObject, destContainer, destObject):
        """
        Copy object into CF container.
        
        Arguments:
        sourceContainer --
        sourceObject -- Name(string)
        destContainer -- 
        destinationObject -- Name(string)
        
        Returns:
        status code
        """
        self._baseURL(self.uri(destContainer)+"/"+self.uri(destObject))
        self.auth.validate()
        self.auth._setHeaders(noType=True)
        headers = { 'X-Copy-From': '/%s/%s' % (self.uri(sourceContainer), self.uri(sourceObject)), 'Content-Length': '0'}
        self.auth.headers = dict( self.auth.headers.items() + headers.items() )
        return apiRequest(self, self.endpoint, "PUT")
        
    def deleteObject(self, container, myObject):
        """
        Delete CF object.
        
        Arguments:
        container --
        myObject --
        
        Returns:
        status code
        """
        self.baseURL(self.uri(container)+"/"+self.uri(myObject))
        return apiRequest(self, self.endpoint, "DELETE")
        
    def getObjectMeta(self, container, myObject):
        """
        Retrieves object metadata.
        
        Arguments:
        container --
        myObject --
        
        Returns:
        Header info
        """
        self.baseURL(self.uri(container)+"/"+self.uri(myObject))
        return apiRequest(self, self.endpoint, "HEAD")
        
    def setObjectMeta(self, container, myObject, metaDict):
        """
        Replaces user defined metadata with supplied.
        
        Arguments:
        container --
        myObject --
        metaDict -- Python dictionary with key/values to be added.   Keys must be prefixed with X-Object-Meta
        
        Returns:
        status code
        """
        self.baseURL(self.uri(container)+"/"+self.uri(myObject))
        try:
            self.auth.validate()
            self.auth.headers = dict(self.auth.headers.items() + metaDict.items() )
            return apiRequest(self, self.endpoint, "POST")
        except:
            raise RSException("setObjectMeta")

    #}}}
    #CDN Services{{{

    def setCDNContainer(self, container, enabled=True, ttl=None):
        """
        Enable or disable CDN services on a container.
        
        Arguments:
        container --
        enabled -- bool (Optional)
        ttl -- How long till CDN cache expires.   The default TTL value is 259200 seconds, or 72 hours (Optional)
        
        Returns:
        headers as string
        """
        headers = { 'X-CDN-Enabled': str(enabled), 'X-Log-Retention': str(enabled) }
        if ttl is not None:
            headers['ttl'] = ttl
        self._basecdnURL(container)
        return apiRequest(self, self.endpoint, "PUT", returnResults='headers')
        
    def getCDNContainers(self, attrDict={}): 
        """
        Container list request from the CDN service.  It will default to showing public and private containers.
        
        Arguments:
        attrDict -- 
            limit -- Limits the number of results to n values. (Optional)
            marker -- Return object names greater in value than the specified marker. (Optional)
            format -- either json or xml for serialized output.  Default json (Optional)
            enabledOnly -- If True, only shows CDN enabled containers (Optional)
        
        Returns:
        JSON results as python dict
        """
        self.basecdnURL('')
        if format not in attrDict:
            attrDict['format'] = 'json'
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setCDNContainerMeta(self, container, metaDict):
        """
        Adjust CDN containers attributes.
        
        Arguments:
        container --
        metaDict -- Python dictionary with key/value pairs to append to container metadata
        
        Returns:
        Headers as string
        """
        self._basecdnURL(container)
        try:
            self.auth.headers = dict( self.auth.headers.items() + metaDict.items() )
            return apiRequest(self, self.endpoint, "POST", returnResults="headers")
        except:
            raise RSException('setCDNContainerMeta')
            
    def getCDNContainerMeta(self, container):
        """
        Returns metadata for specified CDN container.
        
        Arguments:
        container --
        
        Returns:
        Headers as string
        """
        self._basecdnURL(container)
        return apiRequest(self, self.endpoint, "HEAD")
        
    def deleteCDNObject(self, container, myObject):
        """
        Purge CDN cache for a published object. Limit 25/day
        
        Arguments:
        container --
        myObject --
        
        Returns:
        status code
        """
        self._basecdnURL(self.uri(container)+"/"+self.uri(myObject))
        return apiRequest(self, self.endpoint, "DELETE")

    #}}}

#eof            
