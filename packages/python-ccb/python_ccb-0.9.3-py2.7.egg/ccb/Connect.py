#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""

from Exceptions import *
from Clearcheckbook import Clearcheckbook 
from Utils import sendCommand
from httplib2 import ServerNotFoundError

def Connect(username,password):
  try:
    response=sendCommand("GET","premium",None,(username,password))
  except ServerNotFoundError:
    raise ConnectionError()
  if response == "login failed":
    raise AuthError()
  else:
    return response
