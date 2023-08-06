import grokpy

from model import Model
from stream import Stream
from action import Action
from exceptions import GrokError, AuthenticationError

class Project(object):
  '''
  Object representing a Grok project

  * parentClient - A Client object.
  * projectDef - A dict, usually returned from a model creation or get action.
    Usually includes:

    * streamsUrl
    * name
    * url
    * modelsUrl
    * actionsUrl
    * id
  '''

  def __init__(self, parentClient, projectDef):

    # Give projects access to the parent client and its connection
    self.parentClient = parentClient
    self.c = self.parentClient.c

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(projectDef)

  def setName(self, newName):
    '''
    Renames the project.

    * newName - String
    '''

    # Get the current project description
    url = self.url
    projectDef = self.c.request('GET', url)['project']

    # Update the definition
    projectDef['name'] = newName

    # Update remote state
    self.c.request('POST', url, {'project': projectDef})

    # Update local state
    self.name = newName

  def delete(self):
    '''
    Permanently deletes the project, all its models, and data.

    .. warning:: There is currently no way to recover from this opperation.
    '''

    self.c.request('DELETE', self.url)

  #############################################################################
  # Model Methods
  #
  # Thin wrappers for Model methods on the Client object.

  def createModel(self, spec):
    '''
    Return a new Model object. The model will be created under this project.

    * spec - A configuration for this model. Can be EITHER a file path to a
      JSON document OR a Python dict.
    '''

    return self.parentClient.createModel(spec,
                                         parent = self,
                                         url = self.modelsUrl)

  def getModel(self, modelId):
    '''
    Returns the model corresponding to the given modelId

    * modelId
    '''

    return self.parentClient.getModel(modelId, self.modelsUrl)

  def listModels(self):
    '''
    Returns a list of Models that exist in this project
    '''

    return self.parentClient.listModels(self.modelsUrl)

  def deleteAllModels(self, verbose = False):
    '''
    Permanently deletes all models associated with this project.

    * [verbose] - If set, the model Id of each model being deleted will be
      printed.

    .. warning:: There is currently no way to recover from this opperation.
    '''

    modelList = self.listModels()

    return self.parentClient.deleteAllModels(modelList, verbose)

  #############################################################################
  # Stream Methods
  #
  # Thin wrappers for Stream methods on the Client object.

  def createStream(self, spec):
    '''
    Returns a new Stream object. The stream will be created under this project.

    * spec - A configuration for this stream. Can be EITHER a file path to a
      JSON document OR a Python dict OR a StreamSpecification object.
    '''

    return self.parentClient.createStream(spec,
                                          self,
                                          url = self.streamsUrl)

  def getStream(self, streamId):
    '''
    Returns a Stream object from the given streamId. Assumes the stream is part
    of this project.
    '''
    return self.parentClient.getStream(streamId, self.streamsUrl)

  def listStreams(self):
    '''
    Returns a list of streams associated with the current project
    '''
    return self.parentClient.listStreams(self.streamsUrl)

  def deleteAllStreams(self, verbose = False):
    '''
    Permanently deletes all streams associated with the current project

    .. warning:: There is currently no way to recover from this opperation.
    '''
    self.parentClient.deleteAllStreams(self.streamsUrl, verbose)

  #############################################################################
  # Action Methods
  #

  def createAction(self, description):
    '''
    Returns a new Action object. The Action will be created under this project.

    * description - String - A short description of the action the client
      has taken and would like to log with the project.

    '''

    if self.actionsUrl:
      url = self.actionsUrl
    else:
      raise GrokError('There is no Actions URL associated with this Project' \
                      ' object.')

    requestDef = {'action': {'description': description}}

    result = self.c.request('POST', url, requestDef)

    if grokpy.DEBUG:
      print result

    parentProject = self

    return Action(parentProject, result['action'])

  def getAction(self, actionId):
    '''
    Returns a Action object from the given actionId.
    '''
    raise NotImplementedError()

    #if self.actionsUrl:
    #  url = self.actionsUrl
    #else:
    #  raise GrokError('There is no Actions URL associated with this Project' \
    #                  ' object.')
    #
    #url += ('/' + str(actionId))
    #result = self.c.request('GET', url)
    #
    #parentProject = self
    #
    #return Action(parentProject, result['action'])

  def listActions(self):
    '''
    Returns a list of Actions associated with the current project
    '''

    if self.actionsUrl:
      url = self.actionsUrl
    else:
      raise GrokError('There is no Actions URL associated with this Project' \
                      ' object.')

    actionDefs = self.c.request('GET', url)['actions']

    actions = []
    for actionDef in actionDefs:
      actions.append(Action(self, actionDef))

    return actions

  def deleteAllActions(self, verbose = False):
    '''
    Permanently deletes all Actions associated with the current project

      * [verbose] - If set, the action Id of each action being deleted will be
                    printed.

    .. warning:: There is currently no way to recover from this opperation.
    '''

    raise NotImplementedError()

    #actionList = self.listActions()
    #
    #for action in actionList:
    #  if verbose or grokpy.DEBUG:
    #    print 'Deleting action: ' + str(action.id)
    #  action.delete()
