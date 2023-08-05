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
from Category import *
from Account import *

def getTransactionsData(auth,cache,accountId,page,limit):
  transactList=[]
  data={}
  if page != 0:
    data["page"]=page
  if limit != 0:
    data["limit"]=limit
  if accountId != False:
    data["acccount_id"]=accountId
  response=sendCommand("GET","transactions",data,auth)
  for item in response:
    transact=Transaction(auth,cache,item)
    transact.onCommit="modify"
    transactList.append(transact)
  return transactList

def getTransaction(auth, cache, id):
  tran=Transaction(auth, cache, sendCommand("GET","transaction",{"id":id},auth))
  tran.onCommit="modify"
  return tran

class Transaction(Base):
  SPECIALATTRS=["TRANSACTION_TYPE","JIVE","ACCOUNT_ID","CATEGORY_ID"]
  TRANSACTION_TYPE={"withdraw":0,"deposit":1,"transfer":3}
  JIVE={True:1,False:0}
  ACCOUNT_ID=CATEGORY_ID={None:0}
  
  TRANSACT_PAGE_DEFAULT=1
  TRANSACT_LIMIT_DEFAULT=100
  
  def getAccount(self):
    if self.account_id == None:
      return None
    account=searchCacheById(self.cache,"accounts", self.account_id)
    if account != False:
      #get account oject from cache
      return account
    else: #else, get from live data
      return getAccountObjectFromId(self.auth, self.cache, self.account_id)

  def getCategory(self):
    if self.category_id == None:
      return None
    category=searchCacheById(self.cache, "categories", self.category_id)
    if category != False:
      #get account oject from cache
      return category
    else: #else, get from live data
      return getCategoryObjectFromId(self.auth, self.cache, self.category_id)
      
  def getParent(self):
    if self.specialstatus == "split":
      return getTransaction(self.auth, self.cache, self.parent)
    else:
      return None

  def editJive(self, status):
    if status == True:
      newStatus=1
    elif status == False:
      newStatus=0

    if hasattr(self,"id"):
      response=sendCommand("PUT","jive",{"id":self.id,"status":newStatus},self.auth)  
      if response != True:
        raise ResponseError("Unexpected response from server: %s" % (str(response)))
    else:
      self.attributes.append("jive")
 
    self.jive = status

  def clone(self):
    return cloneObject(self)
