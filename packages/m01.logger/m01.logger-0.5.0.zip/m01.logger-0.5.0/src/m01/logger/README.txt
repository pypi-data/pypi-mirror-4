======
README
======

This package provides a python logging formatter and loggin handler for write
log records to a mongodb. There is also a dumpRecord method which knows how to
dump the log records as formatted text.

  >>> import logging
  >>> from pprint import pprint

  >>> import m01.logger
  >>> pprint(logging._handlerList) # Python 2.7 has weakref stuff here
  [<weakref at ...; to 'NullHandler' at ...>,
   <weakref at ...; to 'MongoHandler' at ...>]

  >>> logger = logging.getLogger('m01.logger.testing')
  >>> logger
  <logging.Logger ... at ...>

>>> logger.handlers
[<MongoHandler m01_logger_testing.testing; from testinstance>]

Before we start logging check our mongodb connection and remove previous
testing databases:

>>> mongoHandler = logger.handlers[0]
>>> mongoHandler
<MongoHandler m01_logger_testing.testing; from testinstance>


Adjust default log level:

  >>> logger.setLevel(logging.DEBUG)

  >>> logger.isEnabledFor(logging.INFO)
  True

  >>> logger.isEnabledFor(logging.ERROR)
  True

  >>> logger.isEnabledFor(logging.DEBUG)
  True

  >>> logger.info(u'foobar')
  >>> logger.debug(u'debug message')
  >>> logger.error(u'error message')

we can also log an exception:

  >>> e = KeyError("My Key Error", 42)
  >>> try:
  ...     raise e
  ... except Exception, e:
  ...     logger.exception(e)

Now check the log messages:

  >>> found = tuple(mongoHandler.collection.find())
  >>> for x in found:
  ...     print x[u'levelname'], x[u'message'], x[u'filename'], x[u'instance']
  INFO foobar <doctest README.txt[...]> testinstance
  DEBUG debug message <doctest README.txt[...]> testinstance
  ERROR error message <doctest README.txt[...]> testinstance
  ERROR ('My Key Error', 42) <doctest README.txt[...]> testinstance


dumpData
--------

The formatter module provides a dumpData method which is able to format
the LogRecord data stored in mongodb.

  >>> from m01.logger.formatter import dumpData

Let's dump the record:

  >>> data = mongoHandler.collection.find_one({'message': 'error message'})

By default the dumpData method will only render the message:

  >>> dumpData(data)
  u'error message'

Let's define a formatter string with some attributes:

  >>> fmt = '[%(name)s] %(asctime)s %(message)s %(exception.message)s'
  >>> dumpData(data, fmt)
  u'[m01.logger.testing] ...-...-... ...:...:...,... error message ---'

We can also format an exception:

  >>> data = mongoHandler.collection.find_one({'message':
  ... "('My Key Error', 42)"})

  >>> dumpData(data, fmt)
  u"[m01.logger.testing] ...-...-... ...:...:...,... ('My Key Error', 42) ('My Key Error', 42)"

  >>> fmt = '%(exception.code)s %(exception.stackTrace)s'
  >>> dumpData(data, fmt)
  u'0 Traceback (most recent call last):\n  File "<doctest README.txt[...]>", line 2, in <module>\n    raise e\nKeyError: (\'My Key Error\', 42)'

The server instance of the server/framework that emitted the log entry
is recorded too:

  >>> fmt = '[%(name)s] [%(instance)s] %(message)s'
  >>> dumpData(data, fmt)
  u"[m01.logger.testing] [testinstance] ('My Key Error', 42)"

