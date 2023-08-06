import grokpy

from grokpy.exceptions import GrokError

class LocalDataSource(object):
  '''
  A specification object for adding local data to your stream
  '''

  def __init__(self):

    # Our list of fields in this source
    self.fields = []

    self.name = None

  def setName(self, name):
    '''
    Sets the name of this source locally.

    * name - A short string describing this data source
    '''
    self.name = name

  def addField(self, dataSourceField):
    '''
    Adds a field to the local list of fields defining the local source.

    * dataSourceField - A DataSourceField object
    '''

    self.fields.append(dataSourceField)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification.
    Usually consumed by an instance of the StreamSpecification class.
    '''

    if not self.name:
      raise GrokError('Please set a name for this data source')

    returnSpec = {"name": self.name,
                 "dataSourceType": "local",
                 "fields": []}

    for field in self.fields:
      returnSpec['fields'].append(field.getSpec())

    return returnSpec
