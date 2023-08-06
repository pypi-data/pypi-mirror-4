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

class CloudServersFG(Cloud):
    
    service = "Servers"

    def getLimits(self):
        """
        Gets the current rate and absolute limits for your account.
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('limits') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        

    #Servers{{{

    def getServers(self, details=False, attrDict={}):
        """
        List all servers ([1]Without details = IDs + names only [2]With details = all details)
        
        Arguments:
        details -- true/false  
        """
        if details:
            self.baseURL('servers/detail') 
        else:
            self.baseURL('servers') 
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getServer(self, sId):
        """
        Fetch a specific server.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('servers/'+str(sId)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createServer(self, name, flavorId, imageId, attrDict={}):
        """
        Creates a server.
        
        Arguments:
        name --
        flavorId --
        imageId -- uuid(string)
        attrList -- Python dictionary options:
            metadata --
            personality --

        Returns:
        JSON results as python dict
        """
        self.baseURL('servers') 
        self.postKey = 'server'
        self.attrDict = attrDict

        #required args
        self.postKeyVar('name',name) 
        self.postKeyVar('imageId',imageId) 
        self.postKeyVar('flavorId',flavorId) 

        #optional args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def updateServer(self, sId, attrDict={}):
        """
        Updates the editable attributes for the specified server.
        
        Arguments:
        id -- Server uuid
        attrList -- python dictionary options:
            name --
            adminPass --
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('servers/'+str(sId)) 
        self.postKey = 'server'
        self.attrDict = attrDict
        self.postKeyDict()
        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteServer(self, sId):
        """
        Delete the specified server.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        status code
        """
        self.baseURL('servers/'+str(sId)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Server Addresses {{{

    def getAddresses(self, sId, network=None):
        """
        This operation lists all networks and addresses associated with a specified server.  Specify network for filtering.
        
        Arguments:
        sId -- Server uuid
        network -- Filter by network ie public, private
        
        Returns:
        JSON results as python dict
        """
        if network in ['private','public']:
            self.baseURL('servers/'+str(sId)+'/ips/'+str(network)) 
        else:
            self.baseURL('servers/'+str(sId)+'/ips') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def shareAddress(self, sId, addr, attrDict={}):
        """
        Shares an address to a specifies server.
        
        Arguments:
        sId -- Server uuid
        addr -- 
        attrDict -- python dict options:
            sharedIpGroupId --
            configureServer -- true/false
        
        Returns:
        JSON results as python dict
        """

        self.baseURL('servers/'+str(sId)+'/ips/public/'+str(addr)) 
        self.attrDict = attrDict
        self.postKey = 'shareIp'

        #option args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def unshareAddress(self, sId, addr):
        """
        Shares an address to a specifies server.
        
        Arguments:
        sId -- Server uuid
        addr -- 
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('servers/'+str(sId)+'/ips/public/'+str(addr)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Server Actions {{{    

    def _serverAction(self, sId, actionDict={}, returnResults=False):
        """
        Post requested action to api for included uuid.  
        
        Arguments:
        sId -- server uuid
        actionList -- dictionary containing action request info
        """
        self.baseURL('servers/'+str(sId)+'/action') 
        self.postData = actionDict
        if self.postData == {}:
            return apiRequest(self, self.endpoint, "POST", returnResults)
        else:
            return apiRequest(self, self.endpoint, "POST", self.postData, returnResults)
        
    def rebootServer(self, sId, rType="SOFT"):
        """
        Reboots the specified server.
        
        Arguments:
        sId -- server uuid
        rType -- HARD or SOFT(string)
        
        Returns:
        status code
        """
        data = { 'reboot': { 'type': rType.upper() } }
        return self._serverAction(sId, data)
        
    def rebuildServer(self, sId, iId):
        """
        Rebuilds the specified server.
        
        Arguments:
        sId -- server uuid
        iId -- image Id
        
        Returns:
        JSON results as python dict
        """
        data = {'rebuild': {'imageId':iId}}
        #return self._serverAction(sId, data, returnResults=True)
        return self._serverAction(sId, data)
        
    def resizeServer(self, sId, fId, diskConfig='AUTO'):
        """
        Resizes the specified server.
        
        Arguments:
        sId -- server uuid
        fId -- flavor Id
        
        Returns:
        status code
        """
        data = {'resize':{'flavorId':fId}}
        return self._serverAction(sId, data)
        
    def confirmResizeServer(self, sId):
        """
        Confirm a pending resize action.
        
        Arguments:
        sId -- server uuid
        
        Returns:
        status code
        """
        data = {'confirmResize': None}
        return self._serverAction(sId, data)
        
    def revertResizeServer(self, sId):
        """
        Cancels and reverts a pending resize action.
        
        Arguments:
        sId -- server uuid
        
        Returns:
        status code
        """
        data = {'revertResize':None}
        return self._serverAction(sId, data)

    # }}}
    #Flavors{{{

    def getFlavors(self, details=False):
        """
        Fetch info for  all available flavors. Specify details=True to get details.
        
        Arguments:
        details -- Bool, defaults to False.  
        
        Returns:
        JSON results as python dict
        """
        if details:
            self.baseURL('flavors/detail') 
        else:
            self.baseURL('flavors') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getFlavor(self, fId):
        """
        Fetch info for  all available flavors. Specify details=True to get details.
        
        Arguments:
        fId -- flavor Id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('flavors/'+str(fId)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Images{{{

    def getImages(self, details=False):
        """
        Fetch info for  all available images. Specify details=True to get details.
        
        Arguments:
        details -- Bool, defaults to False.  Specifying iId overrides this.
        
        Returns:
        JSON results as python dict
        """
        if details:
            self.baseURL('images/detail') 
        else:
            self.baseURL('images') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getImage(self, iId):
        """
        Fetch an image.
        
        Arguments:
        iId -- image id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('images/'+str(iId)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteImage(self, iId):
        """
        This operation deletes the specified image from the system.
        
        Arguments:
        iId -- image id
        
        Returns:
        status code
        """
        self.baseURL('images/'+str(iId)) 
        return apiRequest(self, self.endpoint, "DELETE")
        
    def createImage(self, sId, name):
        """
        Creates a new image.
        
        Arguments:
        sId -- server id
        name -- image name

        Returns:
        JSON results as python dict
        """

        self.baseURL('images') 
        self.postKey = 'image'

        #required vars
        self.postKeyVar('serverId',sId)
        self.postKeyVar('name',name)

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        

    # }}}
    #Backup Schedules{{{

    def getBSchedule(self, sId):
        """
        Lists the backup schedules for a specified server.
        
        Arguments:
        sId -- server id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('servers/'+str(sId)+'/backup_schedule') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setBSchedule(self, sId, attrDict={}):
        """
        Sets (creates/updates) the backup schedule for a specified server.
        
        Arguments:
        sId -- server id
        attrDict -- python dict options:
            enabled -- true/false
            weekly -- ie: SUNDAY
            daily -- ie: H_0400_0600

        Returns:
        JSON results as python dict
        """

        self.baseURL('servers/'+str(sId)+'/backup_schedule') 
        self.postKey = 'backupSchedule'
        self.attrDict = attrDict

        #optional args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def disableBSchedule(self, sId):
        """
        Disable the backup schedule a specified server.
        
        Arguments:
        sId -- server id
        
        Returns:
        status code
        """
        self.baseURL('servers/'+str(sId)+'/backup_schedule') 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Shared IP Groups{{{

    def getIPGroups(self, details=False):
        """
        Fetch all current shared IP groups. Toggle details (=True) for more informative results.
        
        Arguments:
        details -- Bool, defaults to False.  Specifying gId overrides this.
        
        Returns:
        JSON results as python dict
        """

        if details:
            self.baseURL('shared_ip_groups/detail') 
        else:
            self.baseURL('shared_ip_groups') 
            #self.baseURL('shared_ip_groups/detail') 

        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getIPGroup(self, gId):
        """
        List IDs and names for shared IP Groups. 
        Specify a gId for details on that IP group or 
        details=True for all details.
        
        Arguments:
        gId -- IP group id (Optional)
        details -- Bool, defaults to False.  Specifying gId overrides this.
        
        Returns:
        JSON results as python dict
        """

        self.baseURL('shared_ip_groups/'+str(gId)) 
        
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteIPGroup(self, gId):
        """
        Deletes a specified IP Group.
        
        Arguments:
        gId -- IP Group id
        
        Returns:
        status code
        """
        self.baseURL('shared_ip_groups/'+str(gId)) 
        return apiRequest(self, self.endpoint, "DELETE")
        
    def createIPGroup(self, gName, sId=None):
        """
        Create a shared IP group.
        
        Arguments:
        gName -- shared ip group name
        sId -- server id

        Returns:
        JSON results as python dict
        """

        self.baseURL('shared_ip_groups')
        self.postKey = 'sharedIpGroup'

        #required args
        self.postKeyVar('name',gName)
        self.postKeyVar('server',sId)

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)

    # }}}

#eof
