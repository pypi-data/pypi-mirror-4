##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
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

import m01.logger.handler

from m01.mongo import pool


def setUpMongoLogger(name, connector, level, capacity, instance, propagate):
    """Setup mongo logging handler based on a given collection getter method"""
    # setup handler
    handler = m01.logger.handler.MongoHandler(connector, level, capacity,
        instance)
    # setup logger
    logger = logging.getLogger(name)
    logging._acquireLock()
    try:
        logger.addHandler(handler)
    finally:
        logging._releaseLock()
    logger.propagate = propagate
    return logger
