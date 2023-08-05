#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""

from Connect import Connect
from Filtertransact import Filtertransact
from Clearcheckbook import Clearcheckbook

def login(username,password, useCache=True):
  dataUser=Connect(username, password)
  return Clearcheckbook( username, password, dataUser, useCache)   

def filter(username,password,data=None):
  dataUser=Connect(username, password)
  return Filtertransact(Clearcheckbook(username, password, dataUser, True), data) 
