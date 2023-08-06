
import json
import requests
from .config import config
from .graph import Graph
from . import util

def new_graph(**ops):

  res = requests.post(util.user_graphs_path(config.user_id),
          data = json.dumps(ops),
          headers =util._build_headers(auth=True, content=True))
  res.raise_for_status()
  g = Graph(res.json()['_id'])
  return g

def find_graph(name=None,graph_id=None):
  if graph_id:
    return Graph(graph_id)
  if name:
    all_graphs = list_graphs()
    for graph in all_graphs:
      if graph['name'] == name:
        return Graph(graph['_id'])
    raise Exception("Graph not found")

def list_graphs():
  res = requests.get(util.user_graphs_path(config.user_id), headers=util._build_headers(auth=True))
  res.raise_for_status()
  return res.json()

