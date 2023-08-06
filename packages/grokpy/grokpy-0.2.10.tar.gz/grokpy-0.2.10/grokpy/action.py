import os
import sys
import json
import math
import StringIO
import traceback
import grokpy

from datetime import datetime

from exceptions import GrokError, AuthenticationError

class Action(object):
  '''
  An Action is a record of a user defined action taken by a Grok Client. A list
  of all actions associated with a Project can be used as a log of activity
  for that project and decisions that have been made based on Grok predictions.

  For example, if your client is controlling the temperature in a building you
  might create a new action with the description "Increased target temperature
  by 2 degrees."

  * parent - A Project object
  * actionDef - A python dict representing the specification of this action
  '''

  def __init__(self, parent, actionDef):

    # Give actions access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c

    # Store the raw action def in case a user wants to get it later
    self._rawActionDef = actionDef

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(actionDef)

  def delete(self):
    '''
    Permanently deletes this action.

    .. warning:: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  def getSpecDict(self):
    '''
    Returns a Python dict representing the specification of this action
    '''
    return self._rawActionDef
