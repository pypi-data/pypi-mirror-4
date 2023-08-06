
class Datum(object):
  def __init__(self,x_value,y_value,series=None,xlabel=None,ylabel=None):
    self.x_value = x_value
    self.y_value = y_value
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.series = series
  def to_hash(self):
    dh = {'x': {'value':self.x_value, 'label':self.xlabel}, 'y': {'value':self.y_value, 'label':self.ylabel}}
    if self.series:
        dh['series'] = self.series
    return dh

class DataSet(object):
  def __init__(self):
    self.data = []
  def add_datum(self, datum):
     self.data.append(datum)
  def add_raw_datum(self, x_value, y_value, series=None,xlabel=None,ylabel=None):
    self.data.append(Datum(x_value, y_value, series, xlabel, ylabel))
  def to_hash(self):
    final_data = []
    for datum in self.data:
        final_data.append(datum.to_hash())
    return final_data
