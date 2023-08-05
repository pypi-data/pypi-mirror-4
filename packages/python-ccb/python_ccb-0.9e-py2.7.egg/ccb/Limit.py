#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""

from Utils import *
from Exceptions import *
from Base import *

def getLimitList(auth,cache):
    limitList=[]
    response=sendCommand("GET", "limits", None, auth)
    for item in response:
      limit=Limit(auth, cache, item)
      limit.onCommit="modify"
      limitList.append(limit)
    return tuple(limitList)

def getLimitFromId(auth,cache,id):
  limit=searchCache(cache,"limits",id)
  if limit != False:
    return limit
  else:
    for limit in getLimitList(auth,cache):
      if hasattr(limit,"id") and getattr(limit,"id") == id:
        return limit
    raise LimitNotFoundError("id %s not found" % (id,)) 

def getLimitObjectFromName(auth,cache,name):
  limit=searchCacheByName(cache,"limits",name)
  if name is None:
    return None
  elif limit != False:
    return limit
  else:
    for limit in getLimitList(auth, cache):
      if hasattr(limit,"name") and getattr(limit,"name").upper() == name.upper():
        return limit
    raise LimitNotFoundError("name %s not found" % (name,))

class Limit(Base):

  SPECIALATTRS=["ROLLOVER","RESET_DAY"]
  ROLLOVER={False:"false", True:"true"}
  RESET_DAY={False:0, True:1}
 
  def getAccount(self):
    if self.account_id == False:
      return None
    else:
      account=searchCacheById(self.cache,"accounts",self.account_id)
      if account != False:
        #get account oject from cache
        return account
      else: #else, get from live data
        return getAccountFromId(self.auth,self.cache,self.account_id)

  def getCategory(self):
    if self.category_id == False:
      return None
    else:
      category=searchCache(self.cache,"categories",self.category_id)
      if category != False:
        #get account oject from cache
        return category
      else: #else, get from live data
        return getCategoryFromId(self.auth,self.cache,self.category_id)
 
  def cloneLimit(self):
    return cloneObject(self)   
