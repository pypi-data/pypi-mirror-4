#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""

from Exceptions import *
from Utils import *
from Account import *
from Category import *
from Transaction import *
from Reminder import *
from Limit import *

class Clearcheckbook:
  SPECIALATTRS=["CHECK_NUM", "MEMO", "PAYEE"]
  MEMO=CHECK_NUM=PAYEE={True:1, False:0}

  def __init__(self,username, password, dataUser, useCache):
    self.auth=(username,password)
    if useCache == True:
      self.cache={"accounts":{},"categories":{},"reminders":{},"limits":{}}
    else:
      self.cache=False
    loadDataToObject(self, dataUser)
    replaceAttributes(self, "fromOutside")

  def getAccounts(self,overview=False):
    return getAccountList(self.auth,self.cache,overview)
  
  def getAccount(self,accountId):
    return getAccountObjectFromId(self.auth,self.cache,accountId)

  def getAccountByName(self,name):
    return getAccountObjectFromName(self.auth,self.cache,name)

  def createAccount(self,name,accountType,initialBalance=0):
    try:
      accountType=Account.TYPE_ID[accountType]
    except:
      raise AccountError("%s is not a valid account type" % (accountType,))
    accountData={"name":name,"type_id":accountType,"initial_balance":initialBalance}
    account=Account(self.auth,self.cache,accountData)
    account.onCommit="create"
    account.commit()
    return account

  def getCategories(self):
    return getCategoryList(self.auth,self.cache)

  def getCategory(self,categoryId):
    return getCategoryObjectFromId(self.auth,self.cache,categoryId)

  def getCategoryByName(self,name):
    return getCategoryObjectFromName(self.auth,self.cache,name)

  def createCategory(self,name,parent=0):
    categoryData={}
    if parent != 0 and self.getCategory(parent) == False:
      raise CategoryNotFoundError("parent category ID %s not found" % (parent,))
    categoryData["parent"]=parent #FIXME: Acording to the API, parent is optional but if not set the category has parent=null instead of parent=0 !! FIXME
    categoryData["name"]=name
    category=Category(self.auth,self.cache,categoryData)
    category.onCommit="create"
    category.commit()
    return category

  def deleteCategory(self, categoryId):
    category=self.getCategory(categoryId)

  def getLimits(self):
    return getLimitList(self.auth, self.cache)    
 
  def getLimit(self, limitid):
    return getLimitFromId(self.auth, self.cache, reminderId)

  def getLimitByName(self, name):
    return getLimitObjectFromName(self.auth, self.cache, name)

  def createLimit(self, name, reset_day):
    limit=Limit(self.auth, self.cache, {"name":name,"reset_day":reset_day})
    limit.onCommit="create"
    limit.commit()
    return limit
 
  def getTransactionById(self, id):
    return getTransaction(self.auth, self.cache, id)
 
  def getTransactions(self,page=1,limit=100,accountId=False):
    return getTransactionsData(self.auth,self.cache,accountId,page,limit)

  def createTransact(self, date, amount, transaction_type, account, category, description):
    if category is None:
      category_id=0
    else:
      category_id=self.getCategoryByName(category).id
    if account is None:
      account=0
    else:
      account_id=self.getAccountByName(account).id

    transact=Transaction(self.auth, self.cache, {"date":date,"transaction_type":transaction_type,\
    "account_id":account_id,"category_id":category_id,"amount":amount,"description":description})
    transact.onCommit="create"
    return transact

  def getNextReminders(self, days=False):
    return getReminderList(self.auth, self.cache, days) 

  def getReminder(self,reminderId):
    return getReminderFromId(self.auth,self.cache,reminderId) 

  def getReminderByName(self,name):
    return getReminderObjectFromName(self.auth,self.cache,name) 

  def createReminder(self,name,parent=0):
    return None


