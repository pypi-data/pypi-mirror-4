##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import logging

from bson.timestamp import Timestamp

_marker = object()


class MongoFormatter(logging.Formatter):
    """Formatter instances are used to convert a LogRecord to a mongodb item.
    
    The MongoFormatter knows how to dump a LogRecord item to mongodb data. The
    MongoHandler will later save the converted data to the mongodb.

    """

    def __init__(self, instance):
        self._instance = instance
        super(MongoFormatter, self).__init__()

    def format(self, record):
        """Convert the record to mongodb data"""
        data = {'_type': u'LogRecord',
                'name': unicode(record.name),
                'levelno': record.levelno,
                'levelname': unicode(record.levelname),
                'pathname': unicode(record.pathname),
                'filename': unicode(record.filename),
                'module': unicode(record.module),
                'lineno': record.lineno,
                'funcName': unicode(record.funcName),
                'created': record.created,
                'asctime': unicode(self.formatTime(record, self.datefmt)),
                'msecs': record.msecs,
                'relativeCreated': record.relativeCreated,
                'thread': record.thread,
                'threadName': unicode(record.threadName),
                'process': record.process,
                'message': unicode(record.getMessage()),
                # additional values
                'timestamp': Timestamp(int(record.created), int(record.msecs)),
                'instance': unicode(self._instance),
                }
        if record.exc_info is not None:
            data['exception'] = {
                u'message' : unicode(record.exc_info[1]),
                u'code' : 0, # XXX: currently unused
                u'stackTrace': unicode(self.formatException(record.exc_info))}

        return data


def dumpData(data, fmt=None, missing=_marker):
    """Knows how to format mongodb log record data

    This method can format log record data to a string using a formatter
    string e.g.:
    
        fmt = '[%(name)s] %(asctime)s %(mesage)s %(exception.message)s'
        fmt += ' %(exception.code)d %(exception.stackTrace)s'
        dumpData(record, fmt)

    The formatter string supports the following syntax:

    %(name)s                 Name of the logger (logging channel)
    %(levelno)s              Numeric logging level for the message (DEBUG, 
                             INFO, WARNING, ERROR, CRITICAL)
    %(levelname)s            Text logging level for the message ("DEBUG",
                             "INFO","WARNING", "ERROR", "CRITICAL")
    %(pathname)s             Full pathname of the source file where the logging
                             call was issued (if available)
    %(filename)s             Filename portion of pathname
    %(module)s               Module (name portion of filename)
    %(lineno)d               Source line number where the logging call was
                             issued (if available)
    %(funcName)s             Function name
    %(created)f              Time when the LogRecord was created (time.time()
                             return value)
    %(asctime)s              Textual time when the LogRecord was created
    %(msecs)d                Millisecond portion of the creation time
    %(relativeCreated)d      Time in milliseconds when the LogRecord was
                             created, relative to the time the logging module
                             was loaded (typically at application startup time)
    %(thread)d               Thread ID (if available)
    %(threadName)s           Thread name (if available)
    %(process)d              Process ID (if available)
    %(message)s              The result of record.getMessage(), computed just
                             as the record is emitted
    %(exception.message)s    The record.exc_info[1] message if an exc_info was
                             logged
    %(exception.code)s       0
    %(exception.stackTrace)s The formatted error message

    Also see README.txt for more information and a sample.

    """
    if fmt is None:
        fmt = "%(message)s"
    if missing is _marker:
        missing = '---'
    exception = data.get('exception', {})
    return fmt % {'name': data.get('name', missing),
                  'levelno': data.get('levelno', missing),
                  'levelname': data.get('levelname', missing),
                  'pathname': data.get('pathname', missing),
                  'filename': data.get('filename', missing),
                  'module': data.get('module', missing),
                  'lineno': data.get('lineno', missing),
                  'funcName': data.get('funcName', missing),
                  'created': data.get('created', missing),
                  'asctime': data.get('asctime', missing),
                  'msecs': data.get('msecs', missing),
                  'relativeCreated': data.get('relativeCreated', missing),
                  'thread': data.get('thread', missing),
                  'threadName': data.get('threadName', missing),
                  'process': data.get('process', missing),
                  'message': data.get('message', missing),
                  'instance': data.get('instance', missing),
                  'exception.message': exception.get('message', missing),
                  'exception.code': exception.get('code', missing),
                  'exception.stackTrace': exception.get('stackTrace', missing),
                 }
