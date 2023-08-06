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

class CloudNetworks(Cloud):
    
    service = "ServersOpenStack"

    def getNetworks(self):
        """
        List the networks configured for a specified tenant ID.
        """
        self.baseURL('os-networksv2')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createNetwork(self, cidr, label):
        """
        Creates a network for the specified tenant ID.
        
        Arguments:
        cidr -- ip block from which to allocate the network
        label -- name of the new network

        Returns:
        JSON results as python dict
        """
        self.baseURL('os-networksv2')
        self.postKey = 'network'
        self.postKeyVar('cidr',cidr)
        self.postKeyVar('label',label)
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def getNetwork(self, nId):
        """
        Fetches network information with an id input.
        
        Arguments:
        nId -- network id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('os-networksv2/'+str(nId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getNetworks(self):
        """
        Lists the networks configured for a specified tenant ID.
        
        Arguments:
        nId -- network id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('os-networksv2')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteNetwork(self, nId):
        """
        Deletes the specified network.
        
        Arguments:
        nId -- network ID
        
        Returns:
        status code
        """
        self.baseURL('os-networksv2/'+str(nId))
        return apiRequest(self, self.endpoint, "DELETE")
        
    def provisionServer(self, server, imageRef, flavorRef, attrDict={}):
        """
        Provision a new server with the specified networks.
        
        Arguments:
        server -- Server name
        imageRef -- image id
        flavorRef -- flavor id(string)
        attrDict -- dictionary the following a combination of the following var/vals:
            networks -- list of network uuid's (inside of uuid key dictionaries) to provision server(s) to (Optional)
            OS-DCF:diskConfig -- AUTO / MANUAL (Optional)
            metadata -- dictionary of key-value meta-data (Optional)
            personality -- list of dictionaries specifiying file path and contents (Optional)
        
        Returns:
        JSON results as python dict
        """

        self.baseURL('servers')
        self.attrDict = attrDict
        self.postKey = 'server'

        #required args
        self.postKeyVar('name',server)
        self.postKeyVar('imageRef',imageRef)
        self.postKeyVar('flavorRef',str(flavorRef))

        #optional args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)

#eof
