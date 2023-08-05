#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""

from Utils import *
from . import Connect
from Exceptions import *
from Base import *
from Transaction import *
from decimal import *
import sqlite3


def convertDecimal(convert):
  return str(convert)


class Filtertransact(sqlite3.Connection):

  DDL="CREATE TABLE transact (id INTEGER PRIMARY KEY, date TEXT, amount REAL, transaction_type TEXT, description TEXT, account_id TEXT, category_id TEXT, jive INTEGER, specialstatus TEXT, parent INTEGER, related_transfer INTEGER, check_num TEXT, memo TEXT, payee TEXT, initial_balance INTEGER, checkbot_id INTEGER, user_id INTEGER, created_at TEXT, additional_user_id INTEGER, ccparent INTEGER)"
  sqlite3.register_adapter(Decimal, convertDecimal)

  def __init__(self,session,data=None):
    self.session=session # get clearcheckbook object
    sqlite3.register_adapter(Decimal, convertDecimal)
    sqlite3.Connection.__init__(self,":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor=self.cursor()
    cursor.execute(self.DDL)
    self.columns=[]
    for column in cursor.execute("SELECT * FROM transact").description:
      self.columns.append(column[0])
    self.columns=tuple(self.columns)

  def loadTransactList(self,transactList):
    for transact in transactList:
      self.loadTransact(transact)

  def loadTransact(self,transact):
    attributeList=[]
    if transact.account_id is not None:
      transact.account_id=transact.getAccount().name
    if transact.category_id is not None:
      transact.category_id=transact.getCategory().name    
    
    for attribute in self.columns:
      attributeValue=getattr(transact,attribute)
      if attributeValue is False:
        attributeValue=0
      elif attributeValue is True:
        attributeValue=1
      elif attributeValue is None:
        attributeValue=""
      if attribute == "initial_balance" and attributeValue == None:      # FIXME: initial_balance return "null", but it should return false!
        attributeValue=0                                                 #
      elif attribute == "initial_balance" and attributeValue != None:    #
        attributeValue=1                                                 #
      attributeList.append(attributeValue)

    if not hasattr(self,"loadCursor"):
      self.loadCursor=self.cursor()
      
    self.loadCursor.execute("INSERT INTO transact values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", attributeList)

  def cursor(self):
    return FilterCursor(self, self.session)  

  def loadAllTransact(self):
    self.loadTransactList(self.session.getTransactions(0,0)) #get all transactions 
  
class FilterCursor(sqlite3.Cursor):
  
  def __init__(self,connection, session):
    sqlite3.Cursor.__init__(self, connection)
    self.auth=session.auth
    self.cache=session.cache
    self.session=session
 
  def unloadTransact(self):
    transactList=[]
    while True:
      rowSet=self.fetchone()
      if rowSet is None:
        break
      else:
         rowSet=list(rowSet)

      transact=Transaction(self.auth, self.cache)
      
      for columnName in self.description:
        attributeValue=rowSet.pop(0)
        setattr(transact, columnName[0], attributeValue)
      if hasattr(transact,"category_id") and transact.category_id != '':
        transact.category_id=self.session.getCategoryFromName(transact.category_id).id
      else:
        transact.category_id=None
      if hasattr(transact,"account_id") and transact.account_id != '':
        transact.account_id=self.session.getAccountFromName(transact.account_id).id
      else:
        transact.account_id=None
      if hasattr(transact,"id"):
        transact.onCommit="modify"
      else:
         transact.onCommit="abort"
      
      transactList.append(transact)

    return tuple(transactList)    
 
