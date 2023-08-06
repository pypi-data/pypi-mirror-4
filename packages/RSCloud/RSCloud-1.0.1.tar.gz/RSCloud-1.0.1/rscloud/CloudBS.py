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

class CloudBS(Cloud):
    
    service = "BlockStorage"

    #Volumes {{{

    def createVolume(self, volume, size, attrDict={}):
        """
        Create a new volume.
        
        Arguments:
        volume -- display_name (ie: vol-001)
        size -- size of volume in GB (ie: 30)

        attrDict -- python list options:
            desc -- display_description
            snapID --  snapshot_id
            volumeType -- volume_type
        
        Returns: status code
        """
        
        self.postKey = 'volume'
        self.attrDict = attrDict
        self.baseURL('volumes')

        #required args
        self.postKeyVar('display_name',volume)
        self.postKeyVar('size',size)

        #optional attrDict args
        self.postKeyDictVar('display_name','name')
        self.postKeyDictVar('display_description','desc')
        self.postKeyDictVar('snapshot_id','snapID')
        self.postKeyDictVar('volume_type','volumeType')

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
         
    def getVolumes(self):
        """
        List all volumes.
        
        Arguments:

        Returns: JSON results as python dict
        """

        self.baseURL('volumes')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
        
    def getVolume(self, id):
        """
        Retrieve volume information.

        Arguments:
        id -- volume id

        Returns: JSON results as python dict
        """

        self.baseURL('volumes/'+str(id))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteVolume(self, id):
        """
        Remove a volume.
        
        Arguments:
        id -- volume id
        
        Returns: status code
        """
        self.baseURL('volumes/'+str(id))
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Volume Types {{{

    def getVolumeTypes(self):
        """
        List all volume types.
        
        Arguments:

        Returns: JSON results as python dict
        """

        self.baseURL('types')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getVolumeType(self, id):
        """
        Retrieve volume type information.

        Arguments:
        id --  volume type id

        Returns: JSON results as python dict
        """

        self.baseURL('types/'+str(id))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Snapshots {{{

    def createSnapshot(self, snapshot, vId, attrDict={}):
        """
        Create a new snapshot.
        
        Arguments:
        snapshot -- snapshot representational name
        vId -- volume id
        attrDict -- python list options:
            force -- (true/false) force a snapshot
            name -- display name
            desc -- display descriptioin
        
        Returns: status code
        """

        self.postKey = 'snapshot'
        self.attrDict = attrDict
        self.baseURL('snapshots')

        #required args
        self.postKeyVar('snapshot',snapshot)
        self.postKeyVar('volume_id',vId)

        #optional attrDict args
        self.postKeyDictVar('force','force')
        self.postKeyDictVar('display_name','name')
        self.postKeyDictVar('display_description','desc')

        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def getSnapshots(self):
        """
        List all snapshots.
        
        Arguments:

        Returns: JSON results as python dict
        """
        self.baseURL('snapshots')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getSnapshot(self, id):
        """
        Retrieve snapshot information.

        Arguments:
        id --  snapshot id

        Returns: JSON results as python dict
        """
        self.baseURL('snapshots/'+str(id))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteSnapshot(self, id):
        """
        Remove a snapshot.
        
        Arguments:
        id -- snapshot id
        
        Returns: status code
        """
        self.baseURL('snapshots/'+str(id))
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}

#eof
