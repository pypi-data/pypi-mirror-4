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

class CloudLB(Cloud):
    
    service = "LoadBalancers"
   
    #Limits {{{

    def getLimits(self, absolute=False):
        """
        Return the current rate limits for the account.  Pass True to return absolute limits.
        
        Arguments:
        absolute -- Bool, set True for absolute limits.  Defaults to False
        
        Returns: JSON results as python dict
        """
        if absolute:
            self.baseURL('loadbalancers/absolutelimits.json') 
        else:
            self.baseURL('loadbalancers/limits.json') 

        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getAbsoluteLimits(self):
        """
        Return the current absolute limits for the account.  
        
        Arguments:
        absolute -- Bool, set True for absolute limits.  Defaults to False
        
        Returns: JSON results as python dict
        """
        return self.getLimits(True)

    # }}}
    #Load Balancers {{{

    def getLBs(self):
        """
        List all load balancers configured for the account (IDs, names and status only).  
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getLB(self, lbId):
        """
        Retrieve load balancer details.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createLB(self, name, port, nodes, protocol, virtualIps, attrDict={}):
        """
        Create a new load balancer with the configuration defined by the request.
        
        Arguments:
        name -- 
        port -- 
        nodes -- A list containing a dictionary for each with all of the following key/values:
            address -- IP address of node (Required)
            port -- Port number for the service you are load balancing on the node. (Required)
            condition -- ENABLED / DISABLED (Required)
            id -- Id of node (Optional)
            status -- ONLINE / OFFLINE (Optional)
        protocol -- HTTP / HTTPS / DNS / IMAPS / LDAP / MYSQL / POP3 / SMTP / TCP / UDP / SFTP etc.
        virtualIps -- A list containing a dictionary with any of the following key/values:
            type -- PUBLIC / PRIVATE (Required)
            address -- IP address of virtual IP (Optional)
            id -- Id of existing LB virtual ip. (Optional)
            ipVersion -- IPV4 / IPV6 (Optional)

        attrDict Options:
            accessList -- Network access controls to be applied to the load balancer's virtual IP address.
            algorithm -- Algorithm that defines how traffic should be directed between back-end nodes.
            connectionLogging -- Current connection logging configuration.
            connectionThrottle -- Limits on the number of connections per IP address
            healthMonitor -- The type of health monitor check to perform.
            metadata -- Information that can be associated with each load balancer for the client's personal use.
            port -- Port number for the service you are load balancing on the node.
            timeout --
            sessionPersistence -- Specifies whether multiple requests from clients are directed to the same node.

        Returns: status code
        """

        self.attrDict = attrDict
        self.postKey = 'loadBalancer'
        self.baseURL('loadbalancers')

        #req args
        self.postKeyVar('name',name)
        self.postKeyVar('nodes',nodes)
        self.postKeyVar('port',port)
        self.postKeyVar('protocol',protocol)
        self.postKeyVar('virtualIps',virtualIps)

        #optional attrDict args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def updateLB(self, lbId, attrDict={}):
        """
        Updates the attributes of the specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id

        attrDict Options:
            name -- Name of the load balancer to create
            protocol -- Protocol of the service which is being load balanced.
            algorithm -- Algorithm that defines how traffic should be directed between back-end nodes.
            port -- Port number for the service you are load balancing.
            connectionLogging -- true/false

        Returns: status code
        """

        self.attrDict = attrDict
        self.postKey = 'loadBalancer'
        self.baseURL('loadbalancers/'+str(lbId))

        #optional attrDict args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteLB(self, lbId):
        """
        Removes the specified load balancer and its associated configuration from the account.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId))
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Error Pages {{{

    def getErrorPage(self, lbId):
        """
        List error page configured for the specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as Python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/errorpage')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setErrorPage(self, lbId, content):
        """
        Set custom error page for the specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        contents -- HTML markup(string)
        
        Returns: response code
        """
        self.postKey = 'errorpage'
        self.baseURL('loadbalancers/'+str(lbId)+'/errorpage')
        self.postKeyVar('content',content)
        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteErrorPage(self, lbId):
        """
        Delete custom error page for the specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/errorpage')
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}        
    #Stats {{{

    def getStats(self, lbId):
        """
        Provides detailed stats output of specified LB.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/stats.json')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Nodes {{{

    def getNode(self, lbId, nId):
        """
        List a specific node per a specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        nId -- Node id
        
        Returns: JSON results as python dict
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/nodes/'+str(nId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getNodes(self, lbId):
        """
        List nodes per a specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        nId -- Node id
        
        Returns: JSON results as python dict
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/nodes')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createNode(self, lbId, attrList=[]):
        """
        Add a node to a specified load balancer.
        
        Arguments:
        lbId -- load balancer id 

        attrList -- python list of dict options:
            address -- IP address or domain name for the node.(Required)
            condition -- Condition for the node.  ENABLED / DISABLED / DRAINING (Required)
            port -- Port number for the service you are load balancing.(Required)
            type -- Type of node to add: PRIMARY / SECONDARY (Optional)
            weight -- Weight of node to add. Must be an integer from 1 to 100.(Optional)
        
        Returns: status code
        """

        self.attrList = attrList
        self.postKey = 'nodes'
        self.baseURL('loadbalancers/'+str(lbId)+'/nodes')

        #attrDict args (required+optional)
        self.postKeyListDict()

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def updateNode(self, lbId, nId, attrDict):
        """
        Modify a node per a specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        nId -- Node id

        attrDict Options:
            condition -- Condition for the node.  ENABLED / DISABLED / DRAINING
            type -- Type of node to add: PRIMARY / SECONDARY
            weight -- Weight of node to add. Must be an integer from 1 to 100.
        
        Returns: status code
        """

        self.attrDict = attrDict
        self.postKey = 'node'
        self.baseURL('loadbalancers/'+str(lbId)+'/nodes/'+str(nId))
        
        #optional attrDict args (at least one req)
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteNode(self, lbId, nodeList=[]):
        """
        Remove node(s) per a specified load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        nodeList -- Python list containing nodes to delete.
        
        Returns: status code
        """
        if len(nodeList) == 1:
            self.baseURL('loadbalancers/'+str(lbId)+'/nodes/'+str(nodeList[0]))
        if len(nodeList) > 1:
            self.baseURL('loadbalancers/'+str(lbId)+'/nodes')
            for node in nodeList:
                self.queryVar('id',str(node))
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Virtual IP's {{{

    def getVirtualIPs(self, lbId):
        """
        List all virtual IPs associated with a load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/virtualips/')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getVirtualIP(self, lbId, vpId):
        """
        List a specific virtual IP associated with a load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        vpId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/virtualips/'+str(vpId))
        endpoint = self.publicURL + "/loadbalancers/%s/virtualips/%s" % (str(lbId),str(vpId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Allowed Domains {{{

    def getAllowedDomains(self):
        """
        List all allowed domains.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/alloweddomains')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createVirtualIP(self, lbId, typeIp, ipVersion='IPV6'):
        """
        Create a new virtual IP (v.6) with the configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        typeIp -- PUBLIC/SERVICENET 
        ipVersion -- IPV6 
        
        Returns: status code
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/virtualips')

        #required args
        self.postVar('type',typeIp)
        self.postVar('ipVersion',ipVersion)

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def deleteVirtualIP(self, lbId, vipList=[]):
        """
        Remove virtual ip(s) from the load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        vipList -- Python list containing virtual Ip's to delete. 
        
        Returns: status code
        """

        if len(vipList) == 1:
            self.baseURL('loadbalancers/'+str(lbId)+'/virtualips/'+str(vipList[0]))
        if len(vipList) > 1:
            self.baseURL('loadbalancers/'+str(lbId)+'/virtualips')
            for vip in vipList:
                self.queryVar('id',str(vip))

        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Usage {{{

    def getBillable(self, startTime, endTime, offset=None, limit=None):
        """
        List paginated billable load balancers.
        
        Arguments:
        startTime -- start date; format is YYYY-MM-DD 
        endTime -- end date; format is YYYY-MM-DD
        offset -- (Optional)
        limit -- (Optional)

        Returns: JSON results as python dict
        """

        self.baseURL('loadbalancers/billable')
        self.queryVar('startTime',startTime)
        self.queryVar('endTime',endTime)
        if offset:
            self.queryVar('offset',offset)
        if limit:
            self.queryVar('limit',limit)

        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getUsage(self, lbId=None, startTime=None, endTime=None, offset=None, limit=None):
        """
        List types of usage statistics (transfer activity, average number of
        connections, virtual IP count) over a date range or last 24 hours ("current").
        
        Arguments:
        lbId -- load balancer id (Optional)
        startTime -- start date; format is YYYY-MM-DD (Optional, if not set then current=true with lbId) 
        endTime -- end date; format is YYYY-MM-DD (Optional, if not set then current=true with lbId) 
        offset -- (Optional)
        limit -- (Optional)

        Returns: JSON results as python dict
        """

        if (startTime==None or endTime==None) and lbId is not None:
            self.baseURL('loadbalancers/'+str(lbId)+'/usage/current')
        else:
            self.baseURL('loadbalancers/usage')
            self.queryVar('startTime',startTime)
            self.queryVar('endTime',endTime)
        if offset:
            self.queryVar('offset',offset)
        if limit:
            self.queryVar('limit',limit)

        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Access Lists {{{

    def getAccessList(self, lbId):
        """
        List all access list associated with a load balancer.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/accesslist')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createAccessList(self, lbId, ipList=[]):
        """
        Create a new access list with the configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        ipList -- python list of dictionary key/value args:
            address -- ip address for item to add 
            alType -- ALLOW / DENY 

        Returns: status code
        """

        self.postKey = 'accessList'
        self.baseURL('loadbalancers/'+str(lbId)+'/accesslist') 
        self.attrList = ipList

        #required args
        self.postKeyListDict()

        return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def updateAccessList(self, lbId, ipList=[]):
        """
        Update an access list with the configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        ipList -- python list of dictionaries with these required args:
            address -- ip address for item to add 
            type -- ALLOW / DENY 

        Returns: status code
        """
        return self.createAccessList(lbId,ipList)
        
    def deleteAccessList(self, lbId):
        """
        Remove access list from the load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/accesslist')
        return apiRequest(self, self.endpoint, "DELETE")
        
    def deleteAccessListNetworkItems(self, lbId, ipList=[]):
        """
        Remove network item(s) from a load balancer's access list.
        
        Arguments:
        lbId -- Load Balancer id
        ipList -- Python list containing network item id's to delete. 
        
        Returns: status code
        """

        if len(ipList) == 1:
            self.baseURL('loadbalancers/'+str(lbId)+'/accesslist/'+str(ipList[0]))
        if len(ipList) > 1:
            self.baseURL('loadbalancers/'+str(lbId)+'/accesslist')
            for ipItm in ipList:
                self.queryVar('id',str(ipItm))

        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Monitor Health {{{

    def getMonitorHealth(self, lbId):
        """
        Retrieve health monitor configuration (if one exists). 
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/healthmonitor')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteMonitorHealth(self, lbId):
        """
        Remove health monitor from the load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/healthmonitor')
        return apiRequest(self, self.endpoint, "DELETE")
        
    def updateMonitorHealthConn(self, lbId, attempts, delay, timeout, type):
        """
        Update Health Monitor connections with the configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        attempts -- attempts before deactivation 
        delay --
        timeout -- 
        type -- 

        Returns: status code
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/healthmonitor')

        #required args
        self.postVar('attemptsBeforeDeactivation',attempts)
        self.postVar('delay',delay)
        self.postVar('timeout',timeout)
        self.postVar('type',type)

        return apiRequest(self, self.endpoint, "PUT", self.postData)
    def updateMonitorHealthHttp(self, lbId, attempts, bRegex, delay, path, sRegex, timeout, type, hostHeader=None):
        """
        Update Health Monitor HTTP/HTTPS with the configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        attempts -- attempts before deactivation 
        bRegex -- bodyRegex
        delay -- 
        path -- 
        sRegex -- statusRegex
        timeout -- 
        type -- 
        hostHeader -- 

        Returns: status code
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/healthmonitor')

        #required args
        self.postVar('attemptsBeforeDeactivation',attempts)
        self.postVar('bodyRegex',bRegex)
        self.postVar('delay',delay)
        self.postVar('path',path)
        self.postVar('statusRegex',sRegex)
        self.postVar('timeout',timeout)
        self.postVar('type',type)
        self.postVar('hostHeader',hostHeader)

        return apiRequest(self, self.endpoint, "PUT", self.postData)

    # }}}
    #Sessions {{{

    def getSession(self, lbId):
        """
        Retrieve session persistence configuration.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/sessionpersistence') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def updateSession(self, lbId, type):
        """
        Update session persistence with the configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        type -- persistence type - HTTP_COOKIE / SOURCE_IP 

        Returns: status code
        """

        self.postKey = 'sessionPersistence'
        self.baseURL('loadbalancers/'+str(lbId)+'/sessionpersistence') 

        #required args
        self.postKeyVar('persistenceType',type)

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteSession(self, lbId):
        """
        Disable session persistence from the load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/sessionpersistence') 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Connections {{{

    def getConnection(self, lbId):
        """
        Retrieve connection logging configuration.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/connectionlogging') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setConnection(self, lbId, enabled):
        """
        Enable/disable connection logging.
        
        Arguments:
        lbId -- Load Balancer id 
        enabled -- true / false  

        Returns: status code
        """

        self.postKey = 'connectionLogging'
        self.baseURL('loadbalancers/'+str(lbId)+'/connectionlogging') 

        #required vars
        self.postKeyVar('enabled',enabled)

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def getConnectionThrottle(self, lbId):
        """
        Retrieve connection throttle configuration.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/connectionthrottle') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def updateConnectionThrottle(self, lbId, attrDict={}):
        """
        Update connection throttle configuration defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        attrDict -- python dict options:
            maxConnectionRate -- (Optional)
            maxConnections -- (Optional)
            minConnections -- (Optional)
            rateInterval -- (Optional)

        Returns: status code
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/connectionthrottle') 
        self.attrDict = attrDict

        #attrDict optional args
        self.postDict()    

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteConnectionThrottle(self, lbId):
        """
        Remove connection throttle configuration from the load balancer.
        
        Arguments:
        lbId -- Load Balancer id (Required)
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/connectionthrottle') 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Content Caching {{{

    def getContentCaching(self, lbId):
        """
        Retrieve content caching configuration.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/contentcaching') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setContentCaching(self, lbId, enabled):
        """
        Enable/disable content caching.
        
        Arguments:
        lbId -- Load Balancer id 
        enabled -- true / false 

        Returns: status code
        """

        self.baseURL('loadbalancers/'+str(lbId)+'/contentcaching') 
        self.postKey = 'contentCaching'

        #required args
        self.postKeyVar('enabled',enabled)

        return apiRequest(self, self.endpoint, "PUT", self.postData)

    # }}}
    #Protocols {{{

    def getProtocols(self):
        """
        List supported load balancing protocols.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/protocols') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Algorithms {{{

    def getAlgorithms(self):
        """
        List supported load balancing algorithms.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/algorithms') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #SSL Termination {{{

    def getSSLTermination(self, lbId):
        """
        List load balancers SSL termination configuration.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: JSON results as python dict
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/ssltermination') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setSSLTermination(self, lbId, attrDict):
        """
        Update/configure SSL termination.
        
        Arguments:
        lbId -- Load Balancer id 

        attrDict -- python dictionary options:
            securePort --  (Required)
            privatekey -- (Required)
            certificate --  (Required)
            intermediatecertificate -- (Required for intermediate SSL Termination)
            enabled -- true / false  (Optional)
            secureTrafficOnly -- true / false (Optional)
        
        Returns: status code
        """

        self.postKey = 'sslTermination'
        self.baseURL('loadbalancers/'+str(lbId)+'/ssltermination') 
        self.attrDict = attrDict

        self.postKeyDict()

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteSSLTermination(self, lbId):
        """
        Remote SSL Termination.
        
        Arguments:
        lbId -- Load Balancer id
        
        Returns: status code
        """
        self.baseURL('loadbalancers/'+str(lbId)+'/ssltermination') 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Metadata {{{

    def getMetadata(self, lbId, metaId=None, nodeId=None):
        """
        Retrieve metadata associated with load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        metaId -- Meta id (Optional)
        nodeId -- Node id (Optional)
        
        Returns: JSON results as python dict
        """

        self.postKey = 'metadata'

        if nodeId is not None:
            req = 'loadbalancers/'+str(lbId)+'/nodes/'+str(nodeId)+'/metadata'
        else:
            req = 'loadbalancers/'+str(lbId)+'/metadata'

        if metaId is not None:
            self.baseURL(req+'/'+str(metaId))
        else:
            self.baseURL(req)

        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createMetadata(self, lbId, metaList=[], nodeId=None):
        """
        Create metadata per a load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        nodeId -- (Optional)
        metaList -- python list of meta key/value dictionaries:
            key -- 
            value --

        Returns: status code
        """

        self.postKey = 'metadata'
        self.attrList = metaList

        if nodeId is not None:
            self.baseURL('loadbalancers/'+str(lbId)+'/nodes/'+str(nodeId)+'/metadata')
        else:
            self.baseURL('loadbalancers/'+str(lbId)+'/metadata')

        #required metaList args
        self.postKeyListDict()

        return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def updateMetadata(self, lbId, metaId, value, nodeId=None):
        """
        Update metadata per a load balancer (and optionally with a node) defined by the request.
        
        Arguments:
        lbId -- Load Balancer id 
        metaId -- Meta id 
        value -- 
        nodeId -- Node id (Optional)

        Returns: status code
        """

        self.postKey = 'meta'

        if nodeId is not None:
            self.baseURL('loadbalancers/'+str(lbId)+'/nodes/'+str(nodeId)+'/metadata/'+str(metaId))
        else:
            self.baseURL('loadbalancers/'+str(lbId)+'/metadata/'+str(metaId))

        #required args
        self.postKeyVar('value',value)

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteMetadata(self, lbId, metaIdList, nodeId=None):
        """
        Remove metadata per a load balancer.
        
        Arguments:
        lbId -- Load Balancer id 
        metaIdList -- Python list containing metadata id's to delete. 
        nodeId -- Node id (Optional)
        
        Returns: status code
        """

        self.postKey = 'metadata'

        if nodeId is not None:
            req = 'loadbalancers/'+str(lbId)+'/nodes/'+str(nodeId)+'/metadata'
        else:
            req = 'loadbalancers/'+str(lbId)+'/metadata'
        if len(metaIdList) == 1:
            self.baseURL(req+'/'+str(metaIdList[0]))
        else:
            self.baseURL(req)
            for metaId in metaIdList:
                self.queryVar('id',str(metaId))

        return apiRequest(self, self.endpoint, "DELETE")

    # }}}

#eof
