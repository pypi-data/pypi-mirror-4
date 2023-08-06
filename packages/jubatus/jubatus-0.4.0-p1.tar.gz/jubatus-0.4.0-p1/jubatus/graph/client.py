
# This file is auto-generated from jubatus-generate/src/server/graph.idl
# *** DO NOT EDIT ***


import msgpackrpc
from types import *


class graph:
  def __init__ (self, host, port):
    address = msgpackrpc.Address(host, port)
    self.client = msgpackrpc.Client(address)

  def get_config (self, name):
    retval = self.client.call('get_config', name)
    return retval

  def create_node (self, name):
    retval = self.client.call('create_node', name)
    return retval

  def remove_node (self, name, node_id):
    retval = self.client.call('remove_node', name, node_id)
    return retval

  def update_node (self, name, node_id, property):
    retval = self.client.call('update_node', name, node_id, property)
    return retval

  def create_edge (self, name, node_id, e):
    retval = self.client.call('create_edge', name, node_id, e)
    return retval

  def update_edge (self, name, node_id, edge_id, e):
    retval = self.client.call('update_edge', name, node_id, edge_id, e)
    return retval

  def remove_edge (self, name, node_id, edge_id):
    retval = self.client.call('remove_edge', name, node_id, edge_id)
    return retval

  def get_centrality (self, name, node_id, centrality_type, query):
    retval = self.client.call('get_centrality', name, node_id, centrality_type, query)
    return retval

  def add_centrality_query (self, name, query):
    retval = self.client.call('add_centrality_query', name, query)
    return retval

  def add_shortest_path_query (self, name, query):
    retval = self.client.call('add_shortest_path_query', name, query)
    return retval

  def remove_centrality_query (self, name, query):
    retval = self.client.call('remove_centrality_query', name, query)
    return retval

  def remove_shortest_path_query (self, name, query):
    retval = self.client.call('remove_shortest_path_query', name, query)
    return retval

  def get_shortest_path (self, name, query):
    retval = self.client.call('get_shortest_path', name, query)
    return [elem_retval for elem_retval in retval]

  def update_index (self, name):
    retval = self.client.call('update_index', name)
    return retval

  def clear (self, name):
    retval = self.client.call('clear', name)
    return retval

  def get_node (self, name, node_id):
    retval = self.client.call('get_node', name, node_id)
    return node.from_msgpack(retval)

  def get_edge (self, name, node_id, edge_id):
    retval = self.client.call('get_edge', name, node_id, edge_id)
    return edge.from_msgpack(retval)

  def save (self, name, id):
    retval = self.client.call('save', name, id)
    return retval

  def load (self, name, id):
    retval = self.client.call('load', name, id)
    return retval

  def get_status (self, name):
    retval = self.client.call('get_status', name)
    return {k_retval : {k_v_retval : v_v_retval for k_v_retval,v_v_retval in v_retval.items()} for k_retval,v_retval in retval.items()}

  def create_node_here (self, name, node_id):
    retval = self.client.call('create_node_here', name, node_id)
    return retval

  def remove_global_node (self, name, node_id):
    retval = self.client.call('remove_global_node', name, node_id)
    return retval

  def create_edge_here (self, name, edge_id, e):
    retval = self.client.call('create_edge_here', name, edge_id, e)
    return retval



