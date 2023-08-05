import grokpy

from grokpy.exceptions import GrokError

class DataSourceField(object):
  '''
  A local object used to build up a stream specification
  '''

  def __init__(self):

    # Default empty values
    self.name = None

    self.type = None

    self.aggregationFunction = None

    self.flag = None

    self.minValue = None

    self.maxValue = None

  def setName(self, name):
    '''
    Updates the local name of this field

    * name - A short string describing this field.
    '''

    # Length check
    maxLen = 255
    if len(name) > maxLen:
      raise GrokError('This name is too large. The limit is %d characters'
                      % maxLen)

    self.name = name

  def setType(self, dataType):
    '''
    Updates the local type of this field

    * type - A grokpy.DataType enum value
    '''

    # Yuk.
    validTypes = [value for value in grokpy.DataType.__dict__.values() if
                  isinstance(value, str)]

    if dataType not in validTypes:
      raise GrokError('Invalid field type. Please pass a grokpy.DataType value')

    self.type = dataType

  def setFlag(self, flag):
    '''
    Optional - Sets a flag locally for this field.

    * flag - A grokpy.DataFlag enum value
    '''

    # Yuk.
    validFlags = [value for value in grokpy.DataFlag.__dict__.values() if
                  isinstance(value, str)]

    if flag not in validFlags:
      raise GrokError('Invalid field flag. Please pass a '
                      'grokpy.DataFlag value')

    self.flag = flag

  def setAggregationFunction(self, aggregationFunction):
    '''
    Sets the function by which we will aggregate values in this field if a
    time aggregation is specified for the whole model.

    * aggregationFunction - A grokpy.AggregationFunction enum value.
    '''

    # Type checking
    if not self.type:
      raise GrokError('Please set a type for this field before specifying its '
                      'aggregation function.')
    if (self.type == grokpy.DataType.CATEGORY or
        self.type == grokpy.DataType.DATETIME):
      if aggregationFunction in [grokpy.AggregationFunction.AVERAGE,
                                 grokpy.AggregationFunction.SUM]:
        raise GrokError('The valid aggregation functions for CATEGORY and '
                        'DATETIME fields are FIRST or LAST')

    self.aggregationFunction = aggregationFunction

  def setMin(self, minValue):
    '''
    Optional - Tells Grok what the minimum value for this field will be

    * minValue - A float
    '''
    # Check that the value passed is a number
    if not isinstance(minValue, (int, long, float)):
      raise GrokError('Min values can only be numbers')

    self._assertType(grokpy.DataType.SCALAR)

    self.minValue = minValue

  def setMax(self, maxValue):
    '''
    Optional - Tells Grok what the minimum value for this field will be

    * minValue - A float
    '''

    # Check that the value passed is a number
    if not isinstance(maxValue, (int, long, float)):
      raise GrokError('Max values can only be numbers')

    self._assertType(grokpy.DataType.SCALAR)

    self.maxValue = maxValue

  def getSpec(self):
    '''
    Returns the constructed dict representation of this field
    '''

    if not self.name or not self.type:
      raise GrokError('Please set both a name and a type for this field')

    returnSpec = {"name": self.name,
                  "dataFormat": {"dataType": self.type}}

    if self.flag:
      returnSpec['flag'] = self.flag

    if self.maxValue:
      returnSpec['max'] = self.maxValue

    if self.minValue:
      returnSpec['min'] = self.minValue

    if self.aggregationFunction:
      returnSpec['aggregationFunction'] = self.aggregationFunction


    return returnSpec

  #############################################################################
  # Private methods

  def _assertType(self, dataType):

    if dataType != self.type:
      print dataType, self.type
      raise GrokError('Setting this value requires a field of data type %s. '
                      'Please make sure to call setType first with an '
                      'appropriate value.' % grokpy.DataType.SCALAR)
