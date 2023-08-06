import os
import sys
import json
import math
import StringIO
import traceback
import grokpy

from datetime import datetime

from exceptions import GrokError, AuthenticationError

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model. Stream objects are returned by createStream()
  methods and should usually not be instantiated directly by end users.

  * parent - Either a Client object or a Project object
  * streamDef - A python dict representing the specification of this stream
  '''

  def __init__(self, parent, streamDef):

    # Give streams access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c

    # Store the raw stream def in case a user wants to get it later
    self._rawStreamDef = streamDef

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(streamDef)

  def addRecords(self, records, step = 500):
    '''
    Appends records to the input cache of the given stream. This method will
    recurse if it needs to split up the records into smaller chunks for
    sending.

    * records - A list of lists representing your data rows
    * step - How many records we will send in each request.
    '''

    # Where to POST the data
    url = self.dataUrl

    # Parse records for various things
    records = self._parseRecords(records)

    # Limit how many records we will send in a given request
    try:
      if len(records) > step:
        i = 0
        while i < len(records):
          requestDef = {"input": records[i:(i+step)]}
          if grokpy.DEBUG:
            print len(requestDef['input'])
          self.c.request('POST', url, requestDef)
          i += step
      # If it's small enough send everything
      else:
        requestDef = {"input": records}
        self.c.request('POST', url, requestDef)
    # TODO: Make the error thrown by connection class more specific
    except GrokError:
      # Break recursion if this just isn't going to work
      if step < 50:
        raise GrokError('Step size started or has grown too small.')
      # Try sending half as many records.
      step = int(math.floor(step / 2))
      self.addRecords(records, step)

  def delete(self):
    '''
    Permanently deletes this stream.

    .. warning:: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  def clone(self, params = None):
    '''
    Clones this stream
    '''
    if params:
      result = self.c.request('POST', self.cloneUrl, {'stream': params})
    else:
      result = self.c.request('POST', self.cloneUrl)


    return Stream(self.parent, result['stream'])

  def getSpecDict(self):
    '''
    Returns a Python dict representing the specification of this stream
    '''
    return self._rawStreamDef


  #############################################################################
  # PRIVATE METHODS

  def _parseRecords(self, records):
    '''
    Return records in a format more compatible with POSTing to the API

    NOTE: This could be expensive. First optimization would be to use list
    comprehensions at the expense of readability.
    '''

    # Convert Python datetime objects into API compatible strings
    for i, record in enumerate(records):
      for j, item in enumerate(record):
        if isinstance(item, datetime):
          records[i][j] = item.strftime('%Y-%m-%d %H:%M:%S.%f')

    return records
