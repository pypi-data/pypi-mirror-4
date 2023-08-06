from .config import config
from . import util
import requests
import json

class Graph(object):
  def __init__(self,graph_id):
    self.graph_id = graph_id
    self._id = self.graph_id
  def read(self):
    res = requests.get(util.api_graph_path(self.graph_id), headers=util._build_headers())
    res.raise_for_status()
    self.__dict__.update(**res.json()) #Import dict entries to class object
    return res
  def update(self, ops={}):

    res = requests.put(util.user_graph_path(config.user_id,self._id),
            data = json.dumps(ops),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()
    
  def destroy(self):
    res = requests.delete(util.user_graph_path(config.user_id, self._id), headers=util._build_headers(auth=True))
    res.raise_for_status()

  def add_datum(self,x_value, y_value, series=None, xlabel=None, ylabel=None, update=False):
    graph_data = [{'series': series, 'x': {'value':x_value, 'label': xlabel}, 'y': {'value':y_value, 'label': ylabel}}]
    res = requests.post(
            util.user_graph_data_path(config.user_id, self._id,update),
            data = json.dumps(graph_data),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()
  def add_data(self, data, build_func,update=False):
    all_data = []
    for idx, record in enumerate(data):
      d = build_func(record,idx)
      all_data.append({'series': g.series, 'x': {'value':d.x_value}, 'y': {'value':d.y_value}})
    res = requests.post(
            util.user_graph_data_path(config.user_id, self._id,update),
            data = json.dumps(all_data),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()
  def add_data_set(self, data_set,update=False):
    res = requests.post(  
            util.user_graph_data_path(config.user_id, self._id,update),
            data = json.dumps(data_set.to_hash()),
            headers = util._build_headers(auth=True, content=True))
    res.raise_for_status()

  def delete_data(self, less_than=None, greater_than=None,update=False):
    del_data = {}
    if less_than:
      del_data['less_than'] = less_than
    if greater_than:
      del_data['greater_than'] = greater_than
    res = requests.delete(
            util.user_graph_data_path(config.user_id, self._id,update), 
            data = json.dumps(del_data),
            headers=util._build_headers(auth=True,content=True))
    res.raise_for_status()
  def url(self):
    return util.graph_path(self._id)
