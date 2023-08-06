#!/usr/bin/python

"""
functions will need to be called with ( Cloud ) instance as first argument.
same behavior as required from any of the other standard bindings files. 
"""

from Cloud import *
from CloudMonitor import *
from CloudServersFG import *
from CloudServersNG import *
from CloudLB import *

class ListOps(Cloud):

    def getAll(self, module, method, attrDict={}):
        """
        Used to get the full (unlimited) list of paginated results from a Cloud API List Operation.         

        Arguments::
        :param module: -- name of RSCloud module who implements 'method' (required)
        :type module: string
        :param method: -- name of method (list operation, usually "get***s" implemented by 'module' (required)
        :type method: string
        
        Optional arguments::
        :attrDict: -- python dictionary of arg options (see original method documentation)
        :*args: -- TODO
        :**kwargs: -- TODO

        :returns: Same as original, but all existing entries of paginated responses in one data structure
          
        """
       
        ClassInstance = globals()[module](self.env, self.region)
 
        ClassMethod = getattr(ClassInstance, method)


        Entries = []

        if attrDict:
            response = ClassMethod(attrDict)
        else:
            response = ClassMethod()

        gimmeMore = 1
        while gimmeMore:
            if response['metadata']['next_href']:
                values = response['values']
                for entry in values:
                    Entries.append(entry)
                next_href = response['metadata']['next_href']
                response = self.apiRequest(next_href, "GET", returnResults=True)
            else:
                values = response['values']
                for entry in values:
                    Entries.append(entry)
                metadata = response['metadata']
                gimmeMore = False

        metadata.update({'total': len(Entries)})                
        results = {'values': Entries, 'metadata': metadata} 

        return results

#EOF 
