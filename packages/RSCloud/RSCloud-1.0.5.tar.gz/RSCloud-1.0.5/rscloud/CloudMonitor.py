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

class CloudMonitor(Cloud):
    
    service = "Monitoring"
            
    #Account {{{

    def getAccount(self):
        """
        Returns account information.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('account') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def updateAccount(self, metaDict={}, token=None):
        """
        Update properties on an account.
        
        Arguments:
        metaDict - metadata key-value pairs in form of python dictionary (Optional)
        token -- webhook token (Optional)
        
        Returns: status code
        """

        self.baseURL('account') 
        self.attrDict = metaDict
        self.postKey = 'metadata'

        #optional args
        self.postVar('webhook_token',token)
        self.postKeyDict()

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def getLimits(self):
        """
        Returns account resource limits.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('limits') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getAudits(self):
        """
        Lists audits for this account.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('audits') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Entities {{{

    def getEntities(self):
        """
        Lists the entities for this particular account.
        
        Arguments:
        
        Returns: JSON results as python dict
        
        """
        endpoint = self.publicURL + "/entities"
        return apiRequest(self, endpoint, "GET", returnResults=True)
        
    def getEntity(self, eId):
        """
        Retrieves the current state of an entity.
        
        Arguments:
        eId -- entity id

        Returns: JSON results as python dict
        """
        self.baseURL('entities/'+str(eId)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def createEntity(self, label, attrDict={}):
        """
        Creates a new entity.
        
        Arguments:
        label -- 
        attrDict -- python dictionary of arg options:
            agent_id --  (Optional)
            ip_addresses - ip's in form of python dictionary (Optional)
            metadata - metadata key-value pairs in form of python dictionary (Optional)
        
        Returns: status code
        """
        
        self.baseURL('entities') 
        self.attrDict = attrDict

        #required args
        self.postVar('label',label)

        #optional args
        self.postDict()

        return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def updateEntity(self, eId, label, attrDict={}):
        """
        Updates an entity specified by the entityId (id).
        
        Arguments:
        eId -- entity id
        label -- (Optional)
        attrDict -- python dictionary of arg options:
            agent_id --  (Optional)
            ip_addresses - ip's in form of python dictionary (Optional)
            metadata - metadata key-value pairs in form of python dictionary (Optional)
        
        Returns: status code
        """

        self.baseURL('entities/'+str(eId)) 
        self.attrDict = attrDict

        #required args
        self.postVar('label',label)

        #optional args
        self.postDict()

        #return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults=True)
        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteEntity(self, eId):
        """
        Delete an entity.
        
        Arguments:
        eId -- entity id
        
        Returns: status code
        """
        self.baseURL('entities/'+str(eId)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Checks {{{

    def createCheck(self, entityId, attrDict={}, testMode=False):
        """
        Creates (or test creates) a new check associated with an entity.
        
        Arguments:
        entityId -- 
        attrDict -- python dictionary of options:
            type -- remote.dns / remote.ssh / remote.smtp / remote.http /
                remote.tcp / remote.ping / remote.ftp-banner / remote.imap-banner /
                remote.pop3-banner / remote.smtp-banner / remote.postgresql-banner /
                remote.telnet-banner / remote.mysql-banner /
                remote.mssql-banner  (Required)
            details -- (Optional)
            disabled -- (Optional)
            label -- (Optional)
            metadataDict -- metadata python dict of key/value pairs (Optional)
            period -- (Optional)
            timeout -- (Optional)
            monitoringZonesPoll -- (for remote checks) (Optional)
            targetAlias -- (for remote checks) (Optional)
            targetHost -- (for remote checks) (Optional)
            targetResolver -- (for remote checks) (Optional)
        testMode -- true/false (default=True)
        
        Returns: status code
        """

        if testMode:
            self.baseURL('entities/'+str(entityId)+'/test-check') 
        else:
            self.baseURL('entities/'+str(entityId)+'/checks') 
        self.attrDict = attrDict

        #required + optional args
        self.postDict()

        if testMode:
            return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        else:
            return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def testCheck(self, entityId, attrDict={}):
        """
        Tests the creation of a new check associated with an entity.
        
        Arguments:
        entityId -- entity id
        attrDict -- python dictionary:
            type -- remote.dns / remote.ssh / remote.smtp / remote.http /
                remote.tcp / remote.ping / remote.ftp-banner / remote.imap-banner /
                remote.pop3-banner / remote.smtp-banner / remote.postgresql-banner /
                remote.telnet-banner / remote.mysql-banner / remote.mssql-banner  
            details -- (Optional)
            disabled -- (Optional)
            label -- (Optional)
            metadataDict -- metadata python dict of key/value pairs (Optional)
            period -- (Optional)
            timeout -- (Optional)
            monitoringZonesPoll -- (for remote checks) (Optional)
            targetAlias -- (for remote checks) (Optional)
            targetHost -- (for remote checks) (Optional)
            targetResolver -- (for remote checks) (Optional)
        
        Returns: status code
        """
        return self.createCheck(entityId, attrDict, True)
        
    def getCheck(self, entityId, checkId):
        """
        Returns the specified check.
        
        Arguments:
        entityId -- 
        checkId -- 
        
        Returns: status code.
        """
        self.baseURL('entities/'+str(entityId)+'/checks/'+str(checkId)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getChecks(self, entityId):
        """
        Lists checks associated with an entityId.
        
        Arguments:
        entityId --
        
        Returns: JSON results as python dict
        """
        self.postData={}
        self.baseURL('entities/'+str(entityId)+'/checks') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def testRunCheck(self, entityId, checkId):
        """
        Test a check inline.
        
        Arguments:
        entityId -- 
        checkId -- 
        
        Returns: status code.
        """
        self.baseURL('entities/'+str(entityId)+'/checks/'+str(checkId)+'/test') 
        return apiRequest(self, self.endpoint, "POST", returnResults=True)
        
    def updateCheck(self, entityId, checkId, attrDict={}):
        """
        Updates a check associated with an entity.
        
        Arguments:
        entityId -- 
        attrDict -- python dictionary or optional args:
            type -- remote.dns / remote.ssh / remote.smtp / remote.http /
                remote.tcp / remote.ping / remote.ftp-banner / remote.imap-banner /
                remote.pop3-banner / remote.smtp-banner / remote.postgresql-banner /
                remote.telnet-banner / remote.mysql-banner / remote.mssql-banner   (Required)
            details -- (Optional)
            disabled -- (Optional)
            label -- (Optional)
            metadata -- metadata python dict of key/value pairs (Optional)
            period -- (Optional)
            timeout -- (Optional)
            monitoringZonePoll -- (for remote checks) (Optional)
            targetAlias -- (for remote checks) (Optional)
            targetHost -- (for remote checks) (Optional)
            targetResolver -- (for remote checks) (Optional)
        
        Returns: status code
        """
        self.baseURL('entities/'+str(entityId)+'/checks/'+str(checkId)) 
        self.attrDict = attrDict
        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteCheck(self, entityId, checkId):
        """
        Deletes a check.
        
        Arguments:
        entityId -- 
        checkId -- 
        
        Returns: status code
        """
        self.baseURL('entities/'+str(entityId)+'/checks/'+str(checkId)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Check Types {{{

    def getCheckType(self, id):
        """
        Returns the specified check type.
        
        Arguments:
        id -- check type id
        
        Returns: status code.
        """
        self.baseURL('check_types/'+str(id)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getCheckTypes(self):
        """
        List available check types.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('check_types') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Alarms {{{

    def createAlarm(self, entityId, checkId, planId, attrDict={}, testMode=False):
        """
        Create (or test run the creation of) a(n) new alarm.
        
        Arguments:
        entityId --
        checkId --
        planId -- notification plan id
        attrDict -- python dict options:
            criteria -- (Optional)
            disabled -- (Optional) (true/false)
            label -- (Optional)
            metadata -- python dict of metadata key value pairs (Optional)
        testMode -- true/false (default=False)

        Returns: status code
        """

        if testMode:
            self.baseURL('entities/'+str(entityId)+'/test-alarm') 
        else:
            self.baseURL('entities/'+str(entityId)+'/alarms') 
        self.attrDict = attrDict

        #required args
        self.postVar('check_id',checkId)
        self.postVar('notification_plan_id',planId)

        #optional args
        self.postDict()

        if testMode:
            return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        else:
            return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def testAlarm(self, entityId, checkId, planId, attrDict={}):
        """
        Test run the creation of an alarm.
        
        Arguments:
        entityId --
        checkId --
        planId -- notification plan id
        attrDict -- python dict options:
            criteria -- (Optional)
            label -- (Optional)
            metadataDict -- python dict of metadata key value pairs (Optional)

        Returns: status code
        """
        return self.createAlarm(entityId, checkId, planId, attrDict, True)
        
    def getAlarm(self, entityId, alarmId):
        """
        Returns the specified alarm.
        
        Arguments:
        entityId -- 
        alarmId -- 
        
        Returns: status code.
        """
        self.baseURL('entities/'+str(entityId)+'/alarms/'+str(alarmId)) 
        return apiRequest(self, self.endpoint, "GET", self.postData, returnResults=True)
        
    def getAlarms(self, entityId):
        """
        Lists alarms associated with an entityId.
        
        Arguments:
        entityId --
        
        Returns: JSON results as python dict
        """
        self.baseURL('entities/'+str(entityId)+'/alarms') 
        return apiRequest(self, self.endpoint, "GET", self.postData, returnResults=True)
        
    def updateAlarm(self, entityId, alarmId, attrDict={}):
        """
        Update an alarm associated with an entity.
        
        Arguments:
        entityId --
        alarmId --
        attrDict -- python dict options:
            checkId --
            planId -- notification plan id (Optional)
            criteria -- (Optional)
            label -- (Optional)
            metadataDict -- python dict of metadata key value pairs (Optional)

        Returns: status code
        """

        self.baseURL('entities/'+str(entityId)+'/alarms/'+str(alarmId)) 
        self.attrDict = attrDict

        #optional args
        self.postDict()

        #return apiRequest(self, self.endpoint, "PUT", self.postData, returnResults=True)
        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteAlarm(self, entityId, alarmId):
        """
        Deletes an alarm.
        
        Arguments:
        entityId -- 
        alarmId -- 
        
        Returns: status code
        """
        self.baseURL('entities/'+str(entityId)+'/alarms/'+str(alarmId)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Notification Plans {{{

    def createNPlan(self, label, attrDict={}): # criticalState, okState, warningState):
        """
        Creates a notification plan.
        
        Arguments:
        label --
        attrDict -- python dict options:
            critical_state --
            ok_state --
            warning_state --

        Returns: status code
        """

        self.baseURL('notification_plans') 
        self.attrDict = attrDict

        #optional args
        self.postVar('label',label)
        self.postDict()

        #print self.endpoint
        #print self.postData

        #return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def getNPlans(self):
        """
        Lists notification plans for current account.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('notification_plans') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getNPlan(self, npId):
        """
        Returns the specified notification plan.
        
        Arguments:
        nplanId -- 
        
        Returns: status code.
        """
        self.baseURL('notification_plans/'+str(npId)) 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def updateNPlan(self, npId, attrDict={}):
        """
        Update a notification plan associated with an entity.
        
        Arguments:
        nplanId --
        attrDict -- python dict of option args:
            label --
            critical_state --
            ok_state --
            warning_state --

        Returns: status code
        """

        self.baseURL('notification_plans/'+str(npId)) 
        self.attrDict = attrDict
        self.postDict()
        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteNPlan(self, npId):
        """
        Deletes a notification plan.
        
        Arguments:
        entityId -- 
        nplanId -- 
        
        Returns: status code
        """
        self.baseURL('notification_plans/'+str(npId)) 
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Monitoring Zones {{{

    def getMZones(self):
        """
        List monitoring zones.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('monitoring_zones') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getMZone(self, mzoneId):
        """
        Returns the specified monitoring zone.
        
        Arguments:
        mzoneId -- 
        
        Returns: status code.
        """
        self.baseURL('monitoring_zones/'+str(mzoneId)) 
        return apiRequest(self, self.endpoint, "GET", self.postData, returnResults=True)
        
    def traceMZone(self, mzoneId, target, attrDict={}):
        """
        Perform a traceroute from a collector in the specified monitoring zones.
        
        Arguments:
        mzoneId -- 
        target -- target ip or hostname
        attrDict -- python dict options:
            targetResolver -- IPv6 / IPv6 (Optional)
        
        Returns: status code.
        """
        self.baseURL('monitoring_zones/'+str(mzoneId)+'/traceroute') 
        self.attrDict = attrDict
        self.postVar('target',target)
        self.postDict()
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)

    # }}}
    #Alarm Notification History {{{

    def discoverAlarmHistory(self, entityId, alarmId):
        """
        List checks for which alarm notification history is available.
        
        Arguments:
        entityId --
        alarmId --

        Returns: JSON results as python dict
        """
        self.baseURL('entities/'+str(entityId)+'/alarms/'+str(alarmId)+'/notification_history') 
        #print self.endpoint
        #print self.postData
        return apiRequest(self, self.endpoint, "GET", self.postData, returnResults=True)
        
    def getAlarmHistory(self, entityId, alarmId, checkId, uuid=None):
        """
        List checks for which alarm notification history is available -- or if
        uuid is provided, retrieves a single alarm notification history item.
        
        Arguments:
        entityId --
        alarmId --
        checkId --
        uuid -- id of a single alarm notification history item (Optional)

        Returns: JSON results as python dict
        """
        if uuid:
            self.baseURL('entities/'+str(entityId)+'/alarms/'+str(alarmId)+'/notification_history/'+str(checkId)+'/'+str(uuid)) 
        else:
            self.baseURL('entities/'+str(entityId)+'/alarms/'+str(alarmId)+'/notification_history/'+str(checkId)) 
        #print self.endpoint
        #print self.postData
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Notifications {{{

    def createNotification(self, label, type, details, testMode=False):
        """
        Create (or test the creation of ) a notification.
        
        Arguments:
        label -- 
        type -- webhook / email
        details -- 
        testMode -- true/false (default=False)
        
        Returns: status code
        """
        self.baseURL('notifications')
        self.postVar('details',details)
        self.postVar('label',label)
        self.postVar('type',type)
        return apiRequest(self, self.endpoint, "POST", self.postData)
        
    def testNotification(self, label, type, details):
        """
        Tests the creation of a notification.
        
        Arguments:
        label -- 
        type -- webhook / email
        details -- 
        
        Returns: status code
        """
        return self.createNotification(label,type,details,True)
        
    def getNotification(self, noteId):
        """
        Returns the specified notification.
        
        Arguments:
        noteId -- 
        
        Returns: status code.
        """
        self.baseURL('notifications/'+str(noteId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getNotifications(self):
        """
        Lists notifications.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('notifications')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def testRunNotification(self, noteId):
        """
        Test a notification inline.
        
        Arguments:
        noteId -- 
        
        Returns: status code.
        """
        self.baseURL('notifications/'+str(noteId)+'/test')
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)
        
    def updateNotification(self, noteId, attrDict={}): 
        """
        Updates a notification.
        
        Arguments:
        noteId --
        attrDict -- python dict options:
            details -- 
            label -- 
            type -- webhook / email
        
        Returns: status code
        """

        self.baseURL('notifications/'+str(noteId))
        self.attrDict = attrDict

        #optional args
        self.postDict()

        return apiRequest(self, self.endpoint, "PUT", self.postData)
        
    def deleteNotification(self, noteId):
        """
        Deletes a notification.
        
        Arguments:
        noteId -- 
        
        Returns: status code
        """
        self.baseURL('notifications/'+str(noteId))
        return apiRequest(self, self.endpoint, "DELETE")

    # }}}
    #Notification Types {{{

    def getNotificationType(self, ntId):
        """
        Returns the specified notification type.
        
        Arguments:
        id -- notification type id
        
        Returns: status code.
        """
        self.baseURL('notification_types/'+str(ntId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getNotificationTypes(self):
        """
        List available notification types.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('notification_types')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Changelogs {{{

    def getAlarmChangelogs(self):
        """
        List alarm changelogs.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('changelogs/alarms')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Views {{{

    def getOverview(self):
        """
        Return the overview.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('views/overview')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)

    # }}}
    #Alarm Examples {{{

    def getAlarmExamples(self):
        """
        Return list of alarm examples.
        
        Arguments:
        
        Returns: JSON results as python dict
        """
        self.baseURL('alarm_examples')
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def getAlarmExample(self, aeId):
        """
        Retrieve alarm example.
        
        Arguments:
        aeId -- alarm example id
        
        Returns: status code.
        """
        self.baseURL('alarm_examples/'+str(aeId))
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def evalAlarmExample(self, aeId, evalDict):
        """
        Evaluate alarm example.
        
        Arguments:
        aeId -- alarm example id
        evalDict  -- python dict of key/value pairs

        Returns: status code.
        """
        self.baseURL('alarm_examples/'+str(aeId))
        self.postVar('values',evalDict)
        return apiRequest(self, self.endpoint, "POST", self.postData, returnResults=True)

    # }}}

#eof
