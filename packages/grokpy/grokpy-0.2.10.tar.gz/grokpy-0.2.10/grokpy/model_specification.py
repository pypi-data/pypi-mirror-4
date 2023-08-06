import grokpy

from grokpy.exceptions import GrokError, NotYetImplementedError

class ModelSpecification(object):
  '''
  This is a client level object that is useful for building Model
  Specifications in an object oriented way. (As opposed to writing the JSON
  or Dict directly).
  '''

  def __init__(self):

    # What is the name of this model
    self.name = ''

    # What stream should this model listen to
    self.streamId = None

    # What aggregation will this model use
    self.aggInt = None

    # Per field aggregation function overrides
    self.aggOverrides = []

    # computeInterval
    self.computeInt = None

    # List of steps into the future to predict
    self.steps = [1]

    # Custom error expression and window
    self.customErrorExpression = None
    self.customErrorAveragingWindow = None

    # Type of model:
    #    grokpy.ModelType.PREDICTOR - standard predictor model
    #    grokpy.ModelType.ANOMALY   - model optimized for anomaly detection
    self.modelType = grokpy.ModelType.PREDICTOR

  def setName(self, name):
    '''
    Updates the local name.
    '''
    self.name = name

  def setPredictedField(self, predictedField):
    '''
    Sets the field the model will attempt to predict. Swarm will evaluate
    models based on the models ability to predict this field.

    * predictedField - String. A field name as it appears in the stream
                       specification.
    '''

    self.predictedField = predictedField

  def setStream(self, streamId):
    '''
    Sets which stream the model will listen to.

    * streamId - String. A 36 char unique id for a Stream OR grokpy.Stream
                 object from which a stream id will be extracted.
    '''

    if isinstance(streamId, grokpy.Stream):
      self.streamId = streamId.id
    elif len(streamId) == 36:
      self.streamId = streamId
    else:
      raise GrokError('This does not appear to be a properly formatted stream '
                      'id.')

  def setAggregationInterval(self, aggInt):
    '''
    Defines the interval Grok will use to aggregate incoming records over.

    * aggInt - Dict.

    Example::

        interval = {'hours': 1,
                    'minutes': 15}

        modelSpec.setAggregationInterval(interval)
    '''

    self.aggInt = aggInt

  def setAggFuncOverrides(self, aggOverrides):
    '''
    Overrides the aggregation functions for fields in a stream to which this
    model is attached.

    * aggOverrides - A list of tuples in the form (fieldName, aggFunc)

    Example Usage::

      When creating a stream you might specify that the field 'Energy' should
      be aggregated using grokpy.AggregationFunction.AVERAGE. However
      for this particular model you might want to re-use the same stream
      but have aggregation sum values over the aggregation interval
      rather than average them.

      model.setAggFuncOverrides([('Energy', grokpy.AggregationFunction.SUM)])
    '''

    if not self.aggInt:
      raise GrokError('Please set an aggregation interval if you want to '
                      'override field aggregation functions.')

    if type(aggOverrides) != type([]):
      raise GrokError('aggOverrides must be a list of tuples.')

    self.aggOverrides = aggOverrides

  def setComputeInterval(self, computeInt):
    ''' Defines the interval at which Grok will to make predictions.

    * computeInt - Dict.

    Example::

        This is closely tied to aggregation interval. If you have input records
        every 15 minutes, and aggregate hourly, by default you will get a
        prediction every four records you send in. If you only need a prediction
        every 4 hours you would set a compute interval of four hours and you
        would then get one prediction for every 16 records you sent in.

        interval = {'hours': 4}

        modelSpec.setComputeInterval(computeInt)
    '''

    self.computeInt = computeInt

  def setPredictionSteps(self, steps = [1]):
    '''
    Adds a list of steps in the future to predict.

    * steps - A list of integers. The default is to predict one timestep into
              the future.

    Example Usage::

      To get predictions for the next three timesteps

      model.setPredictionSteps([1,2,3])

      To get predictions for the next three timesteps where you care most
      about accuracy three steps out

      model.setPredictionSteps([3,1,2])

      The first item in the list is the optimized timestep. The swarm will find
      a model that does best at predicting that number of steps into the future.
    '''

    if not steps:
      raise GrokError('Steps must be a list and have at least one value.')

    if len(steps) > 10:
      raise GrokError('Max number of values for "steps" is 10. Note you can '
                      'request 20 steps into the future (steps = [20]), just '
                      'not all 20 at once (steps = [1, ... 20]')

    self.steps = steps

  def setCustomErrorMetric(self, customExpr, errorWindow = 1):
    '''
    Adds a custom error metric the model will use to evaluate predictions at
    each timestep. The Swarm will use this error metric to pick model
    configurations that minimize the error value.

    * customExpr - A string version of valid python. This would be the inner
                   section of a function definition without the 'def' line.
    * errorWindow - the window over which the error should be averaged. This
                    takes the per-record error generated by the custom error
                    metric, sums it for the desired window and divides it by
                    the size of the window. The possible values are:

                    * 1 - returns the single per-record error metric. This should
                          be chosen if you are doing the averaging inside your
                          metric.
                    * N - causes the per record error to be averaged over the last
                          N records. -1 - causes the error to be averaged since
                          the beginning of the dataset.
                    * 0 - is not supported and will cause an assertion failure.


    Within your expression (customExpr) you will have access to the following:

      * prediction - the prediction provided by the current model.
      * groundTruth - the ground truth provided by the data record.
      * tools - the tools object with an interface identical that which is used
                in the customFuncSource implementation (see above for details).
      * EXP - The expected value from the probability distribution provided by
              the current model.
      * probabilityDistribution - The full probability distribution provided by
                                  the current model, in the form of a dict
                                  where the key is the prediction and the value
                                  is the probability.

    Example::

      Absolute average error over the last 100 records (customExpr)

      customExpr = "abs(prediction - groundTruth)"
      errorWindow = 100
      model.setCustomErrorMetric(customExpr, errorWindow)

    '''

    try:
      encodedCustomExpr = customExpr.encode('string_escape')
    except AttributeError:
      raise GrokError('customExpr must be a string that can be encoded using \
                      encode("string_escape")')

    self.customErrorExpression = encodedCustomExpr
    self.customErrorAveragingWindow = errorWindow

  def setType(self, modelType):
    '''
    Defines the type of model to be run.

    * modelType - string.  Must be one of the grokpy.ModelType options:
                            * grokpy.ModelType.ANOMALY
                            * grokpy.ModelType.PREDICTOR

    If ModelType.ANOMALY, the model will return AnomalyScore and will be
    optimized for anomaly detection.

    Example::

        modelSpec.setType(grokpy.ModelType.PREDICTOR)

    '''
    if type(modelType) != str or \
       modelType not in [grokpy.ModelType.ANOMALY, grokpy.ModelType.PREDICTOR]:
      raise GrokError("Model type must be one of the grokpy.ModelType options.")

    self.modelType = modelType


  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification
    '''

    if not self.name:
      raise GrokError('Please set a name for this model')

    if not self.streamId:
      raise GrokError('Please set a stream id for this model spec.')

    returnSpec = {"name": self.name,
                  "predictedField": self.predictedField,
                  "streamId": self.streamId,
                  "predictionSteps": self.steps}

    returnSpec['modelType'] = self.modelType

    if self.aggInt:
      returnSpec['aggregation'] = {}
      returnSpec['aggregation']['interval'] = self.aggInt

      if self.aggOverrides:
        returnSpec['aggregation']['fields'] = self.aggOverrides

    if self.customErrorExpression:
      returnSpec['customErrorMetric'] = {'customExpr': self.customErrorExpression,
                                         'errorWindow': self.customErrorAveragingWindow}

    return returnSpec
