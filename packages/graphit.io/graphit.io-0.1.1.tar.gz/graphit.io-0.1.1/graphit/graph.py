from .config import config
from . import util
import requests
import json

class Graph(object):
  def __init__(self,graph_id):
    self.id = graph_id
  def read(self):
    res = requests.get(util.api_graph_path(self.id), headers=util._build_headers())
    res.raise_for_status()
    self.__dict__.update(**res.json()) #Import dict entries to class object
    return res
  def update(self, **ops):

    res = requests.put(util.user_graph_path(config.user_id,self.id),
            data = json.dumps(ops),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()
    
  def destroy(self):
    res = requests.delete(util.user_graph_path(config.user_id, self.id), headers=util._build_headers(auth=True))
    res.raise_for_status()

  def add(self,x, y, series=None, xlabel=None, ylabel=None, update=False):
    graph_data = [{'series': series, 'x': {'value':x, 'label': xlabel}, 'y': {'value':y, 'label': ylabel}}]
    res = requests.post(
            util.user_graph_data_path(config.user_id, self.id,update),
            data = json.dumps(graph_data),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()
  # def add_data(self, data, build_func,update=False):
  #   all_data = []
  #   for record in enumerate(data):
  #     (x,y,series) = build_func(record)
  #     all_data.append({'series': series, 'x': {'value':x}, 'y': {'value':y}})
  #   res = requests.post(
  #           util.user_graph_data_path(config.user_id, self.id,update),
  #           data = json.dumps(all_data),
  #           headers = util._build_headers(auth=True, content=True))
  #   res.raise_for_status()
  def add_data_set(self, data_set,update=False):
    res = requests.post(  
            util.user_graph_data_path(config.user_id, self.id,update),
            data = json.dumps(data_set.to_hash()),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()

  def delete_data(self, less_than=None, greater_than=None, all_data=False, update=False):
    del_data = {}
    if less_than:
      del_data['less_than'] = less_than
    if greater_than:
      del_data['greater_than'] = greater_than
    if all_data:
      del_data['all'] = True
    res = requests.delete(
            util.user_graph_data_path(config.user_id, self.id,update), 
            data = json.dumps(del_data),
            headers=util._build_headers(auth=True,content=True))
    res.raise_for_status()
  def url(self):
    return util.graph_path(self.id)
