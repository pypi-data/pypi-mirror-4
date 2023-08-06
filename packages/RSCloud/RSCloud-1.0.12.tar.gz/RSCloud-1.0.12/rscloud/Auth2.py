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

import requests,yaml,os,sys,re,keyring,keyring.backend,logging
import simplejson as json
from datetime import datetime
import dateutil.parser
from pytz import utc
from getpass import getpass
#from bin._Globals import *

log = logging.getLogger(__name__)

"""
A module to interface into Rackspace Cloud's Auth 2 api.  

Exported Classes:

Auth2 -- A class that handles the auth and token caching for Rackspace Cloud accounts via Auth 1.1 api.
"""

class Auth2(object):
    """A class that handles the auth and token caching for Rackspace Cloud accounts.
    It only uses api key for auth.  You will be prompted for creds if a .cloudAccount.yml 
    file doesn't exist.  Create the object to initially validate.  Any time an api 
    request is needed, call validate() to verify the token.  
    
    Variables:
    cloudAccount -- List containing the following creds
    username -- Cloud username(string)
    key      -- Cloud api key(string)
    token    -- Cloud cached token(string)
    expires  -- Cloud token expiration time(string)
    tenant   -- Cloud tenant id
    
    cloudAccountUK -- List containing the following UK creds
    username  -- Cloud UK username(string)
    key       -- Cloud UK api key(string)
    token     -- Cloud UK token(string)
    expires   -- Cloud UK token expiration time(string)
    tenant    -- Cloud tenant id
    
    endpoints -- Dictionary containing US and UK Auth endpoints
    
    pd -- Current working directory

    Public Functions:
    __init__ -- Object initialization
    validate -- Validates current token stored in cloudAccount.
    
    Private Functions:
    _auth    -- Authenticate using cloudAccount credentials and endpoints
    _updateResults -- Dumps account and endpoints to file
    _logResults    --
    
    """
    
    cloudAccount = ""
    env = ""
    region = None
    headers = { }
    
    endpoints = dict(
        US="https://identity.api.rackspacecloud.com/v2.0/tokens",
        UK="https://lon.identity.api.rackspacecloud.com/v2.0/tokens"
        )
        
    pd = os.path.dirname(os.path.realpath(__file__))
    
    def __init__(self, env):
        """Initializes Auth1 object and assigns cloudAccount dict based on env and keyring creds.  Calls validate().
        
        Arguments:
        env -- The cloud environment(us,uk)(string).
        """
        
        if re.search("us", env, re.IGNORECASE) or re.search("uk", env, re.IGNORECASE):
            self.env = env.upper()
        self._getKeyring()
        
        self.validate()
        
    def validate(self, force=False):
        """Checks expires time to current time and re-auths if needed.
        
        Arguments:
        force -- Force token re-auth if needed(bool).
        
        Returns:
        True or False indicating an existing valid cached token or re-auth success.
        """ 
        
        if not force:
            if (dateutil.parser.parse(self.cloudAccount['expires']) > datetime.now(utc)):
                if 'X-Auth-Token' not in self.headers:
                    self._setHeaders()
                return True
            else:
                return self._auth()
        else:
            return self._auth()
                    
    def _auth(self):
        """Re-Authenticates to Rackspace Cloud endpoints using data in cloudAccount lists.
        
        Returns:
        True of False indicating success of failure.
        """
        if self.cloudAccount['key'] is None:
            credentials = { "auth":{ "passwordCredentials":{ "username":self.cloudAccount['username'], "password":self.cloudAccount['password'] } } }
        else:
            credentials = { "auth":{ "RAX-KSKEY:apiKeyCredentials":{ "username":self.cloudAccount['username'], "apiKey":self.cloudAccount['key'] } } }
        
        headers = {'content-type': 'application/json'}
        
        try:
            r = requests.post(self.endpoints[self.env], data=json.dumps(credentials), headers=headers)

            if r.status_code == requests.codes.ok:
                self._logResults("Success-", r.text)
                return self._updateResults(r)
            else:
                print r.text
                self._logResults("Error-", r.text)
                return False
        except requests.exceptions.RequestException as error:
            print "Error when processing request"
            #log somewhere
            return False
            
    def _updateResults(self, r):
        """Updates endpoints.yaml file and calls _setKeyring based on successful auth.
        
        Arguments:
        r -- Requests object containing our data
        
        Returns:
        True or False depending on successful yaml updating
        """
        data = json.loads(r.text)
        cloudServices = json.loads(json.dumps(data['access']['serviceCatalog']))
        auth = json.loads(json.dumps(data['access']['token']))
        
        self.cloudAccount['token'] = auth['id']
        self.cloudAccount['expires'] = auth['expires']
        
        self._setKeyring() #store the new token and expiration
        self._setHeaders() #updating the headers  
        
        f = file(os.path.expanduser("~/.cloudServices%s.yml" % self.env), 'w')
        yaml.dump(cloudServices,f, default_flow_style=False)
        f.close()
        
        return True
        
    def _getKeyring(self):
        """
        This method checks for keyring entries for Cloud credentials and prompts for them if not present.
        Should be called with validate() and initialization.
        
        """
        
        username = keyring.get_password('cloud_auth%s' % self.env, 'username')
        key = keyring.get_password('cloud_auth%s' % self.env, 'key')
        password = keyring.get_password('cloud_auth%s' % self.env, 'password')
        token = keyring.get_password('cloud_auth%s' % self.env, 'token')
        expires = keyring.get_password('cloud_auth%s' %self.env, 'expires')
        
        if username is None: #prompt for username and api key
            username = raw_input("%s Username: " % self.env)
            print "Return to enter api key instead"
            password = getpass("%s Password: " % self.env)
            if len(password) < 3:
                key = raw_input("%s Api Key: " % self.env)
            token = "invalid"
            expires = "2012-09-27T12:17:48.000+01:00"
            
        self.cloudAccount = { "username":username,"key":key,"password":password,"token":token,"expires":expires }
        
    def _setKeyring(self):
        """
        This method sets the keyring with the cloudAccount dict.        
        
        """ 
        try:
            keyring.set_password('cloud_auth%s' % self.env, 'username', self.cloudAccount['username'])
            if self.cloudAccount['key'] is None:
                keyring.set_password('cloud_auth%s' % self.env, 'password', self.cloudAccount['password'])
            else:
                keyring.set_password('cloud_auth%s' % self.env, 'key', self.cloudAccount['key'])
            keyring.set_password('cloud_auth%s' % self.env, 'token', self.cloudAccount['token'])
            keyring.set_password('cloud_auth%s' % self.env, 'expires', self.cloudAccount['expires'])
        except keyring.backend.PasswordError:
            print "Error storing credentials"
            #log somewhere
    
    def _setHeaders(self, noType=False):
        """
        Updates json headers with latest token.
        """
        
        if noType:
            self.headers = { 'X-Auth-Token': '%s' % self.cloudAccount['token']}
        else:
            self.headers = { 'X-Auth-Token': '%s' % self.cloudAccount['token'],'content-type': 'application/json'}
        
    def _logResults(self, status, results):
        """
        Uses logger to log to file
        """
        pass

#eof

