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

#Setup logger.  Root logger config in _Globals.py
log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

class CloudDB(Cloud):
    """
    A class that handles actions to Cloud Databases via public methods listed.
    """

    #properties + constructor{{{

    service = "Databases"
    flavors = { } #flavorId and href

    def __init__(self,*args):
        super(CloudDB,self).__init__(*args)
        self._getFlavors()

    #}}}
    #DB Instances{{{
    
    def createInstance(self, flavor, size, name, db=None, user=None):

        """
        Creates a mysql instance using the provided flavor id and size(1-50 GB) for allocating databases to.  
        
        Arguments:
        flavor -- Instance flavor size(int)
        size   -- Instance storage size(int)
        name   -- Instance name(string)
        db     -- List of databses with optional keys(list)
            name -- Database name(string)
            character_set -- Default utf8(string)
            collate -- Rules default is utf8_general_ci(string)
        user   -- List of users with optional keys(list)
            name -- User name(string)
            password -- User pass(string)
            databases -- List of databases w/ name key(list)
        
        Returns:
        result  -- JSON response converted to python Dict
        """

        self.baseURL('instances') 
        
        if int(size) not in range(1,51):
            log.warning("Size not in range on setInstance")
        elif int(flavor) not in self.flavors:
            log.warning("Flavor key not in dictionary on setInstance")
        
        log.info("createInstance assigning required vars")    
        params = { 'instance': { 'flavorRef': self.flavors[int(flavor)], 'volume': { 'size': str(size) }, 'name': name } }
        
        log.info("createInstance assigning optional vars")    
        if db is not None:
            params['instance']['databases'] = db    
        if user is not None:
            params['instance']['users'] = user
        
        log.info("createInstance POST call to %s with data - %s" % (self.endpoint, str(params)))
        return apiRequest(self, self.endpoint, "POST", data=params, returnResults=True)
        
    def getInstance(self, iId=None):
        """
        Lists mysql instance details.  Either all or one with the provided instance id
        
        Arguments:
        iId -- Instance id(str)
        
        Returns:
        result -- JSON response converted to python Dict
        """
        log.info("getInstance assigning optional vars") 
        if iId is not None:
            self.baseURL('instances/'+str(iId)) 
        else:
            self.baseURL('instances') 
            
        log.info("getInstance GET call to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteInstance(self, iId):
        """
        Deletes mysql instance using provided instance id
        
        Arguments:
        iId -- Instance id(str)
        
        Returns:
        status code
        """
        self.baseURL('instances/'+str(iId)) 
        
        log.info("deleteInstance DELETE call to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "DELETE")
        
    def getRoot(self, iId, check=False):
        """
        Enable and get root credentials for mysql instance using provided instance id
        Or if check=True, return status of root enabled on the instance.
        
        Arguments:
        iId -- Instance id(str)
        
        Returns:
        JSON results as a python dict
        """ 
        self.baseURL('instances/'+str(iId)+'/root') 
        if not check:
            log.info("getRoot POST to %s" % self.endpoint)
            return apiRequest(self, self.endpoint, "POST", returnResults=True)
        else:
            log.info("getRoot GET to %s" % self.endpoint)
            return apiRequest(self, self.endpoint, "GET", returnResults=True)

    #}}}
    #DB Instance Actions{{{

    def setAction(self, iId, reboot=False, flavor=False, volume=False):
        """
        Perfom action on instance such as reboot mysql or resize flavor/volume.
        
        Arguments:
        iId -- Instance id(string)
        reboot -- Boolean
        flavor -- Flavor id(int)
        volume -- Storage size in GB(int)
        
        Returns:
        status code
        """ 

        self.baseURL('instances/'+str(iId)+'/action') 

        if not reboot and not flavor and not volume:
            log.warning("setAction need reboot, flavor or volume argument")
        elif flavor is not False and int(flavor) not in self.flavors:
            log.warning("setAction flavor key %s not in dictionary" % str(flavor))
        elif volume is not False and int(volume) not in range(1,51):
            log.warning("setAction volume %s is not within range 1-50" % str(volume))
        else:
            log.warning("setAction needs reboot, flavor or volume arg set")
        
        data = {}
        
        if reboot:
            data = { 'restart': { } }
        elif flavor:
            data = { 'resize': { 'flavorRef': self.flavors[int(flavor)] } }
        elif volume:
            data = { 'resize': { 'volume': { 'size': int(volume) } } }

        log.info("setInstance POST to %s with data - %s" % (self.endpoint, str(data)))
        return apiRequest(self, self.endpoint, "POST", data)
        
    #}}}
    #Databases{{{

    def createDatabase(self, iId, name, charset=None, collate=None):
        """
        Create new database within an instance id given the provided name
        
        Arguments:
        iId -- Instance id(str)
        name -- Database name(str)
        charset -- Default utf8(string)(optional)
        collate -- Rules default is utf8_general_ci(string)(optional)
        
        Returns:
        status code
        """

        self.baseURL('instances/'+str(iId)+'/databases') 

        log.info('createDatabase assigning  required vars')
        data = { 'databases': [ { 'name':str(name) } ] }
        
        log.info('createDatabase assigning optional vars')
        if charset is not None:
            data['databases'][0]['character_set'] = charset
        if collate is not None:
            data['databases'][0]['collate'] = collate
        
        log.info("createDatabase POST to %s with data - %s" % (self.endpoint, str(data)))        
        return apiRequest(self, self.endpoint, "POST", data)

    def getDatabases(self, iId):
        """
        Lists databases within an instance
        
        Arguments:
        id -- Instance id(str)
        
        Returns:
        JSON results as python dict
        """ 
        self.baseURL('instances/'+str(iId)+'/databases') 

        log.info("getDatabases GET to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
                
    def deleteDatabase(self, iId, name):
        """
        Deletes specified database name within specified instance id
        
        Arguments:
        id -- Instance id(str)
        name -- Instance name(str)
        
        Returns:
        status code
        """
        self.baseURL('instances/'+str(iId)+'/databases/'+name) 
        
        log.info("deleteDatabase DELETE to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "DELETE")

    #}}}
    #Users{{{

    def createUser(self, iId, name, password, databases=None):
        """
        Creates a user for the specified instance, optionally to specific databases
        with specified name and pass.

        Arguments:
        id --
        name -- Name of the user for the database.
        password -- User password for database access.
        databases -- Optional(list of database names)

        Returns:
        status code
        """

        self.baseURL('instances/'+str(iId)+'/users')

        log.info('createUser assigning required vars')
        data = { 'users': [ { 'name':name, 'password':password } ] }


        if databases is not None:
            log.info('createUser assigning optional vars')
            data['users'][0]['databases'] = databases

        log.info('createUser POST to %s with data - %s' % (self.endpoint, str(data)))
        return apiRequest(self, self.endpoint, "POST", data)

 
    def getUsers(self, iId):
        """
        Lists users associated with a specific instance
        
        Arguments:
        iId -- Instance id(string)
        
        Returns:
        JSON results as a python dict
        """
        self.baseURL('instances/'+str(iId)+'/users') 
        
        log.info("getUsers GET to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
    

    def getUser(self, iId, name):
        """
        Lists a specified user associated with a specified instance
        
        Arguments:
        iId -- Instance id(string)
        name -- User name(string)
        
        Returns:
        status code
        """ 
        self.baseURL('instances/'+str(iId)+'/users/'+name) 
        
        log.info("getUser GET to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)


    def getUserAccess(self, iId, name):
        """
        Lists a specified user associated with a specified instance
        
        Arguments:
        iId -- Instance id(string)
        name -- User name(string)
        
        Returns:
        status code
        """ 
        self.baseURL('instances/'+str(iId)+'/users/'+name+'/databases') 
        
        log.info("getUserAccess GET to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)


    def grantUserAccess(self, iId, username, dbName):
        """
        Grants access for the specified user to one or more databases for the specified instance. 
        
        Arguments:
        iId -- Instance id(string)
        username -- User name (string)
        dbName -- New user password for database access
        
        Returns:
        status code

        """ 

        self.baseURL('instances/'+str(iId)+'/users/'+username+'/databases') 
        
        log.info('grantUserAccess assigning required vars username:%s and dbName:%s' % (username, dbName))
        data = { 'databases': [ { 'name':dbName } ] }
        
        log.info('grantUserAccess PUT to %s with data - %s' % (self.endpoint, str(data)))
        return apiRequest(self, self.endpoint, "PUT", data)
    
    def revokeUserAccess(self, iId, username, dbName):
        """
        Revokes access for the specified user to one or more databases for the specified instance. 
        
        Arguments:
        iId -- Instance id(string)
        username -- User name (string)
        dbName -- New user password for database access
        
        Returns:
        status code

        """ 

        self.baseURL('instances/'+str(iId)+'/users/'+username+'/databases/'+dbName) 
        
        log.info('revokeUserAccess DELETE to %s ' % (self.endpoint))
        return apiRequest(self, self.endpoint, "DELETE")

 
    def deleteUser(self, iId, name):
        """
        Deletes a specified user from a specified instance
        
        Arguments:
        iId -- Instance id(string)
        name -- User name(string)
        
        Returns:
        status code
        """ 
        self.baseURL('instances/'+str(iId)+'/users/'+name) 
        
        log.info("deleteUser DELETE to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "DELETE")

    def changePass(self, iId, name, password):
        """
        Changes the MySQL password of the specified user.  
        
        Arguments:
        iId -- Instance id(string)
        name -- User name (string)
        password -- New user password for database access
        
        Returns:
        status code

        """ 

        self.baseURL('instances/'+str(iId)+'/users') 
        
        log.info('changePass assigning required vars')
        data = { 'users': [ { 'name':name, 'password':password } ] }
        
        log.info('changePass PUT to %s with data - %s' % (self.endpoint, str(data)))
        return apiRequest(self, self.endpoint, "PUT", data)
    

    #}}}
    #Flavors{{{

    def getFlavor(self, fId=None):
        """
        Lists info about flavor(s).  Can specify an id for detailed info on flavor
        
        Arguments:
        fId -- Flavor id(int)(optional)
        
        Returns:
        JSON results as python dict
        """ 
        if fId is not None:
            self.baseURL('flavors/'+str(fId)) 
        else:
            self.baseURL('flavors') 
        
        log.info("getFlavor GET to %s" % self.endpoint)
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def _getFlavors(self):
        """
        Updates self.flavors dict to have an index(int) based on flavor id with href url value
        Called on init
        """
        self.baseURL('flavors') 
        try:
            data = apiRequest(self, self.endpoint, "GET", returnResults=True)
            fdata = loads(dumps(data['flavors']))
            for flavor in fdata:
                self.flavors[flavor['id']] = flavor['links'][0]['href']
        except:
            log.warning("Unhandled exception caught in CloudDB._getFlavors()")

    #}}}

#eof
