
# This file is auto-generated from jubatus-generate/src/server/anomaly.idl
# *** DO NOT EDIT ***


import msgpackrpc
from types import *


class anomaly:
  def __init__ (self, host, port):
    address = msgpackrpc.Address(host, port)
    self.client = msgpackrpc.Client(address)

  def get_config (self, name):
    retval = self.client.call('get_config', name)
    return retval

  def clear_row (self, name, id):
    retval = self.client.call('clear_row', name, id)
    return retval

  def add (self, name, row):
    retval = self.client.call('add', name, row)
    return  (retval[0], retval[1]) 

  def update (self, name, id, row):
    retval = self.client.call('update', name, id, row)
    return retval

  def clear (self, name):
    retval = self.client.call('clear', name)
    return retval

  def calc_score (self, name, row):
    retval = self.client.call('calc_score', name, row)
    return retval

  def get_all_rows (self, name):
    retval = self.client.call('get_all_rows', name)
    return [elem_retval for elem_retval in retval]

  def save (self, name, id):
    retval = self.client.call('save', name, id)
    return retval

  def load (self, name, id):
    retval = self.client.call('load', name, id)
    return retval

  def get_status (self, name):
    retval = self.client.call('get_status', name)
    return {k_retval : {k_v_retval : v_v_retval for k_v_retval,v_v_retval in v_retval.items()} for k_retval,v_retval in retval.items()}



