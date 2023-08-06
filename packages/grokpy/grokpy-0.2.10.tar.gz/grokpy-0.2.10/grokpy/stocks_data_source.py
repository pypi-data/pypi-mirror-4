import grokpy

from grokpy.exceptions import GrokError

class StocksDataSource(object):
  '''
  A specification object for adding Stock data to your stream

  Using stock data requires that your input stream contain a TIMESTAMP field
  with the flag DATETIME.

  Below is an example of how to join in the closing price of AAPL with all
  of your records.

  Example use::

    stocks = grokpy.StockssDataSource()
    stocks.addSymbol('AAPL')
    stocks.addDataType(grokpy.StockDataTypes.LastPrice)

    Input Record

    TIMESTAMP
    ['2010-01-08 00:45:00.0']

    Appended Record

    TIMESTAMP                 AAPL-LastPrice
    ['2010-01-08 00:45:00.0', 211.98]

    Note that the hours, minutes, and seconds of a timestamp are ignored
    by this data source. All data is tied to a specific date.
  '''

  def __init__(self):

    # Our list of fields
    self.fields = []

    # Our list of symbols
    self.symbols = []

    # Our list of requested data types
    self.dataTypes = []

  def addSymbol(self, symbol):
    '''
    Adds a ticker symbol to the list of symbols to be merged with the parent
    stream.

    * symbol - A valid ticker symbol
    '''

    # Validate input
    if len(symbol) >= 6:
      raise GrokError('The stock symbol requested (%s) appears invalid '
                      '(too long). ' % symbol)

    self.symbols.append(symbol)

  def addSymbols(self, symbols):
    '''
    Adds each keyword in the list `keywords` to the datasource

    * sybols - A list of symbols to be added.
    '''
    for symbol in symbols:
      self.addSymbol(symbol)

  def addDataType(self, dataType):
    '''
    Adds a data type to the source specification which will be returned for
    all requested stocks.
    '''

    validTypes = [value for value in grokpy.StockDataTypes.__dict__.values() if
                  isinstance(value, str)]

    if dataType not in validTypes:
      raise GrokError('Invalid data type. Please pass a '
                      'grokpy.StockDataType value')

    self.dataTypes.append(dataType)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification.
    Usually consumed by an instance of the StreamSpecification class.
    '''

    if not self.symbols or not self.dataTypes:
      raise GrokError('Please specify at least one stock symbol and one '
                      'datatype.')

    for symbol in self.symbols:
      for dataType in self.dataTypes:
        fieldSpec = {"name": symbol + '-' + dataType,
                 "dataFormat": {"dataType": grokpy.DataType.SCALAR}}
        # Don't duplicate fields
        if fieldSpec not in self.fields:
          self.fields.append(fieldSpec)

    returnSpec = {"name": "stocks",
                 "dataSourceType": "public",
                 "fields": self.fields}

    return returnSpec
