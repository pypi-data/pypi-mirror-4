import grokpy

from grokpy.exceptions import GrokError

class EventsDataSource(object):
  '''
  A specification object for adding Events data to your stream

  Events are currently limited to national holidays for the following:

      United States
      Canada
      United Kingdom

  Using this data source requires that you have a TIMESTAMP field in your
  stream specification.

  If a value of the TIMESTAMP field falls on the same day as an event in our
  database, the name of that event will be used as the value for this field.

  For example::

    events = grokpy.EventsDataSource()
    events.addEventType(grokpy.HolidayLocale.US_HOLIDAYS)

    Input Record

    TIMESTAMP
    ['2010-01-01 00:45:00.0']

    Appended Record

    TIMESTAMP                   US_HOLIDAYS
    ['2010-01-01 00:45:00.0', 'New Years Day']

    Note that the hours, minutes, and seconds of a timestamp are ignored
    by this data source. If an event corresponds to the date portion of the
    timestamp it will be appended.
  '''

  def __init__(self):

    # Our list of fields in this source
    self.fields = []

  def addEventType(self, eventType):
    '''
    Adds an event type to the data source.

    * eventType - Currently a grokpy.HolidayLocale value only.
    '''

    validTypes = [value for value in grokpy.HolidayLocale.__dict__.values() if
                  isinstance(value, str)]

    if eventType not in validTypes:
      raise GrokError('Invalid event type. Please pass a '
                      'grokpy.HolidayLocale value')

    fieldSpec = {"name": eventType,
                 "dataFormat": {"dataType": grokpy.DataType.CATEGORY}}

    self.fields.append(fieldSpec)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification.
    Usually consumed by an instance of the StreamSpecification class.
    '''
    if not self.fields:
      raise GrokError('Please specify at least one event type you would like '
                      'to join with your data.')

    returnSpec = {"name": "events",
                 "dataSourceType": "public",
                 "fields": self.fields}

    return returnSpec
