import os
try:
  import configparser
except ImportError:
  import ConfigParser as configparser

CONFIG_FILE = os.path.expanduser('~/.graphitconfig')

class Config(object):
  
  def __init__(self,user_id=None,api_key=None):
    self.user_id = None
    self.api_key = None
    self.last_graph = None
    self.base_url = None
    if not user_id or not api_key:
      try:
        self.read_config()
      except:
        pass
    else:
      self.user_id = user_id
      self.api_key = api_key

  def read_config(self):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if not config.has_section('config') or not config.has_option('config', 'user_id') or not config.has_option('config', 'api_key')\
      or config.get('config', 'user_id') == "None" or config.get('config', 'api_key') == "None":
      raise Exception("No config or invalid config")

    self.user_id = None
    self.api_key = None
    self.last_graph = None
    self.base_url = None
    self.user_id = config.get('config', 'user_id')
    self.api_key = config.get('config', 'api_key')
    self.last_graph = config.get('config', 'last_graph')
    if config.has_option('config', 'base_url'):
      self.base_url = config.get('config', 'base_url')

  def save(self):
    if not self.user_id or not self.api_key:
      raise Exception("Can't save empty config")
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if not config.has_section('config'):
        config.add_section('config')
    config.set('config', 'user_id', self.user_id)
    config.set('config', 'api_key', self.api_key)
    try:
      if self.last_graph:
        config.set('config', 'last_graph', self.last_graph)
    except:
      pass
    configfile = open(CONFIG_FILE, 'w')
    config.write(configfile)
  def test_config(self):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if not config.has_section('config') or not config.has_option('config', 'user_id') or not config.has_option('config', 'api_key')\
      or config.get('config', 'user_id') == "None" or config.get('config', 'api_key') == "None":
        return False
    return True


config = Config()
