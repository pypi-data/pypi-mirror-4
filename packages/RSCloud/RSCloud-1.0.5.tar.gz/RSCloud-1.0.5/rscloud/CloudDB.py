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
        flavor --
        size   --
        name   --
        db     --
        user   --
        
        Returns:
        result  -- JSON response converted to python Dict
        """

        self.baseURL('instances') 
        
        if int(size) not in range(1,51):
            raise RSException("setInstance", "Size not in range on setInstance")
        elif int(flavor) not in self.flavors:
            raise RSException("setInstance", "Flavor key not in dictionary on setInstance")
            
        params = { 'instance': { 'flavorRef': self.flavors[int(flavor)], 'volume': { 'size': str(size) }, 'name': name } }
            
        if db is not None:
            params['instance']['databases'] = db
            
        if user is not None:
            params['instance']['users'] = user
            
        return apiRequest(self, self.endpoint, "POST", data=params, returnResults=True)
        
    def getInstance(self, iId=None):
        """
        Lists mysql instance details.  Either all or one with the provided instance id
        
        Arguments:
        iId --
        
        Returns:
        result -- JSON response converted to python Dict
        """ 
        if iId is not None:
            self.baseURL('instances/'+str(iId)) 
        else:
            self.baseURL('instances') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteInstance(self, iId):
        """
        Deletes mysql instance using provided instance id
        
        Arguments:
        iId --
        
        Returns:
        status code
        """
        self.baseURL('instances/'+str(iId)) 
        return apiRequest(self, self.endpoint, "DELETE")
        
    def getRoot(self, iId, check=False):
        """
        Enable and get root credentials for mysql instance using provided instance id
        Or if check=True, return status of root enabled on the instance.
        
        Arguments:
        iId --
        
        Returns:
        JSON results as a python dict
        """ 
        self.baseURL('instances/'+str(iId)+'/root') 
        if not check:
            return apiRequest(self, self.endpoint, "POST", returnResults=True)
        else:
            return apiRequest(self, self.endpoint, "GET", returnResults=True)

    #}}}
    #DB Instance Actions{{{

    def doAction(self, iId, reboot=False, flavor=False, volume=False):
        """
        Perfom action on instance such as reboot mysql or resize flavor/volume.
        
        Arguments:
        iId --
        reboot --
        flavor --
        volume --
        
        Returns:
        status code
        """ 

        self.baseURL('instances/'+str(iId)+'/action') 

        if not reboot and not flavor and not volume:
            raise RSException("doAction", "Need reboot, flavor or volume argument")
        elif flavor is not False and int(flavor) not in self.flavors:
            raise RSException("doAction", "Flavor key %s not in dictionary on setInstance" % str(flavor))
        elif volume is not False and int(volume) not in range(1,51):
            raise RSException("doAction", "Volume %s is not within range 1-50" % str(volume))
        
        data = {}
        
        if reboot:
            data = { 'restart': { } }
        elif flavor:
            data = { 'resize': { 'flavorRef': self.flavors[int(flavor)] } }
        elif volume:
            data = { 'resize': { 'volume': { 'size': int(volume) } } }

        return apiRequest(self, self.endpoint, "POST", data)
        
    def createDatabase(self, iId, name, charset=None, collate=None):
        """
        Create new database within an instance id given the provided name
        
        Arguments:
        iId --
        name --
        charset --
        collate --
        
        Returns:
        status code
        """

        self.baseURL('instances/'+str(iId)+'/databases') 

        try:
            data = { 'databases': [ { 'name':str(name) } ] }
            if charset is not None:
                data['databases'][0]['character_set'] = charset
            if collate is not None:
                data['databases'][0]['collate'] = collate
        
            return apiRequest(self, self.endpoint, "POST", data)
            
        except:
            raise RSException("setDatabase")

    #}}}
    #Databases{{{

    def getDatabases(self, iId):
        """
        Lists databases within an instance
        
        Arguments:
        id --
        
        Returns:
        JSON results as python dict
        """ 
        self.baseURL('instances/'+str(iId)+'/databases') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
                
    def deleteDatabase(self, iId, name):
        """
        Deletes specified database name within specified instance id
        
        Arguments:
        id --
        name --
        
        Returns:
        status code
        """
        self.baseURL('instances/'+str(iId)+'/databases/'+name) 
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
        data = { 'users': [ { 'name':name, 'password':password } ] }
        
        try:
            if databases is not None:
                data['users'][0]['databases'] = databases
            
            return apiRequest(self, self.endpoint, "POST", data)
        except:
            raise RSException("setUser")
                    
    def getUsers(self, iId):
        """
        Lists users associated with a specific instance
        
        Arguments:
        iId --
        
        Returns:
        JSON results as a python dict
        """
        self.baseURL('instances/'+str(iId)+'/users') 
        return apiRequest(self, self.endpoint, "GET", returnResults=True)
        
    def deleteUser(self, iId, name):
        """
        Deletes a specified user from a specified instance
        
        Arguments:
        id --
        name --
        
        Returns:
        status code
        """ 
        self.baseURL('instances/'+str(iId)+'/users/'+name) 
        return apiRequest(self, self.endpoint, "DELETE")

    #}}}
    #Flavors{{{

    def getFlavor(self, fId=None):
        """
        Lists info about flavor(s).  Can specify an id for detailed info on flavor
        
        Arguments:
        fId -- Optional
        
        Returns:
        JSON results as python dict
        """ 
        if fId is not None:
            self.baseURL('flavors/'+str(fId)) 
        else:
            self.baseURL('flavors') 
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
            raise RSException("_getFlavors")

    #}}}

#eof
