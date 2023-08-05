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
from copy import copy

def getAccountList(auth,cache,overview):
    if overview == True:
      data={"is_overview":"true"}
    else:
      data={}
    accountList=[]
    response=sendCommand("GET","accounts",data,auth)
    for item in response:
      account=Account(auth,cache,item)
      account.onCommit="modify"
      accountList.append(account)
    return tuple(accountList)

def getAccountObjectFromId(auth,cache,id):
  account=searchCacheById(cache,"accounts",id)
  if account != False:
    return account
  else:
    for account in getAccountList(auth,cache,True):
      if hasattr(account,"id") and getattr(account,"id") == id:
        return account
    raise AccountNotFoundError("id %s not found" % (id,)) 

def getAccountObjectFromName(auth,cache,name):
  account=searchCacheByName(cache,"accounts",name)
  if name is None:
    return None
  elif account != False:
    return account
  else:
    for account in getAccountList(auth, cache,False):
      if hasattr(account,"name") and getattr(account,"name").upper() == name.upper():
        return account 
    raise AccountNotFoundError("name %s not found" % (name,))

class Account(Base):
 
  SPECIALATTRS=["TYPE_ID"] 
  TYPE_ID={"cash":1,"checking":2,"savings":3,"credit":4}

  def __init__(self, auth, cache, data=None):
    Base.__init__(self, auth, cache, data)
    
    if self.jive_deposit == None:
      self.jive_deposit=0
    if self.jive_withdrawal == None:
      self.jive_withdrawal=0
    if self.deposit == None:
      self.deposit=0
    if self.withdrawal == None:
      self.withdrawal=0


    self.total_unjived=self.deposit - self.withdrawal
    self.total_jived=self.jive_deposit - self.jive_withdrawal

  def refreshAccount(self):
    account=getAccountObjectFromId(self.auth, None, self.id)
    for attr in dir(account):
      if attr != "cache" and callable(getattr(account, attr)) == False:
        #do not copy cache or callable objects
        setattr(self, attr, getattr(account, attr))


  def cloneAccount(self):
    return cloneObject(self)    
