import os
import time
import json
import warnings
import grokpy

from exceptions import GrokError, AuthenticationError, NotYetImplementedError
from swarm import Swarm

VERBOSITY = 0

class Model(object):
  '''
  Object representing a Grok Model.

  * parent - **Either** a `Client` or `Project`.
  * modelDef - A dict, usually returned from a model creation or get action.
    Usually includes:

    * id
    * name
    * streamId
    * swarmsUrl
    * url
  '''

  def __init__(self, parent, modelDef):

    # Give streams access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(modelDef)

    # Prepare to have a swarm associated with the model
    self.swarm = None

  def _runCommand(self, command, **params):
    url = self.commandsUrl
    commandObject = {'command': command}

    if params:
      commandObject['params'] = params

    result = self.c.request('POST', url, commandObject)
    return result

  def delete(self):
    '''
    Permanently deletes the model

    .. warning:: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  def clone(self, params = None):
    '''
    Clones this model
    '''

    if params:
      result = self.c.request('POST', self.cloneUrl, {'model': params})
    else:
      result = self.c.request('POST', self.cloneUrl)

    return Model(self.parent, result['model'])

  #############################################################################
  # Model Configuration

  def setName(self, newName):
    '''
    Renames the model.

    * newName - String
    '''

    # Get the current model state
    modelDef = self.getState()

    # Update the definition
    modelDef['name'] = newName

    # Update remote state
    self.c.request('POST', self.url, {'model': modelDef})

    # Update local state
    self.name = newName

  def setNote(self, newNote):
    '''
    Adds or updates a note for this model.

    * newNote - A String describing this model.
    '''

    raise NotYetImplementedError()

    # Get the current model state
    modelDef = self.getState()

    # Update the definition
    modelDef['note'] = newNote

    # Update remote state
    self.c.request('POST', self.url, {'model': modelDef})

    # Update local state
    self.note = newNote

  #############################################################################
  # Model states

  def getState(self):
    '''
    Returns the full state of the model from the API server

    TODO: Remove popping of Nones once API is updated
    '''

    modelDef = self.c.request('GET', self.url)['model']

    # API server doesn't except None values. Remove them.
    for key, value in modelDef.items():
      if value == None:
        del modelDef[key]

    return modelDef

  def promote(self, **params):
    '''
    Puts the model into a production ready mode.

    .. note: This may take several seconds.
    '''

    # Check how many records are in the swarm model output cache
    headers, data, meta = self.getModelOutput()
    swarmOutputCacheLen = len(data)

    # Promotion command
    self._runCommand('promote', **params)

    ##### WARNING: Ugly hack that will go away #####

    # Check if the state of the model changes
    timeoutCounter = 0
    while True:
      modelDef = self.c.request('GET', self.url)['model']
      status = modelDef['status']
      if timeoutCounter >= 20:
        raise GrokError('The production model did not start in a reasonable '
                        'amount of time. Please try again or contact support.')
      elif status == 'running':
        # The production model has turned on
        break
      else:
        print 'Waiting for the production model to become ready ...'
        time.sleep(.5)
        timeoutCounter += 1

    # Check that the production model has at least caught up to where we were
    # at the end of swarm.
    timeoutCounter = 0
    while True:
      # Production Model Output Cache Length
      try:
        headers, data, meta = self.getModelOutput()
        pmocLen = len(data)
      except grokpy.requests.exceptions.HTTPError:
        print 'Whoops 500'
        time.sleep(.5)
        timeoutCounter += 1
        continue

      if timeoutCounter >= 80:
        raise GrokError("The production model did not catch up to the swarm "
                        "in a reasonable amount of time. Please try again or "
                        "contact support.")
      elif pmocLen >= swarmOutputCacheLen:
        break
      else:
        print 'Waiting for the production model to catch up with the data ...'
        time.sleep(1)
        timeoutCounter += 1

    ##### END UGLY HACK

  def start(self, **params):
    '''
    Starts up a model, readying it to receive new data from a stream
    '''
    return self._runCommand('start', **params)

  def disableLearning(self, **params):
    '''
    Puts the model into a predictions only state where it will not learn from
    new data.

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('disableLearning', **params)

  def enableLearning(self, **params):
    '''
    New records will be integrated into the models future predictions.

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('enableLearning', **params)


  def setAnomalyAutoDetectThreshold(self, autoDetectThreshold):
    '''
    Sets the autoDetectThreshold of the model.  Model must be TemporalAnomaly
    for this to succeed.

    Parameters
    ----------------------------
    autoDetectThreshold - value to set the auto detect threshold

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('setAutoDetectThreshold', \
      autoDetectThreshold=autoDetectThreshold)


  def getAnomalyAutoDetectWaitRecords(self):
    '''
    Gets the autoDetectWaitRecords of the model.  Model must be TemporalAnomaly
    for this to succeed.

    Response on success
    ----------------------------
    {
      'autoDetectWaitRecords': integer
    }

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('getAutoDetectWaitRecords')


  def setAnomalyAutoDetectWaitRecords(self, autoDetectWaitRecords):
    '''
    Sets the autoDetectWaitRecords of the model.  Model must be TemporalAnomaly
    for this to succeed.

    Parameters
    ----------------------------
    autoDetectWaitRecords - value to set the auto detect wait records

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('setAutoDetectWaitRecords', \
      autoDetectWaitRecords=autoDetectWaitRecords)


  def getAnomalyAutoDetectThreshold(self):
    '''
    Gets the autoDetectThreshold of the model.  Model must be TemporalAnomaly
    for this to succeed.

    Response on success
    ----------------------------
    {
      'autoDetectThreshold': float
    }

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('getAutoDetectThreshold')


  def getLabels(self, startRecordID=None, endRecordID=None):
    '''
    Returns a list of labels for a given range of records. Each record has a 
    list of labels assocciated. A label may have no labels.

    Parameters
    ----------------------------
    startRecordID - ROWID of the first prediction of these label results
    endRecordID - ROWID of the last prediction record of these label results.
                  (Not inclusive.)

    Response on success
    ----------------------------
    {
      'isProcessing': boolean,
      'recordLabels': [
        {
          'ROWID': integer,
          'labels': [str, ...]
        },...
      ]
    }

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('getLabels', startRecordID=startRecordID,
      endRecordID=endRecordID)


  def addLabel(self, startRecordID, endRecordID, labelName):
    '''
    Adds a label to a given range of records from startRecordID to endRecordID,
    not inclusive of endRecordID.

    Parameters
    ----------------------------
    startRecordID - ROWID of the first prediction to add this label
    endRecordID - ROWID of the last prediction record to add this label.
                  (Not inclusive.)
    labelName - string indicating name of the label to add to the given range

    Response on success
    ----------------------------
    {
      'status': 'success'
    }

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('addLabel', startRecordID=startRecordID, \
      endRecordID=endRecordID, labelName=labelName)


  def removeLabels(self, startRecordID=None, endRecordID=None, labelFilter=None):
    '''
    Removes a label or all labels from a given range of records from 
    startRecordID to endRecordID, not inclusive of endRecordID. If labelFilter
    is set, only labels of type labelFilter will be removed, otherwise all
    labels will be removed from the given range.

    Parameters
    ----------------------------
    startRecordID - ROWID of the first prediction to remove labels
    endRecordID - ROWID of the last prediction record to remove labels.
                  (Not inclusive.)
    labelFilter - string. If not None, only labels equal to this will be
                  removed. Otherwise all labels will be removed from given
                  range.

    Response on success
    ----------------------------
    {
      'status': 'success'
    }

    .. note:: This method is intended for use with RUNNING models that have
              been promoted. The API server will return an error in other cases.
    '''
    return self._runCommand('removeLabels', startRecordID=startRecordID, \
      endRecordID=endRecordID, labelFilter=labelFilter)

  #############################################################################
  # Stream

  def getStream(self):
    '''
    Returns the Stream that this model is associated with.
    '''
    return self.parent.getStream(self.streamId)

  #############################################################################
  # Swarms

  def listSwarms(self):
    '''
    Returns a list of Swarm objects for this model
    '''

    # Where to make our request
    url = self.swarmsUrl

    swarmDefs = self.c.request('GET', url)['swarms']

    swarms = []
    for swarmDef in swarmDefs:
      swarms.append(Swarm(self, swarmDef))

    return swarms

  def startSwarm(self, size = None):
    '''
    Runs permutations on model parameters to find the optimal model
    characteristics for the given data.

    * size - A value from grokpy.SwarmSize. Initially, small, medium, or large.
            the default is medium. Small is only good for testing, whereas
            large can take a very long time.
    '''
    if self.swarm and self.swarm.getState() in ['Starting', 'Running']:
      raise GrokError('This model is already swarming.')

    url = self.swarmsUrl
    requestDef = {}
    if size:
      requestDef.update({'options': {"size": size}})

    result = self.c.request('POST', url, requestDef)

    # Save the swarm object
    self.swarm = Swarm(self, result['swarm'])

    return result

  def stopSwarm(self):
    '''
    Terminates a Swarm in progress
    '''
    raise NotYetImplementedError()

  def getSwarmState(self):
    '''
    Returns the current state of a swarm.
    '''

    if not self.swarm:
      # See if the API knows about a swarm for this model
      swarms = self.listSwarms()
      if not swarms:
        raise GrokError('There is no swarm associated with this model.')
      else:
        # Find the latest swarm
        # Use the string time to sort with the latest time first
        # If details hasn't been populated yet, assume this is the latest
        swarms = sorted(swarms,
                        key = lambda swarm: swarm.details.get('startTime', 0),
                        reverse=True)


        # Set that as *the* swarm for this model
        self.swarm = swarms[0]

    return self.swarm.getState()

  #############################################################################
  # Checkpoints

  def listCheckpoints(self):
    '''
    Returns a list of checkpoint dicts for this model
    '''
    # Where to make our request
    url = self.checkpointsUrl
    checkpoints = self.c.request('GET', url)['checkpoints']
    return checkpoints

  def createCheckpoint(self):
    '''
    Creates a new checkpoint object and returns it as a dict
    '''
    # Where to make our request
    url = self.checkpointsUrl
    checkpoint = self.c.request('POST', url)['checkpoint']
    return checkpoint

  #############################################################################
  # Model data

  def getModelOutput(self, limit=None, offset = None,
                           startAt = None, shift = True):
    '''
    Returns the data in the output cache of the best model found during Swarm.

    * limit - The maximum number of rows to get from the model
    * offset - The number of rows from the last row from which to begin
               returning data from. For example::

      If you have 1000 records in the model output cache and set offset to
      100, you will get records with row ID 900 to 999. If you set offset
      above the maximum row ID that exists in the model's output cache you will
      get no records.

    * startAt - The start row ID to begin returning data from. For example::

      If you have 1000 records in the model output cache and set startAt to
      100, you will get records with row ID 100 to 1000. If you set startAt
      above the maximum row ID that exists in the model's output cache you will
      get no records.

    * shift - This shifts the records returned so that all predictions are
              aligned with actual values. Note: Set this value to False if you
              are working with realtime data.
    '''

    params = {}
    if limit is not None:
      params['limit'] = limit
    if offset is not None:
      params['offset'] = offset
    if startAt is not None:
      params['startAt'] = startAt
    if shift is not None:
      params['shift'] = shift

    result = self.c.request('GET', self.dataUrl, params = params)['output']

    headers = result['names']
    data = result['data']

    try:
      meta = result['meta']
    except KeyError:
      meta = None

    return headers, data, meta
