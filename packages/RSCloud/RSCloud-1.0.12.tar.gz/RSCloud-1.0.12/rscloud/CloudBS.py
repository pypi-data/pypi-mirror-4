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
log = logging.getLogger(__name__)

class CloudBS(Cloud):
    
    service = "BlockStorage"

    #Volumes {{{

    def getVolumes(self,attrDict={}):
        """
        List all volumes.
        Arguments:
        attrDict -- python dictionary of arg options:
            limit -- when not specifed in the endpoint actually defaults to 100, we're setting default to 1000 (Optional)
            From -- query start date [*] (Optional)
            To -- query end date [*] (Optional)
            reverse -- enabled specifying that time sequenced data be returned in reverse order, default=False (Optional)
            marker -- used to mark query when retrieving info in subsequent queries (Optional)

        [*] These parameters take integer values, which are interpreted as timestamps expressed in milliseconds since 00:00:00 UTC on January 1, 1970. If the to value is not specified it defaults to the current time. Each time series collection specifies a default offset from the current time, which is used when the from value is not supplied. For example, if no to or from values are specified when retrieving an alarm history, then it will be treated as a query for the last 7 days of data.
        To convert a particular time to UTC, you can use the date +%s000 command or a website such as
            http://www.epochconverter.com/
        If no 'to' or 'from' values are specified, then it will be treated as a query for the last 7 days of data.

        Returns: JSON results as python dict
        """
        self.baseURL('volumes')
        self.attrDict = attrDict
        self.attrDictDefaultKeyVal('limit',1000)
        self.attrDictDefaultKeyVal('reverse',False)
        self.queryDict()
        log.info("getVolumes GET call to %s" % self.endpoint)
        return self.apiRequest(self.endpoint, "GET", returnResults=True)
        
    def getVolume(self, id):
        """
        Retrieve volume information.

        Arguments:
        id -- volume id

        Returns: JSON results as python dict
        """

        self.baseURL('volumes/'+str(id))
        log.info("getVolume GET call to %s" % (self.endpoint))
        return self.apiRequest(self.endpoint, "GET", returnResults=True)
        
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
        
        log.info("createVolume assigning Cloud vars")
        self.postKey = 'volume'
        self.attrDict = attrDict
        self.baseURL('volumes')

        log.info("createVolume assigning required vars")
        self.postKeyVar('display_name',volume)
        self.postKeyVar('size',size)

        log.info("createVolume assigning optional vars")
        self.postKeyDictVar('display_name','name')
        self.postKeyDictVar('display_description','desc')
        self.postKeyDictVar('snapshot_id','snapID')
        self.postKeyDictVar('volume_type','volumeType')

        log.info("createVolume POST call to %s with data - %s" % (self.endpoint, str(self.postData)))
        return self.apiRequest(self.endpoint, "POST", self.postData, returnResults=True)
         
    def deleteVolume(self, id):
        """
        Remove a volume.
        Arguments:
        id -- volume id
        Returns: status code
        """
        self.baseURL('volumes/'+str(id))
        log.info("deleteVolume DELETE call to %s" % (self.endpoint))
        #print self.endpoint
        return self.apiRequest(self.endpoint, "DELETE")

    # }}}
    #Volume Types {{{

    def getVolumeTypes(self):
        """
        List all volume types.
        
        Arguments:

        Returns: JSON results as python dict
        """

        self.baseURL('types')
        log.info("getVolumeTypes GET call to %s" % (self.endpoint))
        return self.apiRequest(self.endpoint, "GET", returnResults=True)
        
    def getVolumeType(self, id):
        """
        Retrieve volume type information.

        Arguments:
        id --  volume type id

        Returns: JSON results as python dict
        """

        self.baseURL('types/'+str(id))
        log.info("getVolumeType GET call to %s" % (self.endpoint))
        return self.apiRequest(self.endpoint, "GET", returnResults=True)

    # }}}
    #Snapshots {{{

    def getSnapshots(self,attrDict={}):
        """
        List all snapshots.
        Arguments:
        attrDict -- python dictionary of arg options:
            limit -- when not specifed in the endpoint actually defaults to 100, we're setting default to 1000 (Optional)
            From -- query start date [*] (Optional)
            To -- query end date [*] (Optional)
            reverse -- enabled specifying that time sequenced data be returned in reverse order, default=False (Optional)
            marker -- used to mark query when retrieving info in subsequent queries (Optional)

        [*] These parameters take integer values, which are interpreted as timestamps expressed in milliseconds since 00:00:00 UTC on January 1, 1970. If the to value is not specified it defaults to the current time. Each time series collection specifies a default offset from the current time, which is used when the from value is not supplied. For example, if no to or from values are specified when retrieving an alarm history, then it will be treated as a query for the last 7 days of data.
        To convert a particular time to UTC, you can use the date +%s000 command or a website such as
            http://www.epochconverter.com/
        If no 'to' or 'from' values are specified, then it will be treated as a query for the last 7 days of data.

        Returns: JSON results as python dict
        """
        self.baseURL('snapshots')
        self.attrDict = attrDict
        self.attrDictDefaultKeyVal('limit',1000)
        self.attrDictDefaultKeyVal('reverse',False)
        self.queryDict()
        log.info("getSnapshots GET call to %s" % (self.endpoint))
        return self.apiRequest(self.endpoint, "GET", returnResults=True)
        
    def getSnapshot(self, id):
        """
        Retrieve snapshot information.

        Arguments:
        id --  snapshot id

        Returns: JSON results as python dict
        """
        self.baseURL('snapshots/'+str(id))
        log.info("getSnapshot GET call to %s" % (self.endpoint))
        return self.apiRequest(self.endpoint, "GET", returnResults=True)
        
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

        log.info("createSnapshot assigning Cloud vars")
        self.postKey = 'snapshot'
        self.attrDict = attrDict
        self.baseURL('snapshots')

        log.info("createSnapshot assigning required args")
        self.postKeyVar('snapshot',snapshot)
        self.postKeyVar('volume_id',vId)

        log.info("createSnapshot assigning optional args")
        self.postKeyDictVar('force','force')
        self.postKeyDictVar('display_name','name')
        self.postKeyDictVar('display_description','desc')

        log.info("createSnapshot POST call to %s with data - %s" % (self.endpoint, str(self.postData)))
        return self.apiRequest(self.endpoint, "POST", self.postData, returnResults=True)
        
    def deleteSnapshot(self, id):
        """
        Remove a snapshot.
        
        Arguments:
        id -- snapshot id
        
        Returns: status code
        """
        self.baseURL('snapshots/'+str(id))
        log.info("deleteSnapshot DELETE call to %s" % (self.endpoint))
        return self.apiRequest(self.endpoint, "DELETE")

    # }}}

#eof
