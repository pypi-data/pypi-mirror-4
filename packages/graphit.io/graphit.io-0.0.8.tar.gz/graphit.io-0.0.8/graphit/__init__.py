

"""
graphit - Graphit.io Client Library
-----------------------------------

Graphit.io allows you to create embeddable Javascript Graphs via
a JSON REST API. This is the Python Library to access it using
the requests library.

usage:

  >>> import graphit
  >>> g = graphit.new_graph("Bogus Data", x_label="Time", y_label="Temperature")
  >>> g.add_datum(x_value=0, y_value=Temp.read())
  >>> g.update()

  OR, pass fuction to generate data

  >>> mydata = (1, 2, 3, 4, 5)
  >>> g.add_data(mydata, lambda r,i: graphit.Datum(i, r))
  >>> g.update()

  OR, create data set

  >>> ds = graphit.DataSet()
  >>> ds.add_datum(0, 2)
  >>> ds.add_datum(1, 3)
  >>> g.add_data_set(ds, update=True)

"""

from .config import config
from . import util
from .interface import *
from .data import Datum, DataSet

