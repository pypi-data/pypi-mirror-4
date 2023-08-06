

"""
graphit - Graphit.io Client Library
-----------------------------------

Graphit.io allows you to create embeddable Javascript Graphs via
a JSON REST API. This is the Python Library to access it using
the requests library.

usage:

  >>> import graphit
  >>> g = graphit.new_graph(name="Bogus Data", x_label="Time", y_label="Temperature")
  >>> g.add(x=0, y=3)
  >>> g.update()

  OR, create data set

  >>> ds = graphit.DataSet()
  >>> ds.add(x=0, y=2)
  >>> ds.add(x=1, y=3)
  >>> g.add_data_set(ds, update=True)

"""

from .config import config
from . import util
from .interface import *
from .data import Datum, DataSet

