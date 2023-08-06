
# This file is auto-generated from jubatus-generate/src/server/graph.idl
# *** DO NOT EDIT ***


import sys
import msgpack


class node:
  def __init__(self, property, in_edges, out_edges):
    self.property = property
    self.in_edges = in_edges
    self.out_edges = out_edges

  def to_msgpack(self):
    return (
      self.property,
      self.in_edges,
      self.out_edges,
      )

  @staticmethod
  def from_msgpack(arg):
    return node(
      {k_arg_0_ : v_arg_0_ for k_arg_0_,v_arg_0_ in arg[0].items()},
      [elem_arg_1_ for elem_arg_1_ in arg[1]],
      [elem_arg_2_ for elem_arg_2_ in arg[2]])

class preset_query:
  def __init__(self, edge_query, node_query):
    self.edge_query = edge_query
    self.node_query = node_query

  def to_msgpack(self):
    return (
      self.edge_query,
      self.node_query,
      )

  @staticmethod
  def from_msgpack(arg):
    return preset_query(
      [ (elem_arg_0_[0], elem_arg_0_[1])  for elem_arg_0_ in arg[0]],
      [ (elem_arg_1_[0], elem_arg_1_[1])  for elem_arg_1_ in arg[1]])

class edge:
  def __init__(self, property, source, target):
    self.property = property
    self.source = source
    self.target = target

  def to_msgpack(self):
    return (
      self.property,
      self.source,
      self.target,
      )

  @staticmethod
  def from_msgpack(arg):
    return edge(
      {k_arg_0_ : v_arg_0_ for k_arg_0_,v_arg_0_ in arg[0].items()},
      arg[1],
      arg[2])

class shortest_path_query:
  def __init__(self, source, target, max_hop, query):
    self.source = source
    self.target = target
    self.max_hop = max_hop
    self.query = query

  def to_msgpack(self):
    return (
      self.source,
      self.target,
      self.max_hop,
      self.query,
      )

  @staticmethod
  def from_msgpack(arg):
    return shortest_path_query(
      arg[0],
      arg[1],
      arg[2],
      preset_query.from_msgpack(arg[3]))


