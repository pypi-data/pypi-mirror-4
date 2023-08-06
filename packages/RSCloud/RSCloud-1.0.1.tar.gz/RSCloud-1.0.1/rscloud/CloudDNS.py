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

class CloudDNS(Cloud):
    """
    A class that handles actions to Cloud DNS via public methods listed.
    """
    
    service = "DNS"
    
    #Limits{{{

    def getLimits(self, type=None):
        """
        Lists all current api limits for CloudDB.  Passing type=list_types will show all available types of limits and passing
        type=<type> will show you assigned limits for that type.
        
        Arguments:
        type -- Limit type(string)(Optional)
        
        Returns:
        JSON results as a python dict
        """
        if type is not None:
            if re.search("list_types", str(type), re.IGNORECASE):
                self.baseURL('limits/types')
            else:
                self.baseURL('limits/'+str(type).lower())
        else:
            self.baseURL('limits')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    #}}}
    #Domains{{{

    def getDomains(self, name=None):
        """
        Lists all account domains.  Filter by name, if specified.  Use getDomainsId for more
        detailed response.
        
        Arguments:
        name -- Domain name(string)
        
        Returns:
        JSON results as a python dict
        """
        self.baseURL('domains')
        self.queryVar('name',name)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getDomain(self, domainId, attrDict={}): 
        """
        List details for a specific domain, using the showRecords and showSubdomains 
        parameters that specify whether to request information for records and subdomains.
        
        Arguments:
        domainId --
        attrDict --
            showRecords -- (Optional)
            showSubdomains -- (Optional)
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('domains/'+str(domainId))
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getDomainChanges(self, domainId, changeSince):
        """
        Show all changes to the specified domain since the specified date/time in ISO format(2011-09-13T00:00:00-0500)
        
        Arguments:
        domainId --
        changeSince -- format 2011-05-19T08:07:08-0500 etc
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('domains/'+str(domainId)+'/changes')
        self.queryVar('since',changeSince)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getDomainExport(self, domainId):
        """
        Export details of the specified domain id.
        
        Arguments:
        domainId --
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('domains/'+str(domainId)+'/export')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createDomains(self, attrList, returnResults=False):
        """
        Create domain requests given the provided info.  The recordsList is a list of "records" using
        name, type(A,CNAME, etc), data and ttl. The subdomains is a list of "domains" using name, comment 
        and emailAddress.  See api docs for examples.
        
        Arguments:
        attrList: python list of dictionaries: 
            name -- (Required)
            emailAddress -- (Required)
            ttl -- (Optional)
            commment -- (Optional)
            #recordsList -- (Optional)
            #subdomains -- (Optional)
        returnResults -- True / False - receive the Async Json (True) or the Response Code (Optional)

        Returns: Depends on returnResults arg.
        """
        self.baseURL('domains')
        self.postKey = 'domains'
        self.attrList = attrList
        self.postKeyListDict()
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=returnResults)    
        
    def createDomain(self, name, email, attrDict={}, returnResults=False):
        """
        Create domain request given the provided info.  The recordsList is a list of "records" using
        name, type(A,CNAME, etc), data and ttl. The subdomains is a list of "domains" using name, comment 
        and emailAddress.  See api docs for examples.
        
        Arguments:
        name -- (Required)
        email -- (Required)
        attrDict: python dictionary:
            ttl -- (Optional)
            commment -- (Optional)
            #recordsList -- (Optional)
            #subdomains -- (Optional)
        returnResults -- True / False - receive the Async Json (True) or the Response Code (Optional)
        
        Returns: Depends on returnResults arg.
        """
        attrDict['name'] = name
        attrDict['emailAddress'] = email
        attrList = [attrDict]
        return self.createDomains(attrList, returnResults)
        
    def importDomain(self, contents, contentType="BIND_9"):
        """
        Import a new domain with the configuration specified by the request.  Currently "BIND_9" is the 
        only type supported and is defaulted to.
        
        Arguments:
        contentType --
        contents --
        
        Returns: 
        JSON results as a python dict
        """
        self.baseURL('domains/import')
        self.postKey = 'domains' 
        attrList = [{'contentType':contentType,'contents':contents}] 
        self.attrList = attrList
        self.postKeyListDict()
        return apiRequest(self, self.endpoint, "POST", self.data, returnResults=True)
        
    def updateDomains(self, domainList):
        """
        Update the configuration of a domain or domains.  This allows for updating of comments, ttl's or
        emailAddresses set on the domain.  Domain dict should include id and optionally comment, ttl and 
        emailAddress
        
        Arguments:
        domainList --
            id --
            emailAddress -- (Optional)
            ttl -- (Optional)
            comment -- (Optional)

        Returns:
        JSON results as a python dict
        """
        try:
            if len(domainList) > 1: #updating multiple
                self.baseURL('domains')
                self.postKey = 'domains' 
                self.postKeyListDict()
            else: #updating just 1
                self.baseURL('domains/'+str(domainList[0]['id']))
                del domainList[0]['id']
                self.attrDict = domainList[0]
                self.postDict()
            return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults=True)
        except:
            raise RSException("updateDomains")
            
    def updateDomain(self, domainId, domainDict={}):
        """
        Update the configuration of a domain.  This allows for updating of comments, ttl's or
        emailAddresses set on the domain.  Domain dict should include id and optionally comment, ttl and 
        emailAddress
        
        Arguments:
        domainId --
        domainList --
            email -- (Optional)
            ttl -- (Optional)
            comment -- (Optional)

        Returns:
        JSON results as a python dict
        """
        domainDict['id'] = domainId
        domainList = [domainDict]
        return self.updateDomains(domainList)
            
    def deleteDomain(self, domainId, deleteSubdomains=False, returnResults=False):
        """
        Remove domain from account.  Pass True to delete subdomains.
        
        Arguments:
        domainList -- list of domain ids to delete
        deleteSubdomains -- (Optional)
        returnResults -- True / False - receive the Async Json (True) or the Response Code (Optional)
        
        Returns: Depends on returnResults arg.
        """
        return self.deleteDomains([domainId],deleteSubdomains,returnResults)
        
    def deleteDomains(self, domainList, deleteSubdomains=False, returnResults=False):
        """
        Remove domain(s) from account.  Pass True to delete subdomains.
        
        Arguments:
        domainList -- list of domain ids to delete
        deleteSubdomains -- (Optional)
        returnResults -- True / False - receive the Async Json (True) or the Response Code (Optional)
        
        Returns: Depends on returnResults arg.
        """

        try:
            self.baseURL('domains')
            self.queryVar('id',str(domainList[0]))
            if len(domainList) > 1:
                for i in range(1,len(domainList)):
                    self.queryVar('id',str(domainList[i]))
            if deleteSubdomains:
                self.queryVar('deleteSubdomains','true')
            return apiRequest(self, self.endpoint, "DELETE", returnResults=returnResults)
        except:
            raise RSException("deleteDomain")

    #}}}
    #Subdomains{{{

    def getSubdomains(self, domainId):
        """
        List domains that are subdomains of the specified domain.
        
        Arguments:
        domainId --
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('domains/'+str(domainId)+'/subdomains')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    #}}}
    #Records{{{

    def getRecord(self, domainId, recordId=None):
        """
        List all records configured for the domain. SOA cannot be modified. Pass recordId to get 
        record details.
        
        Arguments:
        domainId --
        recordId --
        """
        if recordId is not None:
            self.baseURL('domains/'+str(domainId)+'/records/'+str(recordId))
        else:
            self.baseURL('domains/'+str(domainId)+'/records')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getRecords(self, domainId, recordType, attrDict={}): #name=None, data=None):
        """
        List all records for the specified domain of the specified type that match the specified 
        name and/or data.
        
        Arguments:
        domainId --
        recordType --
        attrDict: 
            name -- (Optional)
            data -- (Optional)
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('domains/'+str(domainId)+'/records')
        self.queryVar('type',recordType)
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createRecords(self, domainId, recordList,returnResults=False):
        """
        Add new record(s) to the specified domains in a "records" list with name, type and data required.
        
        Arguments:
        domainId -- Domain Id
        recordList -- Python List of Dictionaries:
            type -- Specifies the record type to add.
            name -- Specifies the name for the domain or subdomain. Must be a valid domain name.
            data -- The data field for PTR, A, and AAAA records must be a valid IPv4 or IPv6 IP address
            priority -- (MX and SRV records only) Must be an integer from 0 to 65535.
            ttl -- Must be greater than 300. Defaults to the domain TTL or 3600 (Optional)
            comment -- If included, its length must be less than or equal to 160 characters. (Optional)
        returnResults -- True / False - receive the Async Json (True) or the Response Code (Optional)
        
        Returns: Depends on returnResults arg.
        """
        self.baseURL('domains/'+str(domainId)+'/records')
        self.attrList = recordList
        self.postKey = 'records'
        self.postKeyListDict()
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=returnResults)
        
    def createRecord(self, domainId, type, name, data, recordDict={},returnResults=False):
        """
        Add new record to the specified domains in a "records" list with name, type and data required.
        
        Arguments:
        domainId -- Domain Id
        type -- Specifies the record type to add.
        name -- Specifies the name for the domain or subdomain. Must be a valid domain name.
        data -- The data field for PTR, A, and AAAA records must be a valid IPv4 or IPv6 IP address
        recordDict --
            priority -- (MX and SRV records only) Must be an integer from 0 to 65535.
            ttl -- Must be greater than 300. Defaults to the domain TTL or 3600 (Optional)
            comment -- If included, its length must be less than or equal to 160 characters. (Optional)
        returnResults -- True / False - receive the Async Json (True) or the Response Code (Optional)
        
        Returns: Depends on returnResults arg.
        """
        recordDict['type'] = type
        recordDict['name'] = name
        recordDict['data'] = data
        recordList = [recordDict]
        return self.createRecords(domainId,recordList,returnResults)
        
    def updateRecords(self, domainId, recordList):
        """
        Modify the configuration of records in the domain.
        
        Arguments:
        domainId -- Domain Id
        recordList -- 
            rId -- Record Id
            type -- Specifies the record type to add.
            name -- Specifies the name for the domain or subdomain. Must be a valid domain name.
            data -- The data field for PTR, A, and AAAA records must be a valid IPv4 or IPv6 IP address
            priority -- (MX and SRV records only) Must be an integer from 0 to 65535.
            ttl -- Must be greater than 300. Defaults to the domain TTL or 3600 (Optional)
            comment -- If included, its length must be less than or equal to 160 characters. (Optional)
        
        Returns:
        JSON results as python dict
        """
        
        try:
            if len(recordList) > 1:
                self.baseURL('domains/'+str(domainId)+'/records')
                self.postKey = 'records'
                self.attrList = recordList
                self.postKeyListDict()
            else:
                recordDict = recordList[0]
                self.baseURL('domains/'+str(domainId)+'/records/'+str(recordDict['id']))
                del recordDict['id']
                self.attrDict = recordDict
                self.postDict()
            return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults=True)
        except:
            raise RSException("updateRecord")
        
    def updateRecord(self, domainId, rId, recordDict):
        """
        Modify the configuration of records in the domain.
        
        Arguments:
        domainId -- Domain Id
        rId --  Record Id
        recordDict -- 
            type -- Specifies the record type to add.
            name -- Specifies the name for the domain or subdomain. Must be a valid domain name.
            data -- The data field for PTR, A, and AAAA records must be a valid IPv4 or IPv6 IP address
            priority -- (MX and SRV records only) Must be an integer from 0 to 65535.
            ttl -- Must be greater than 300. Defaults to the domain TTL or 3600 (Optional)
            comment -- If included, its length must be less than or equal to 160 characters. (Optional)
        
        Returns:
        JSON results as python dict
        """
        recordDict['id'] = rId
        #recordDict['type'] = type
        #recordDict['name'] = name
        recordList = [recordDict]
        return self.updateRecords(domainId,recordList) 
        
    def deleteRecords(self, domainId, recordIdList,returnResults=False):
        """
        Remove records from the domain.
        
        Arguments:
        domainId --
        recordIdList -- List containing record ids
        """
        try:
            if len(recordIdList) > 1:
                self.baseURL('domains/'+str(domainId)+'/records')
                for i in range(0,len(recordIdList)):
                    self.queryVar('id',recordIdList[i])
            else:
                self.baseURL('domains/'+str(domainId)+'/records/'+str(recordIdList[0]))
            return apiRequest(self, self.endpoint, "DELETE", returnResults=returnResults)
        except:
            raise RSException("deleteRecord")
        
    def deleteRecord(self, domainId, recordId, returnResults=False):
        """
        Remove a record from the domain.
        
        Arguments:
        domainId -- Domain Id
        recordId -- Record Id
        """
        recordIdList = [recordId]
        return self.deleteRecords(domainId,recordIdList,returnResults) 

    #}}}
    #Rdns{{{

    def getRdns(self, serviceType, deviceUri, recordId=None):
        """
        List all PTR records configured for a Rackspace Cloud device or details on a specified record.
        
        Arguments:
        serviceType -- Current available options are cloudServersOpenStack or cloudLoadBalancers
        deviceUri -- Device href for associated service
        recordId -- Id specified in ptr record listing
        
        Returns:
        JSON results as python dict
        """
        if recordId is None:
            endpoint = self.publicURL + "/rdns/%s?href=%s" % (str(serviceType), str(deviceUri))
        else:
            endpoint = self.publicURL + "/rdns/%s/%s?href=%s" % (str(serviceType), str(recordId), str(deviceUri))
        return apiRequest(self, endpoint, "GET", returnResults=True)
        
    def createRdns(self, recordList, serviceType, deviceUri):
        """
        Add new PTR record(s) for the specified Cloud device.
        
        Arguments:
        recordList -- { 'records': [ { 'name': required, 'type': 'PTR', 'data': required, 'ttl': optional } ] } etc
        serviceType -- cloudServersOpenStack or cloudLoadBalancers
        deviceUri -- Uri from service
        
        Returns:
        JSON result as python dict
        """
        data = { }
        endpoint = self.publicURL + "/rdns"
        data['recordsList'] = recordList
        data['link'] = { 'content': '', 'href':str(deviceUri), 'rel': str(deviceUri) }
        return apiRequest(self, endpoint, "POST", data, returnResults=True)
        
    def updateRdns(self, recordList, serviceType, deviceUri):
        """
        Modify existing PTR record(s) for specified Cloud device(s).
        
        Arguments:
        recordList -- { 'records': [ { 'name': required, 'id': required, 'type': 'PTR', 'data': required, 'ttl': optional } ] } etc
        serviceType -- cloudServersOpenStack or cloudLoadBalancers
        deviceUri -- Uri from service
        
        Returns:
        JSON result as python dict
        """
        #self.baseURL('rdns')
        data = { }
        endpoint = self.publicURL + "/rdns"
        data['recordsList'] = recordList
        data['link'] = { 'content': '', 'href':str(deviceUri), 'rel': str(deviceUri) }
        return apiRequest(self, self.endpoint, "PUT", data, returnResults=True)
        
    def deleteRdns(self, serviceType, deviceUri, ip=None):
        """
        Remove one or all PTR records associated with a Rackspace Cloud device. Use the optional ip query parameter to 
        specify a specific record to delete. Omitting this parameter removes all PTR records associated with the 
        specified device.
        
        Arguments:
        serviceType -- cloudServersOpenStack or cloudLoadBalancers
        deviceUri -- Uri from service
        ip -- Optional ipv4 or ipv6 addy
        
        Returns:
        status code
        """
        endpoint = self.publicURL + "/rdns/%s?href=%s" % (str(serviceType), str(deviceUri))
        if ip is not None:
            endpoint = endpoint + "&ip=%s" % str(ip)
        return apiRequest(self, endpoint, "DELETE")

    #}}}

    def getAsync(self, url, detail=False):
        """
        List status of the specified asynchronous request. Display details, as specified by the showDetails parameter.
        
        Arguments:
        url -- callbackUrl(string)
        detail -- (bool)
        
        Returns:
        JSON results as python dict
        """
        self.baseURL(url)
        self.queryVar('showDetails',str(detail))
        self.queryVar('showDetails',str('true'))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

#eof
