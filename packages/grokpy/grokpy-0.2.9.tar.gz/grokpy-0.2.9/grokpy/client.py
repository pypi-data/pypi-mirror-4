import StringIO
import traceback
import json
import grokpy
import warnings

from connection import Connection
from user import User
from project import Project
from model import Model
from model_specification import ModelSpecification
from stream import Stream
from stream_specification import StreamSpecification
from exceptions import (GrokError,
                       AuthenticationError,
                       NotYetImplementedError)

class Client(object):
  '''
  A client to access the Grok HTTP API.

  * [key] - Grok API Key
  * [baseURL] - Grok server request target
  * [connection] - An instance of the grokpy.Connection class. Used mainly for
    testing.
  * [headers] - Overrides for auth and user agent headers. Used mainly for
    testing.
  * [proxies] - Dict - e.g. {"http": "10.10.1.10:3128", "https": "10.10.1.10:1080"}
  '''

  def __init__(self, key = None,
               baseURL = None,
               connection = None,
               headers = None,
               proxies = None):

    if headers is None:
      headers = {}
    # Create a connection to the API
    if not connection:
      if baseURL:
        self.c = Connection(key, baseURL, headers = headers, proxies = proxies)
      else:
        self.c = Connection(key, headers = headers, proxies = proxies)
    else:
      self.c = connection

    # Test the connection works and get the User info
    self.user = self.getUser()

  #############################################################################
  # User Methods

  def getUser(self, userId = None):
    '''
    Returns a User object. By default returns the first user associated with
    this API key.

    * [userId]
    '''
    url = '/users'
    rv = self.c.request('GET', url)

    # By default return the first user.
    if not userId:
      user = User(rv['users'][0])
      return user
    # Otherwise return the first user with a matching Id
    else:
      for userDict in rv['users']:
        if userDict['id'] == userId:
          return User(userDict)

    # We didn't find the user
    raise GrokError('There were no users, or the userId you specified was not '
                    'found.')

  #############################################################################
  # Model Methods

  def createModel(self, spec, parent = None, url = None):
    '''
    Returns a Model object.

    * spec - A configuration for this model. Can be EITHER a file path to a
      JSON document OR a Python dict
    * [parent] - A Project object which associates this model with a specific
      parent project.
    * [url] - The target for creating this model. Automatically specified
      when calling project.createModel() rather than client.createModel().
    '''

    # Process the given spec
    modelSpec = self._handelAmbiguousSpec(spec)

    if not parent:
      parent = self

    if not url:
      url = self.user.modelsUrl

    requestDef = {'model': modelSpec}

    result = self.c.request('POST', url, requestDef)

    if grokpy.DEBUG:
      print result

    return Model(parent, result['model'])

  def getModel(self, modelId, url = None):
    '''
    Returns a Model object corresponding to the given modelId

    * modelId
    * [url] - Usually only specified when calling the equivalent method on a
      project.
    '''

    if not url:
      url = self.user.modelsUrl

    url += ('/' + str(modelId))
    modelDef = self.c.request('GET', url)['model']

    return Model(self, modelDef)

  def listModels(self, url = None):
    '''
    Returns a list of Models. By default it will return a list of all models
    tied to the current API key.

    TODO: Update this once the list returned from the server contains info
    about what projects the models belong to.

    * [url] - Usually only specified when calling the equivalent method on a
      project.
    '''

    params = None
    if not url:
      # The user hasn't specified a url (usually to limit values to a project)
      url = self.user.modelsUrl
      params = {'all': True}

    modelDefs = self.c.request('GET', url, params = params)['models']

    models = []
    for modelDef in modelDefs:
      models.append(Model(self, modelDef))

    return models

  def deleteAllModels(self, modelList = None, verbose = False):
    '''
    Permanently deletes all models associated with the current API key.

    * [verbose] - If set, the model Id of each model being deleted will be
      printed.

    .. warning:: There is currently no way to recover from this opperation.
    '''

    if modelList == None:
      modelList = self.listModels()

    for model in modelList:
      if verbose or grokpy.DEBUG:
        print 'Deleting model: ' + str(model.id)
      model.delete()

  #############################################################################
  # Stream Methods

  def createStream(self, spec, parent = None, url = None):
    '''
    Returns an instance of the Stream object.

    * spec - A configuration for this stream. Can be EITHER a file path to a
      JSON document OR a Python dict OR a StreamSpecification object.
    * [parent] - A Project object which associates this stream with a specific
      parent project.
    * [url] - The target for creating this stream. Automatically specified
      when calling project.createStream() rather than client.createStream()
    '''

    # Process the given spec
    streamSpec = self._handelAmbiguousSpec(spec)

    # Default to the client as container if not passed a project
    if not parent:
      parent = self

    # Streams created from projects will pass in a project streamsUrl
    if not url:
      url = self.user.streamsUrl

    requestDef = {'stream': streamSpec}

    result = self.c.request('POST', url, requestDef)

    return Stream(parent, result['stream'])

  def getStream(self, streamId, url = None):
    '''
    Returns a Stream object corresponding to the given streamId

    * streamId
    * [url] - Usually only specified when calling the equivalent method on a
      project.
    '''

    if not url:
      # The user hasn't specified a url (usually to limit values to a project)
      url = self.user.streamsUrl

    url += '/' + streamId

    rv = self.c.request('GET', url)
    streamDef = rv['stream']

    return Stream(self, streamDef)

  def listStreams(self, url = None):
    '''
    Returns a list of Stream objects. By default it will return a list of all
    streams tied to the current API key.

    * [url] - Usually only specified when calling the equivalent method on a
      project.
    '''

    params = None
    if not url:
      # The user hasn't specified a url (usually to limit values to a project)
      url = self.user.streamsUrl
      params = {'all': True}

    streams = []
    for streamDef in self.c.request('GET', url, params = params)['streams']:
      streams.append(Stream(self, streamDef))

    return streams

  def deleteAllStreams(self, url = None, verbose = False):
    '''
    Permanently deletes all streams associated with the current API key.

    * [url] - Usually only specified when calling the equivalent method on a
      project.
    * [verbose] - If set, the stream Id of each stream being deleted will be
      printed.

    .. warning:: There is currently no way to recover from this opperation.
    '''

    for stream in self.listStreams(url):
      if verbose:
        print 'Deleting stream: ' + str(stream.id)
      stream.delete()

  def _safe_dict(self, d):
    '''
    Recursively clone json structure with UTF-8 dictionary keys

    From: http://www.gossamer-threads.com/lists/python/python/684379
    '''
    if isinstance(d, dict):
      return dict([(k.encode('utf-8'), self._safe_dict(v)) for k,v in d.iteritems()])
    elif isinstance(d, list):
      return [self._safe_dict(x) for x in d]
    else:
      return d

  def _handelAmbiguousSpec(self, spec):
    '''
    Returns a sanitized python dictionary for use in creating a stream

    * spec - A Python dict OR
             A file path to a JSON docucment OR
             A StreamSpecification object
    '''

    processedSpec = {}
    # If we were given a dict directly, use that.
    if type(spec) == type({}):
      processedSpec = spec
    # If we are given a StreamSpecification object, pull its spec and use that.
    elif isinstance(spec, (StreamSpecification, ModelSpecification)):
      processedSpec = spec.getSpec()
    # Otherwise pull the info out of a file.
    else:
      fileHandle = open(spec, 'rU')
      try:
        specFromFile = json.load(fileHandle)
      except:
        msg = StringIO.StringIO()
        print >>msg, ("Caught JSON parsing error. Your stream specification may "
        "have errors. Original exception follows:")
        traceback.print_exc(None, msg)
        raise GrokError(msg.getvalue())

      # Convert all unicode to normal
      processedSpec = self._safe_dict(specFromFile)

    return processedSpec

  #############################################################################
  # Project Methods

  def createProject(self, projectName):
    '''
    Returns a Project object.

    * projectName - Used primarly for display purposes
    '''

    # A dictionary describing the request
    requestDef = {'project': {'name': projectName}}

    # The URL target for our request
    url = self.user.projectsUrl

    # Make the API request
    result = self.c.request('POST', url, requestDef)

    # Use the results to instantiate a new Project object
    project = Project(self, result['project'])

    return project

  def getProject(self, projectId):
    '''
    Returns a Project with the given Id

    * projectId
    '''
    if projectId == 'YOUR_PROJECT_ID':
      raise GrokError('Please supply a valid Project Id')

    url = self.user.projectsUrl

    url += ('/' + str(projectId))
    projectDef = self.c.request('GET', url)['project']

    return Project(self, projectDef)

  def listProjects(self):
    '''
    Lists all the projects currently associated with this account
    '''

    params = {'all': True}

    rv = self.c.request('GET', self.user.projectsUrl, params = params)
    projectDefs = rv['projects']

    projects = []
    for projectDef in projectDefs:
      projects.append(Project(self, projectDef))

    return projects

  def deleteAllProjects(self, verbose = False):
    '''
    Permanently deletes all projects

    * [verbose] - If set, the model Id of each model being deleted will be
      printed.

    .. warning:: There is currently no way to recover from this opperation.
    '''

    for project in self.listProjects():
      if verbose:
        print 'Deleting project: ' + str(project.id)
      project.delete()

  #############################################################################
  # Public Data Source Methods

  def listPublicDataSources(self):
    '''
    Lists all the public data sources registered with Grok
    '''
    pass

  def getPublicDataSource(self, id):
    '''
    Looks up and returns a PDS by its code.
    '''
    pass

  #############################################################################
  # Helper Methods

  @staticmethod
  def alignPredictions(headers, resultRows):
    '''
    .. deprecated:: 0.2.3
      This is now done by default when calling .getModelOutput(). To get
      unshifted results, call .getModelOutput(shift = False).

    Returns a list of list suitable for writing to a CSV file. Puts predictions
    on the same row the actual value for easy comparison in external tools
    like Excel.

    * headers - A list of strings to use as column headers.
    * resultRows - A list of lists representing the output data from a model.

    Example Transformation::

      RowID   ActualValue     PredictedValue
      0       3               5
      1       5               7
      2       7               9

      RowID   ActualValue     PredictedValue
      0       3
      1       5               5
      2       7               7
                              9
    '''
    warnings.warn("deprecated", DeprecationWarning)

    # Find columns that contain predictions / metrics
    predictionIndexes = [headers.index(header)
                       for header in headers
                       if ('Score' in header)
                       or ('Predicted' in header)]

    # Bump all predictions down one row
    columns = zip(*resultRows)
    for index in range(len(columns)):
      column = list(columns[index])
      if index in predictionIndexes:
        column.insert(0, '')
      else:
        column.append('')
      columns[index] = column
    resultRows = zip(*columns)

    return resultRows
