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

import requests,re,os,traceback,sys,logging
from yaml import load
from simplejson import loads,dumps
import simplejson as json
#from Auth2 import *
from urllib import quote
from time import time,sleep

#logging {{{

#make log dir if doesn't exist
if not os.path.exists("log"):
    os.makedirs("log")
    
#setup root logger. Valid levels (DEBUG,INFO,WARNING,ERROR,CRITICAL)
logging.basicConfig(
    filename='log/RSCloud.log',
    level=logging.WARNING,
    format='%(levelname)s %(name)s %(asctime)s %(message)s'
    )

#setup scheduler logger.  Logging levels (DEBUG,INFO,WARNING,ERROR).
log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

#set timeout for requests lib different than max_retries
timeout=86400

#setup stdout debug logging (True/False) 
#NOTE: This is just for showing in stdout clearly where the test outputs start and stop.
try:
    with open('soLog') as f:
        soLog = True
except IOError as e:
    soLog = False

#Setup logger.  Root logger config in _Globals.py
#log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

#logging }}}

class innerCls(object): 
    
    def __init__(self, cls):
        self.cls = cls
        
    def __get__(self, instance, outerclass):
        class Wrapper(self.cls):
            outer = instance
        Wrapper.__name__ = self.cls.__name__
        return Wrapper
        
    

def filterCols(var,keys,mode="var"):
    """
    Prints out key values of a list (of dictionaries) or a dictionary.

    Arguments:
    var -- can be either a list of dictionaries or a dictionary
    keys -- can be either a string or a list of strings
    """

    if mode == "var":
        var1 = []

    if type(var).__name__=='list':
        for itm in var:
            if type(keys).__name__=='list':
                buf = []
                for k,v in itm.items():
                    for key in keys:
                        if k == key:
                            buf.append(str(v))
                if mode == "print": 
                    print buf
                else:
                    var1.append(buf)
            if type(keys).__name__=='str':
                for k,v in itm.items():
                    if k == keys:
                        if mode == "print": 
                            print v
                        else:
                            var1.append(v)
    if type(var).__name__=='dict':
        if type(keys).__name__=='list':
            buf = []
            for k,v in var.items():
                for key in keys:
                    if k == key:
                        buf.append(str(v))
            if mode == "print": 
                print buf
            else:
                var1.append(buf)
        if type(keys).__name__=='str':
            for k,v in var.items():
                if k == keys:
                    if mode == "print": 
                        print v
                    else:
                        var1.append(v)

    if mode == "var":
        return var1        
   
def filterRows(listDict,inKey,inVal,outKeys,mode="str",subStr=False,caseSensitive=True):
    """
    Retrieve an output key's value from a list (of dict's) based on an input key and its value.
    Note that the input value may either be a string or a list.
    """
    if mode == "list":
        var = []
    for d in listDict:
        if mode == 'list':
            subVar = {}
        else:
            subVar = []
        #if d[inKey] == inVal:
        if reStrOrList(inVal,d[inKey],subStr,caseSensitive):
            if mode != "list":
                if type(outKeys).__name__=='str':
                    return d[outKeys]
                if type(outKeys).__name__=='list':
                    for ok in outKeys:
                        if mode == "list":
                            subVar[ok] = d[ok]
                        else:
                            subVar.append(d[ok])
                    if mode == 'list':
                        var.append(subVar)
                    else:
                        return subVar
            else:
                if type(outKeys).__name__=='str':
                    var.append(d[outKeys])
                if type(outKeys).__name__=='list':
                    for ok in outKeys:
                        if mode == "list":
                            subVar[ok] = d[ok]
                        else:
                            subVar.append(d[ok])
                    if mode == 'list':
                        var.append(subVar)
                    else:
                        return subVar
    if mode == "list":
        return var 
    return None
    
def filterRowsNot(listDict,inKey,inVal,outKeys,mode="str",subStr=False,caseSensitive=True):
    """
    Inverse retrieval of an output key's value from a list (of dict's) based on an input key and its value.
    Note that the input value may either be a string or a list.
    """
    if mode == "list":
        var = []
    for d in listDict:
        if mode == 'list':
            subVar = {}
        else:
            subVar = []
        #if d[inKey] == inVal:
        if reStrOrListNot(inVal,d[inKey],subStr,caseSensitive):
            if mode != "list":
                if type(outKeys).__name__=='str':
                    return d[outKeys]
                if type(outKeys).__name__=='list':
                    for ok in outKeys:
                        if mode == "list":
                            subVar[ok] = d[ok]
                        else:
                            subVar.append(d[ok])
                    if mode == 'list':
                        var.append(subVar)
                    else:
                        return subVar
            else:
                if type(outKeys).__name__=='str':
                    var.append(d[outKeys])
                if type(outKeys).__name__=='list':
                    for ok in outKeys:
                        if mode == "list":
                            subVar[ok] = d[ok]
                        else:
                            subVar.append(d[ok])
                    if mode == 'list':
                        var.append(subVar)
                    else:
                        return subVar
    if mode == "list":
        return var 
    return None
    
def reStrOrListNot(v1,v2,subStr=False,caseSensitive=True):
    """
    Search for v1 in v2. v1 may be a string or list.
    """
    if caseSensitive is False:
        v1 = v1.lower()
        v2 = v2.lower()
    if type(v1).__name__=='str':
        if subStr is True and re.search(v1,v2):
            return False
        if subStr is False and v1 == v2:
            return False
    if type(v1).__name__=='list':
        for v in v1:
            if subStr is True and re.search(v,v2):
                return False
            if subStr is False and v == v2:
                return False
    return True
    
def reStrOrList(v1,v2,subStr=False,caseSensitive=True):
    """
    Search for v1 in v2. v1 may be a string or list.
    """
    if caseSensitive is False:
        v1 = v1.lower()
        v2 = v2.lower()
    if type(v1).__name__=='str':
        if subStr is True and re.search(v1,v2):
            return True
        if subStr is False and v1 == v2:
            return True
    if type(v1).__name__=='list':
        for v in v1:
            if subStr is True and re.search(v,v2):
                return True
            if subStr is False and v == v2:
                return True
    return False
    

