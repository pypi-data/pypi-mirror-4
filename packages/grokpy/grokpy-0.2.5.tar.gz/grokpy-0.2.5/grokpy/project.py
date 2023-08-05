from model import Model
from stream import Stream
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
