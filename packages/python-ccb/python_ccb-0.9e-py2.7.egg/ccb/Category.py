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

def getCategoryList(auth,cache):
    categoryList=[]
    response=sendCommand("GET","categories",None,auth)
    for item in response:
      category=Category(auth,cache,item)
      category.onCommit="modify"
      categoryList.append(category)
    return tuple(categoryList)

def getCategoryObjectFromId(auth,cache,id):
  category=searchCacheById(cache,"categories",id)
  if id is None:
    return None
  elif category != False:
    return category
  else:
    for category in getCategoryList(auth,cache):
      if hasattr(category,"id") and getattr(category,"id") == id:
        return category
    raise CategoryNotFoundError("id %s not found" % (id,)) 

def getCategoryObjectFromName(auth,cache,name):
  category=searchCacheByName(cache,"categories",name)
  if name is None:
    return None
  elif category != False:
    return category
  else:
    for category in getCategoryList(auth, cache):
      if hasattr(category,"name") and getattr(category,"name").upper() == name.upper():
        return category
    raise CategoryNotFoundError("name %s not found" % (name,))

class Category(Base):
  SPECIALATTRS=["PARENT"] 
  PARENT={None:0}

  def getParent(self):
    if self.parent == 0:
      return None
    else:
      return searchCacheById(self.cache,"categories",self.parent)

  def refreshCategory(self):
    category=getCategoryObjectFromId(self.auth, None, self.id)
    for attr in dir(category):
      if attr != "cache" and callable(getattr(newData, attr)) == False:
        #do not copy cache or callable objects
	setattr(self, attr, getattr(category, attr))

  def cloneCategory(self):
    return cloneObject(self)   
