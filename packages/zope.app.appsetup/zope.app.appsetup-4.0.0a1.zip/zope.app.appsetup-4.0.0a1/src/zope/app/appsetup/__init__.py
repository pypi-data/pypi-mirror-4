##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Zope Application Server setup package

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.appsetup.appsetup import config, database

#BBB
from zope.app.appsetup.interfaces import IDatabaseOpenedEvent, DatabaseOpened
from zope.app.appsetup.interfaces import IProcessStartingEvent, ProcessStarting
