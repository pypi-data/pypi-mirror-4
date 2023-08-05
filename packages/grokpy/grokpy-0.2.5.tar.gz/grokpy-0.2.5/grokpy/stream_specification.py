import grokpy

from grokpy.exceptions import GrokError

class StreamSpecification(object):
  '''
  This is a client level object that is useful for building Stream
  Specifications in an object oriented way. (As opposed to writing the JSON
  directly). By adding dataSources you can add both local and public data
  to your stream.
  '''

  def __init__(self):

    # What is the name of this stream
    self.name = ''

    # What data sources are in this stream
    self.dataSources = []

    # What type of prediction models will make when listening to this stream
    self.predictionType = ''

  def setName(self, name):
    '''
    Updates the local name.
    '''
    self.name = name

  def setPredictionType(self, predictionType):
    '''
    .. warning:: This method is temporary and may move to the model class

    Sets the prediction type that models will produce when consuming data
    from this stream

    * predictionType - A grokpy.PredictionType enum value
    '''

    self.predictionType = predictionType

  def addDataSource(self, dataSource):
    '''
    Adds the data source to the local list of data sources for later assembly
    into a descriptive dict.
    '''

    # Data sources must implement a getSpec() method
    if 'getSpec' not in dir(dataSource):
      raise GrokError('Data source objects must implement at least a getSpec '
                      'method that returns a python dict.')

    self.dataSources.append(dataSource)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification
    '''

    if self.name == '':
      raise GrokError('Please set a name for this stream')

    if self.dataSources == []:
      raise GrokError('Please add at least one dataSource to this '
                      'specification.')

    returnSpec = {"name": self.name,
                 "dataSources": []}

    if self.predictionType:
      returnSpec['flags'] = self.predictionType

    for dataSource in self.dataSources:
      returnSpec['dataSources'].append(dataSource.getSpec())

    return returnSpec
