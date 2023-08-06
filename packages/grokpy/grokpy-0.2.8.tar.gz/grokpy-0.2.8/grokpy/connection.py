import base64
import grokpy
import json
import os
import requests
import sys
import time
from datetime import (
  datetime,
  timedelta
)
from exceptions import (
  GrokError,
  AuthenticationError
)
from functools import wraps
from grokpy.requests.exceptions import HTTPError


def total_seconds(dt):
  '''
  Calculates the total seconds represented in a datetime.timedelta instance.

  Provided for backward compatibility in versions of python < 2.7.  For later
  versions, the native datetime.timedelta.total_seconds() implementation is
  used.
  '''
  if hasattr(dt, 'total_seconds'):
    return dt.total_seconds()

  return (dt.microseconds + (dt.seconds + dt.days * 24 * 3600) * 10**6) / 10**6


class Connection(object):
  '''
  Connection object for the Grok Prediction Service
  '''

  def __init__(self,
               key = None,
               baseURL = None,
               session = None,
               headers = None,
               proxies = None):
    '''
    key - Grok API Key
    baseURL - Grok server request target
    session - A requests lib Session instance. Useful for testing.
    headers - Dict - Headers to add to each request.
    proxies - Dict - e.g. {"http": "10.10.1.10:3128", "https": "10.10.1.10:1080"}
    '''
    # Search for API key in environment
    if not key or key == 'YOUR_KEY_HERE':
      key = self._find_key()
      if not key:
        raise AuthenticationError("""
          Please supply your API key.

          Method 1:
            Supply your credentials when you instantiate the connection.

            connection = %s(key='YOUR_KEY_HERE')

          Method 2:
          (More Secure)

            Add your credentials to your shell environment. From the command
            line:

            echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
            source ~/.bashrc

            For either method please replace the dummy key value with your real
            key from your account page.

            http://grok.numenta.com/account""" % self.__class__.__name__)
    else:
      self._validateKey(key)

    # The API key we'll use to authenticate all HTTP calls.
    self.key = key
    if grokpy.DEBUG:
      print 'Using API Key'
      print key

    if not baseURL:
      baseURL = self._find_baseURL(default='https://api.numenta.com/')

    # The base path for all our HTTP calls
    if baseURL[-1] != '/':
      baseURL += '/'
    self.baseURL = baseURL + 'v2'

    # Require https
    if baseURL[:5] != 'https' and baseURL[:16] != 'http://localhost':
      raise GrokError('Please supply an HTTPS URL to override the default.')

    # The HTTP Client we'll use to make requests
    if not session:
      base64string = base64.encodestring(self.key + ':').replace('\n', '')
      agent = "Grok API Client - Python - Version %s" % grokpy.__version__
      if headers is None:
        headers = {}
      headers["Authorization"] = "Basic %s" % base64string
      headers["Content-Type"] = 'application/json; charset=UTF-8'
      headers["User-Agent"] = agent
      session = requests.session(headers=headers, proxies=proxies)

    self.s = session
    self.requuid = None

  def request(self, method, url, requestDef = None, params = None,
    retries = 3, retryInterval = 30):
    '''
    Interface for all HTTP requests made to the Grok API
    '''

    if url[:4] != 'http':
      url = self.baseURL + url

    # JSON serialize the requestDef object
    requestDefJSON = json.dumps(requestDef, ensure_ascii=False)

    if grokpy.DEBUG:
      print "Method :", method
      print "Url :", url
      print "requestDef : ", requestDefJSON
      print "params :", params

    try:
      # Make the request, handle initial connection errors
      if method == 'GET':
        response = self.s.get(url, params = params)
      elif method == 'POST':
        response = self.s.post(url, requestDefJSON)
      elif method == 'DELETE':
        response = self.s.delete(url)
      elif method == 'PUT':
        response = self.s.put(url, requestDefJSON)
      else:
        raise GrokError('Unsupported HTTP method: %s' % method)
    except ImportError:
      raise GrokError('The certifi module is required to use grokpy. Please '
                      'install it by running "sudo pip install certifi". If '
                      'you get an "unknown command" error. Please install pip '
                      'by running "sudo easy_install pip", then rerun the '
                      'first command.')

    if response.headers.get('x-grok-requuid'):
      self.requuid = response.headers.get('x-grok-requuid')
    if not response.ok:
      try:
        # Requests will construct an exception based on context
        raise response.raise_for_status(response.text)
      except HTTPError, e:
        # Add in our useful error text to that exception
        e = str(e) + \
            " - Request Uid: %s - Response content: %s" % (
                                         response.headers.get('x-grok-requuid'),
                                         response.text
                                        )

        if ('retry-after' in response.headers) \
          and response.status_code == 503 \
          and retries:
          retryAfter = response.headers['retry-after']

          try:
            ttl = int(retryAfter)

          except ValueError:
            retryAfterTS = \
              datetime.strptime(retryAfter, '%a, %d %b %Y %H:%M:%S UTC')

            dttl = retryAfterTS - datetime.utcnow()

            ttl = total_seconds(dttl)

          if ttl > 0:
            time.sleep(ttl)

            return self.request(method, url, requestDef, params, retries)

          raise HTTPError(e)

        elif response.status_code >= 500 and retries > 1:
          time.sleep(retryInterval)
          return self.request(method, url, requestDef, params, retries - 1, retryInterval)

        else:
          raise HTTPError(e)

    if grokpy.DEBUG >= 1:
      print 'Raw response:'
      print response.text

    # Load info from returned JSON strings
    content = json.loads(response.text)

    if grokpy.DEBUG:
      print 'Response converted to JSON:'
      print content
      print 'Request Uid:%s' % response.headers.get('x-grok-requuid')

    return content

  ###########################################################################
  # Private Methods

  def _find_key(self):
    '''
    Retrieve an API key from the user's shell environment
    '''
    try:
      key = os.environ["GROK_API_KEY"]
    except KeyError:
      return None

    return key

  def _find_baseURL(self, default):
    '''
    Retrieve an API base URL from the user's shell environment
    '''
    return os.environ.get("GROK_API_URL", default)

  def _validateKey(self, key):
    '''
    Makes sure that a given key conforms to the expected format
    '''
    if len(key) < 5:
      raise AuthenticationError('This key is too short, '
                                'please check it again: "' + key +'"')
    else:
      return 'OK'

  ###########################################################################
  # Debugging hooks
  #
  # See http://docs.python-requests.org/en/latest/user/advanced/#event-hooks

  def _printHeaders(self, args):
    '''
    Event hook to print the headers of a request. Pass this to the request
    method like this::

      requests.get('http://httpbin.org', hooks=dict(args=self._printHeaders))
    '''
    print args['headers']
