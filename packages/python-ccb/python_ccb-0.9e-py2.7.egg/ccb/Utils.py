#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""
   
import restclient
from copy import copy
from httplib2 import ServerNotFoundError
from Exceptions import *
from decimal import *
#from Reminder import *
#from Limit import *

BASEURL="https://www.clearcheckbook.com/api/"
null=None
false=False
true=True

def sendCommand(requestType, command, data, auth, mode=False):
  request=getattr(restclient,requestType)
  response=request("%s%s" % (BASEURL,command),params=data,credentials=auth,async=mode)
  try:
    response=eval(response.replace("\/","/")) #WARNING1! response is coming as raw unicode WARNING2!: Slashes are escapped!!
  except:
    pass
  return response

def castAttribute(attribute):

  if type(attribute) != str:
    return attribute
  else:
    try:
      return int(attribute)
    except:
      try:
        return Decimal(attribute)
      except:
        if attribute is None:
          return None
        elif attribute.lower() == "false":
          return bool(0)
        elif attribute.lower() == "true":
          return bool(1)
        else:
          return str(attribute).decode('raw_unicode_escape') # Convert to Unicode 

def replaceAttributes(object,direction):
  if not hasattr(object,"SPECIALATTRS"):
    return None
  else:
    attributesDict={}
    for specialAttr in object.SPECIALATTRS:
      if direction == "fromOutside":
        for item in getattr(object,specialAttr).copy().items(): #get new dict and get each items key,value
          attributesDict[item[1]]=item[0] #reverse original dict and convert them to str to later get them

      elif direction == "toOutside": #in this case, we don't need to reverse the dict
        attributesDict=getattr(object,specialAttr)
 
      if hasattr(object, specialAttr.lower()): # Do only of the attribute exists
        attribute=getattr(object,specialAttr.lower()) #get attribute to change
        newValue=attributesDict.get(attribute,getattr(object,specialAttr.lower())) #get new value or return the old value
        if direction == "fromOutside":
          newValue=castAttribute(newValue)  #cast newValue
        setattr(object, specialAttr.lower(), newValue) # set it to attribute

def loadDataToObject(object,data):
  object.attributes=[]
  for name,value in data.items():
    if name.upper() not in object.SPECIALATTRS: #we will convert the special attributes later (function replaceAttributes)
      value=castAttribute(value)
    setattr(object,name,value)
    object.attributes.append(name)

def unloadDataFromObject(object):
  data={}
  for name in object.attributes:
    attr=getattr(object,name)
    if type(attr) == unicode:
      pass
      #attr=attr.encode('raw_unicode_escape')
    data[name]=attr
  return data

def cloneObject(object):
    newObject=copy(object)
    newObject.id=None
    newObject.onCommit="create"
    return newObject

def searchCacheById(cache,cacheType,index):
  if cache != None and index in cache[cacheType].keys():
    return cache[cacheType][index]
  else:
    return False

def searchCacheByName(cache, cacheType, name):
  if cache != None:
    for object in cache[cacheType].values():
      if hasattr(object,"name"):
        if object.name.upper() == name.upper():
          return object
 
  return False

def addCache(cache,object,index):
  if cache == None:
    return None
  elif object.__class__.__name__ == "Account":
    cacheType="accounts"
  elif object.__class__.__name__ == "Category":
    cacheType="categories"
  elif object.__class__.__name__ == "Reminder":
    cacheType="reminders"
  elif object.__class__.__name__ == "Limit":
    cacheType="limits"
  elif object.__class__.__name__ == "Transaction":
    return None
  else:
    raise CacheError("%s is not a valid object type" % (object.__class__.__name__,))
  
  if searchCacheById(cache,cacheType,index) == False:
    cache[cacheType][index]=object

def deleteCache(cache,object,index):
  if cache == None:
    return None
  elif object.__class__.__name__ == "Account":
    cacheType="accounts"
  elif object.__class__.__name__ == "Category":
    cacheType="categories"
  elif object.__class__.__name__ == "Reminder":
    cacheType="reminders"
  elif object.__class__.__name__ == "Limit":
    cacheType="limits"
  elif object.__class__.__name__ == "Transaction":
    return None
  else:
    raise CacheError("%s is not a valid object type" % (object.__class__,))
  
  if searchCacheById(cache,cacheType,index) != False:
    del(cache[cacheType][index])




 
