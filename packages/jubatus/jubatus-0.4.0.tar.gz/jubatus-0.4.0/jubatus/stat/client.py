
# This file is auto-generated from jubatus-generate/src/server/stat.idl
# *** DO NOT EDIT ***


import msgpackrpc
from types import *


class stat:
  def __init__ (self, host, port):
    address = msgpackrpc.Address(host, port)
    self.client = msgpackrpc.Client(address)

  def get_config (self, name):
    retval = self.client.call('get_config', name)
    return retval

  def push (self, name, key, value):
    retval = self.client.call('push', name, key, value)
    return retval

  def sum (self, name, key):
    retval = self.client.call('sum', name, key)
    return retval

  def stddev (self, name, key):
    retval = self.client.call('stddev', name, key)
    return retval

  def max (self, name, key):
    retval = self.client.call('max', name, key)
    return retval

  def min (self, name, key):
    retval = self.client.call('min', name, key)
    return retval

  def entropy (self, name, key):
    retval = self.client.call('entropy', name, key)
    return retval

  def moment (self, name, key, degree, center):
    retval = self.client.call('moment', name, key, degree, center)
    return retval

  def save (self, name, id):
    retval = self.client.call('save', name, id)
    return retval

  def load (self, name, id):
    retval = self.client.call('load', name, id)
    return retval

  def get_status (self, name):
    retval = self.client.call('get_status', name)
    return {k_retval : {k_v_retval : v_v_retval for k_v_retval,v_v_retval in v_retval.items()} for k_retval,v_retval in retval.items()}



