class User(object):
  '''
  An object representation of the JSON user description the API provides.
  '''
  def __init__(self, userDict):

    self.__dict__.update(userDict)
