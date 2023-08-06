
class Datum(object):
  def __init__(self,x,y,series=None,xlabel=None,ylabel=None):
    self.x = x
    self.y = y
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.series = series
  def to_hash(self):
    dh = {'x': {'value':self.x, 'label':self.xlabel}, 'y': {'value':self.y, 'label':self.ylabel}}
    if self.series:
        dh['series'] = self.series
    return dh

class DataSet(object):
  def __init__(self):
    self.data = []
  def add_datum(self, datum):
     self.data.append(datum)
  def add(self, x, y, series=None,xlabel=None,ylabel=None):
    self.data.append(Datum(x, y, series, xlabel, ylabel))
  def to_hash(self):
    final_data = []
    for datum in self.data:
        final_data.append(datum.to_hash())
    return final_data
