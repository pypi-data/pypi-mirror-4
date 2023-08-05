#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""

from Utils import *
from copy import copy

class Base:
  
  def __init__(self, auth, cache, data=None):
 
    if data is not None:
      loadDataToObject(self,data)
    
    if hasattr(self,"id"):
      try:
        addCache(cache,self,self.id)
      except CacheError: #catch CacheError exception because we don't want to add to cache Transact objects
        pass

    self.cache=cache
    self.auth=auth
    if data is not None:
      replaceAttributes(self,"fromOutside")

  def commit(self):
    workObject=copy(self)
    replaceAttributes(workObject,"toOutside")    
    data=unloadDataFromObject(workObject)
    objectType=self.__class__.__name__.lower()
    if self.onCommit == "create":
      response=sendCommand("POST", objectType, data, self.auth, False)
      if type(response) == int:
        self.id=response
        addCache(self.cache, self, self.id)
        self.onCommit="modify"
    
    elif self.onCommit == "modify":
      return sendCommand("PUT", objectType, data, self.auth, False)
    else:
      raise CommitError("commit for object %s is not allowed" % (objectType,))
    
  def delete(self):
    objectType=self.__class__.__name__
    data={"id": self.id}
    response=sendCommand("DELETE", objectType, data, self.auth, False)
    if response == True:
      deleteCache(self.cache,self, self.id) 
      for attribute in self.attributes:
        delattr(self, attribute)
      del self.attributes
      del self.onCommit
      del self.auth
      return True
    else:
      raise DeleteError("unspected response from server:" + str(response))
