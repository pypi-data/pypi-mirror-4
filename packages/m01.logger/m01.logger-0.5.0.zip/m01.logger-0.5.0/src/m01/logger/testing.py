##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
__docformat__ = "reStructuredText"

import logging
import os.path

testLogger = None
orgLevelNames = None
orgHandlers = None
orgHandlerList = None
orgLoggers = None

import m01.mongo.pool
import m01.mongo.testing
import m01.stub.testing
import m01.logger.handler


def setUp(test, capacity=None):
    """Logger testing setup
    
    Note: this logger setUp and tearDown method is only used because the tests
    can run in a loop and we have to make sure that we correct remove our
    logger.

    You don't need such a setup in your application. You can simply setup
    your logger within the following call:

    LOGGER = m01.logger.setUpMongoLogger('m01.logger.testing', connector,
        level, capacity, instance, propagate)

    Normaly setUpMongoLogger get only called once and the returned logger can
    get used anywhere for logging. But you can also simply ignore the returned
    LOGGER instance and allways get the registered logger within the python API
    e.g.

    logging.getLogger('m01.logger.testing')

    """

    # first store the original logging onfiguration
    global testLogger
    global orgLevelNames
    global orgHandlers
    global orgHandlerList
    global orgLoggers
    loggerDict = logging.getLogger().manager.loggerDict
    logging._acquireLock()
    try:
        orgHandlers = logging._handlers.copy()
        orgHandlerList = logging._handlerList[:]
        orgLoggers = loggerDict.copy()
        orgLevelNames = logging._levelNames.copy()
        # now setup our new logger
        host = 'localhost'
        port = 45017
        pool = m01.mongo.pool.MongoConnectionPool(host, port)
        connection = pool.connection
        size = 5*1024*1024
        connection.loging.create_collection('testing', capped=True, size=size)
        def connector():
            pool = m01.mongo.pool.MongoConnectionPool
            return connection['m01_logger_testing']['testing']
        level = 10
        capacity = capacity
        instance = u'testinstance'
        propagate = False
        testLogger = m01.logger.setUpMongoLogger('m01.logger.testing',
            connector, level, capacity, instance, propagate)
    finally:
        logging._releaseLock()


def tearDown(test):
    global testLogger
    global orgLevelNames
    global orgHandlers
    global orgHandlerList
    global orgLoggers
    # bring back the original logging configuration
    logging._acquireLock()
    try:
        # first drop our mongodb test database
        testHandler = testLogger.handlers[0]
        testHandler.connection.m01_logger_testing.drop_collection('testing')
        testHandler.connection.drop_database('m01_logger_testing')
        testHandler.close()
        testLogger.removeHandler(testHandler)
        # bring back the original handlers
        logging._levelNames.clear()
        logging._levelNames.update(orgLevelNames)
        logging._handlers.clear()
        logging._handlers.update(orgHandlers)
        logging._handlerList[:] = orgHandlerList
        loggerDict = logging.getLogger().manager.loggerDict
        loggerDict.clear()
        loggerDict.update(orgLoggers)
    finally:
        logging._releaseLock()
        testLogger = None
        orgLevelNames = None
        orgHandlers = None
        orgHandlerList = None
        orgLoggers = None


def setUpMongoDB(test, capacity=None):
    host = 'localhost'
    port = 45017
    sandBoxDir = os.path.join(os.path.dirname(__file__), 'sandbox')
    m01.stub.testing.startMongoDBServer(host, port, sandBoxDir=sandBoxDir)
    setUp(test, capacity)


def setUpMongoDBOverrideCapacity(test):
    setUpMongoDB(test, 5)


def tearDownMongoDB(test):
    tearDown(test)
    m01.stub.testing.stopMongoDBServer()

