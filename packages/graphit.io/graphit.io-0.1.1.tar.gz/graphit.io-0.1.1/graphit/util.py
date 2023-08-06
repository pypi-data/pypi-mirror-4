
from .config import config

BASE_URL = 'https://graphit.io'
if config.base_url:
  BASE_URL = config.base_url
API_URL = BASE_URL + "/api"


def graph_path(graph_id):
  return "%s/graphs/%s"%(BASE_URL, graph_id)

def api_graph_path(graph_id):
  return "%s/graphs/%s"%(API_URL, graph_id)

def user_graph_path(user_id, graph_id):
  return "%s/users/%s/graphs/%s"%(API_URL, user_id, graph_id)

def user_graphs_path(user_id):
  return "%s/users/%s/graphs"%(API_URL, user_id)

def user_graph_data_path(user_id, graph_id,update=False):
  url = "%s/users/%s/graphs/%s/data"%(API_URL, user_id, graph_id)
  if update:
    url += "?update=true"
  return url

def _build_headers(content=False,auth=False,version=1):
  headers = {}
  if content:
    headers['Content-Type'] = 'application/json'
  if auth:
    headers['Authorization'] = 'Token token="%s"'%config.api_key
  if version:
    headers['Accept'] = 'application/graphit.io; version=%d'%version
  return headers

def working_graph(args):
  if args.graphid:
    return args.graphid
  elif config.last_graph and config.last_graph != "None":
    return config.last_graph
  else:
    return None
