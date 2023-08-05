#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2012 Oscar Curero

This code is free software; you can redistribute it and/or modify it
under the terms of the GPL 3 license (see the file
COPYING.txt included with the distribution).
"""
  
class ConnectionError(Exception):
  def __str__(self):
    return "Unable to connect to www.clearcheckbook.com"

class AuthError(Exception):
  def __str__(self):
    return "Authentification failed"

class CommitError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Commit Error: " + repr(self.value)

class AccountNotFoundError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "AccountID does not exist: " + repr(self.value)

class AccountError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Account Error: " + repr(self.value)

class CategoryNotFoundError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Category does not exist: " + repr(self.value)

class CategoryError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Category Error: " + repr(self.value)

class ReminderNotFoundError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Reminder does not exist: " + repr(self.value)

class DeleteError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Server returned False"


class CacheError(Exception): 
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Cache Error: " + repr(self.value)

class ResponseError(Exception): 
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Response error: " + repr(self.value)


