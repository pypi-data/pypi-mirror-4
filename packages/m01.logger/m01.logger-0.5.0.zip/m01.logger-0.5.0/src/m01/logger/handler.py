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
import logging.handlers
import pymongo

import m01.logger.formatter


class MongoHandler(logging.handlers.BufferingHandler):
    """MongoHandler instances dispatch logging events to mongodb.
    
    Note: the initial level will be NOTSET. This means the parent logger will
    defind the level used for logging and not as described in the pyhton
    documentation any log information. The python documentation is describes
    the logging concept not correct. If you need to log any information simply
    set the logger level to DEBUG e.g.:
    
    logger.setLevel(logging.DEBUG)

    """

    def __init__(self, connector, level=logging.NOTSET, capacity=1, 
        instance='noinstance'):
        # the ``connector`` is a callable collection getter method
        self._connector = connector
        # init handler
        logging.Handler.__init__(self, level)
        super(MongoHandler, self).__init__(capacity)
        # use our formatter
        self.formatter = m01.logger.formatter.MongoFormatter(instance)
        # setup buffer, how many entries to keep around till we write to mongo
        self.capacity = capacity
        self._instance = instance

    @property
    def collection(self):
        return self._connector()

    @property
    def database(self):
        return self.collection.database

    @property
    def connection(self):
        return self.database.connection

    def flush(self):
        """Insert records as batch into mongodb if capacity is reached"""
        try:
            # not safe insert in batch, don't manipulate, don't
            # check keys and also keep going on errors. I think we
            # won't miss missing log calls
            data = [self.format(rec) for rec in self.buffer]
            if data:
                self.collection.insert(data,
                    manipulate=False, safe=False, check_keys=False,
                    continue_on_error=True)
                self.buffer = []
        except pymongo.errors.AutoReconnect:
            # catch connection error which happens during atexit
            pass

    def format(self, record):
        """Format the specified record within our MongoFormatter."""
        return self.formatter.format(record)

    def close(self):
        """Closes the mongodb."""
        try:
            self.flush()
        except pymongo.errors.AutoReconnect:
            pass
        logging.Handler.close(self)

    def __repr__(self):
        try:
            database = self.collection.database.name
            collection = self.collection.name
        except pymongo.errors.AutoReconnect:
            database = 'unknown'
            collection = 'unknown'
        return "<MongoHandler %s.%s; from %s>" % (database, collection,
            self._instance)

