'''
A set of Enum-like classes to specifiy the strings expected by the API
in a straight forward and self-documenting fashion.
'''

class Aggregation(object):

  RECORD = 'record'
  SECONDS = 'seconds'
  MINUTES = 'minutes'
  MINUTES_15 = 'minutes15'
  HOURS = 'hours'
  DAYS = 'days'
  WEEKS = 'weeks'
  MONTHS = 'months'

class SwarmSize(object):

  SMALL = 'small'
  MEDIUM = 'medium' # Default
  LARGE = 'large'

class SwarmStatus(object):

  STARTING = 'starting'
  RUNNING = 'running'
  CANCELED = 'canceled'
  COMPLETED = 'completed'

class DataType(object):

  DATETIME = 'DATETIME' # a point in time.
  CATEGORY = 'CATEGORY' # a category.
  SCALAR = 'SCALAR' # a numeric value.

class DataFlag(object):

  TIMESTAMP = 'TIMESTAMP'
  LOCATION = 'LOCATION'

class AggregationFunction(object):

  FIRST = 'first'
  LAST = 'last'
  AVERAGE = 'mean'
  SUM = 'sum'
  MAX = 'max'
  MIN = 'min'

class PredictionType(object):

  TEMPORAL = 'temporal'
  SPATIAL = 'spatial'

class ModelType(object):

  ANOMALY = 'anomalyDetector'
  PREDICTOR = 'predictor'

class DataSourceType(object):

  LOCAL = 'local'
  PUBLIC = 'public'

class PublicDataSources(object):

  WEATHER = 'weather'
  TWITTER = 'twitter'
  STOCKS = 'stocks'
  EVENTS = 'events'

class WeatherDataType(object):

  TEMPERATURE = "TEMP"
  PRECIPITATION = "PRCP"
  WIND_SPEED = "WDSP"

class StockDataTypes(object):

  OPEN_PRICE = "OpenPrice"
  HIGH_PRICE = "HighPrice"
  LOW_PRICE = "LowPrice"
  LAST_PRICE = "LastPrice"
  VOLUME = "Volume"

class HolidayLocale(object):

  US_HOLIDAYS = "US-HOLIDAYS"
  UK_HOLIDAYS = "UK-HOLIDAYS"
  CA_HOLIDAYS = "CA-HOLIDAYS"
