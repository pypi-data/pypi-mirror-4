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

class CloudServersNG(Cloud):
    
    service = "ServersOpenStack"

    def getLimits(self):
        """
        Gets the current rate and absolute limits for your account.
        
        Returns:
        JSON results as python dict
        
        """
        endpoint = self.publicURL + "/limits"
        return apiRequest(self, endpoint, "GET", returnResults=True)
        
    def getExtensions(self, extension=None):
        """
        List available extensions and get details for a specific extension.
        
        Arguments:
        extension -- alias of extension(string)
        
        Returns:
        JSON results as python dict
        
        """
        
        endpoint = self.publicURL + "/extensions"
        
        if extension is not None:
            endpoint = endpoint + "/%s" % unicode(quote(str(extension)), 'utf-8')
            
        return apiRequest(self, endpoint, "GET", returnResults=True)

    #Servers{{{

    def getServer(self, sId):
        """
        Fetch a server's details.
        This operation returns the details of a specified server.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('servers/'+str(sId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getServers(self, details=False, attrDict={}):
        """
        Fetch servers. Use details=True for all details. Use attrDict to filter results.
        
        Arguments:
        details -- bool, defaults to False
        attrDict Options:
            image -- The image ID (Optional)
            flavor -- The flavor ID (Optional)
            name -- The server name. (Optional)
            status -- The server status. (Optional)
            marker -- The ID of the last item in the previous list. (Optional)
            limit -- The page size. (Optional)
            changes-since --The changes-since time.
        """
        if details:
            self.baseURL('servers/detail') 
        else:
            self.baseURL('servers') 
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createServer(self, name, flavorRef, imageRef, attrDict={}):
        """
        This operation asynchronously provisions a new server.
        
        Arguments:
        name --
        flavorRef --
        imageRef -- uuid(string)
        attrDict -- Optional dictionary containing OS-DCF:diskConfig, metadata, personality or accessIPv[4,6]
        
        Returns:
        JSON results as python dict
        """

        self.postKey='server'
        self.baseURL('servers')
        self.attrDict = attrDict

        #required args
        self.postKeyVar('name',name)
        self.postKeyVar('flavorRef',flavorRef)
        self.postKeyVar('imageRef',imageRef)

        #optional attrDict args
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def setServerAttr(self, sId, attrDict):
        """
        This operation updates the editable attributes of a specified server.
        
        Arguments:
        id -- Server uuid
        attrDict -- dictionary containing name, accessIPv[4,6] updates
        
        Returns:
        JSON results as python dict
        """

        self.postKey='server'
        self.baseURL('servers/'+str(sId))
        self.attrDict = attrDict

        #optional attrDict args (1 of which is required)
        self.postKeyDict()
        
        return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults=True)
        
    def deleteServer(self, sId):
        """
        This operation deletes a specified server instance from the system.
        
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
        This operation lists all networks and addresses associated with a specified server.  Specify network for 
        filtering
        
        Arguments:
        sId -- Server uuid
        network -- Filter by network ie public, private
        
        Returns:
        JSON results as python dict
        
        """
        endpoint = self.publicURL + "/servers/%s/ips" % str(sId)
        if network is not None:
            endpoint = endpoint + "/%s" % str(network)
        return apiRequest(self, endpoint, "GET", returnResults=True)

    # }}}
    #Server Actions {{{    

    def _setAction(self, sId, actionList, returnResults=False):
        """
        Post requested action to api for included uuid.  
        
        Arguments:
        sId -- Server uuid
        actionList -- dictionary containing action request info
        """
        self.baseURL('servers/'+str(sId)+'/action')
        self.postData = actionList
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults)
        
    def changePass(self, sId, adminPass):
        """
        This operation changes the administrator password for a specified server.
        
        Arguments:
        sId -- Server uuid
        adminPass -- new password
        
        Returns:
        status code
        """
        actionList = { 'changePassword': { 'adminPass': adminPass } }
        return self._setAction(sId, actionList)
        
    def rebootServer(self, sId, rType="SOFT"):
        """
        This operation performs a soft or hard reboot of a specified server. A soft reboot is a graceful 
        shutdown and restart of your server's operating system. A hard reboot power cycles your server, 
        which performs an immediate shutdown and restart.
        
        Arguments:
        sId -- Server uuid
        rType -- HARD or SOFT(string)
        
        Returns:
        status code
        """
        actionList = { 'reboot': { 'type': rType.upper() } }
        return self._setAction(sId, actionList)
        
    def rebuildServer(self, sId, name, flavorRef, imageRef, attrDict=None):
        """
        The rebuild operation removes all data on the server and replaces it with the specified image. The 
        serverRef and all IP addresses remain the same. If you specify name, metadata, accessIPv4, or accessIPv6 
        in the rebuild request, new values replace existing values. Otherwise, these values do not change.
        
        Arguments:
        sId -- Server uuid
        name -- Server name(string)
        flavorRef -- flavor number(string)
        imageRef -- uuid(string) 
        attrDict -- Optional dictionary containing OS-DCF:diskConfig, metadata, personality or accessIPv[4,6]
        
        Returns:
        JSON results as python dict
        """
        data = { 'rebuild': { 'name': str(name), 'flavorRef': str(flavorRef), 'imageRef': str(imageRef) } }
        if attrDict is not None:
            data = { 'servers': dict( data['servers'].items() + attrDict.items() ) }
        return self._setAction(sId, data, returnResults=True)
        
    def resizeServer(self, sId, flavorRef, diskConfig='AUTO'):
        """
        This operation converts an existing server to a different flavor, which scales the server up or down. The 
        original server is saved for a period of time to allow roll back if a problem occurs. You should test and 
        explicitly confirm all resizes. When you do so, the original server is removed. All resizes are automatically 
        confirmed after 24 hours if you do not explicitly confirm or revert the resize.
        
        Arguments:
        sId -- Server uuid
        flavorRef -- flavor id (string)
        diskConfig -- AUTO or MANUAL(string) OS-DCF:diskConfig
        
        Returns:
        status code
        """
        data = { 'resize': { 'flavorRef': str(flavorRef) } }
        if diskConfig.upper() == "MANUAL":
            data['resize']['OS-DCF:diskConfig'] = "MANUAL"
        return self._setAction(sId, data)
        
    def confirmResizeServer(self, sId):
        """
        After you verify that the newly resized server works properly, use this operation to confirm the resize. After 
        you confirm the resize, the original server is removed and you cannot roll back to that server. All resizes are 
        automatically confirmed after 24 hours if you do not explicitly confirm or revert the resize.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        status code
        """
        data = { 'confirmResize': None }
        return self._setAction(sId, data)
        
    def revertResizeServer(self, sId):
        """
        Use this operation to revert the resize and roll back to the original server. All resizes are automatically 
        confirmed after 24 hours if you do not explicitly confirm or revert the resize.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        status code
        """
        data = { 'revertResize': None }
        return self._setAction(sId, data)
        
    def rescueServer(self, sId):
        """
        A temporary root password is assigned for use during rescue mode. This password is returned in the response body 
        for this call.  Rescue mode is limited to 90 minutes, after which the rescue image is destroyed and the server 
        attempts to reboot. You can exit rescue mode at any time.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        JSON results as python dict
        """
        data = { 'rescue': None }
        
        return self._setAction(sId, data, returnResults=True)
        
    def unrescueServer(self, sId):
        """
        After you resolve any problems and reboot a rescued server, you can unrescue the server. When you unrescue the server, 
        the repaired image is restored to its running state with your original password.
        
        Arguments:
        sId -- Server uuid
        
        Returns:
        JSON results as python dict
        """
        data = { 'unrescue': None }
        return self._setAction(sId, data)
        
    def createImage(self, sId, name, metaDict=None):
        """
        This operation creates a new image for a specified server. Once complete, a new image is available that you can use to 
        rebuild or create servers.
        
        Arguments:
        sId -- Server uuid
        name -- Image name(string)
        metaDict -- dictionary containing metadata key/value pairs.(Optional)
        
        Returns:
        status code
        """
        data = {'createImage': {'name':str(name)}}
        if metaDict is not None:
            data['createImage']['metadata'] = metaDict
        return self._setAction(sId, data)

    # }}}
    #Volume Attachment Actions {{{

    def createAttVolume(self, sId, volumeList):
        """
        This operation attaches one or more volumes to the specified server.
        
        Arguments:
        sId -- Server uuid
        volumeList -- dictionary containing volumeId and device keys.
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('servers/'+str(sId)+'/os-volume-attachments')
        #endpoint = self.publicURL + "/servers/%s/os- volume_attachments" % str(sId)
        self.postVar('volumentAttachment',{volumeList})
        self.postData = { 'volumeAttachment': { volumeList } }
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def getAttVolumes(self, sId, vId=None):
        """
        This operation returns a response body that lists the volume attachment(s) for the specified server.
        
        Arguments:
        sId -- Server uuid
        vId -- Volume attachment id(Optional)
        
        Returns:
        JSON results as python dict
        """
        #endpoint = self.publicURL + "/servers/%s/os-volume_attachments" % str(sId)
        if vId is not None:
            self.baseURL('servers/'+str(sId)+'/os-volume-attachments/'+str(vId))
            #endpoint = endpoint + "/%s" % str(vId)
        else:
            self.baseURL('servers/'+str(sId)+'/os-volume-attachments')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteAttVolume(self, sId, vId):
        """
        This operation deletes a specified volume attachment from a specified server instance.
        
        Arguments:
        sId -- Server uuid
        vId -- Volume attachment id
        
        Returns:
        status code
        """
        self.baseURL('servers/'+str(sId)+'/os-volume-attachments/'+str(vId))
        #endpoint = self.publicURL + "/servers/%s/os-volume_attachments/%s" % (str(sId), str(vId))
        return apiRequest(self, self.endpoint,"DELETE")

    # }}}
    #Flavors{{{

    def getFlavor(self, fId):
        """
        Fetch a flavor's details.
        
        Arguments:
        fId -- Flavor id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('flavors/'+str(fId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getFlavors(self, details=False, attrDict=None):
        """
        Fetch flavors. Use details=True for all details. Use attrDict to filter results.
        
        Arguments:
        details -- Bool, defaults to False.  Specifying fId overrides this.
        attrDict -- Python dict containing any of the following:
            minDisk -- Minimum number of gigabytes of disk storage.
            minRam -- Minimum amount of RAM in megabytes.
            marker -- The ID of the last item in the previous list.
            limit -- Sets the page size.
        
        Returns:
        JSON results as python dict
        """
        if details:
            self.baseURL('flavors/details') 
        else:
            self.baseURL('flavors') 
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Images{{{

    def getImage(self, iId):
        """
        Fetch an image's details.
        
        Arguments:
        iId -- Image id
        
        Returns:
        JSON results as python dict
        """
        self.baseURL('images/'+str(iId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getImages(self, details=False, attrDict=None):
        """
        Fetch images. Use details=True for all details. Use attrDict to filter results.
        
        Arguments:
        details -- Bool, defaults to False.  Specifying iId overrides this.
        attrDict -- Python dict containing any of the following:
            server -- Specify the server reference by ID or by full URL.
            name -- Filters the list of images by image name.
            status -- Filters the list of images by status.
            changes-since -- Filters the list of images to those that have changed since the changes-since time.
            marker -- The ID of the last item in the previous list.
            limit -- Sets the page size. 
            type -- {BASE|SERVER}
        
        Returns:
        JSON results as python dict
        """
        if details:
            self.baseURL('images/detail') 
        else:
            self.baseURL('images') 
        self.attrDict = attrDict
        self.queryDict()
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteImage(self, iId):
        """
        This operation deletes the specified image from the system.
        
        Arguments:
        iId -- Image id
        
        Returns:
        status code
        """
        self.baseURL('images/'+str(iId))
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Metadata{{{

    def getMeta(self, mType, mId, key=None):
        """
        Lists metadata associated with a server/image or specified key.
        
        Arguments:
        mType -- servers / images
        mId -- Server or Image uuid
        key -- metadata key(optional)
        
        Returns:
        JSON response as python dict
        """
        if key is not None:
            self.baseURL(mType.lower()+'/'+str(mId)+'/metadata/'+str(key)) 
        else:
            self.baseURL(mType.lower()+'/'+str(mId)+'/metadata') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def setMeta(self, mType, mId, metaDict, key=None):
        """
        Sets metadata for the specified server or image.  If no key is provided, this will replace all existing
        metadata with the provided metaDict key/value pairs.  If a key is provided, the list must contain that 
        key/value pair and only that one will get set.
        
        Arguments:
        mType -- servers / images
        mId -- Server or Image uuid
        metaDict -- Python dictionary containing key/value pairs to be added/replaced.
        key -- metadata key
        
        Returns:
        JSON results as python dict
        """

        if key is not None:
            self.baseURL(mType.lower()+'/'+str(mId)+'/metadata/'+str(key)) 
            self.postKey = 'meta'
            self.postKeyVar(str(key),metaDict[str(key)])
        else:
            self.baseURL(mType.lower()+'/'+str(mId)+'/metadata') 
            self.postVar('metadata',metaDict)

        return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults=True)
        
    def updateMeta(self, mType, mId, metaList):
        """
        Updates metadata items for specified server or image.  Items that are not explicitly mentioned are not modified.
        
        Arguments:
        mType -- servers / images
        mId -- Server or Image uuid
        metaList -- Python dictionary containing key/value pairs to be udpated.
        
        Returns:
        JSON results as python dict
        """
        self.baseURL(mType.lower()+'/'+str(mId)+'/metadata') 
        self.postVar('metadata',metaList)
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def deleteMeta(self, mType, mId, key):
        """
        Deletes a metadata item.
        
        Arguments:
        mType -- servers / images
        mId -- Server or Image uuid
        key -- Metadata key to delete
        
        Returns:
        status code
        """
        self.baseURL(mType.lower()+'/'+str(mId)+'/metadata/'+str(key)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}

#eof
