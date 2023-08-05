###############################################################################
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
###############################################################################
"""
$Id: tz_util.py 3560 2012-12-19 05:18:50Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import datetime

# UTC support
ZERO = datetime.timedelta(0)


class FixedOffsetBase(datetime.tzinfo):
    """Fixed offset base class."""

    def __init__(self, offset, name):
        if isinstance(offset, int):
            offset = datetime.timedelta(minutes=offset)
        self.__offset = offset
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        return self.__name


class FixedOffset(FixedOffsetBase):
    """Pickable implementation of fixed offset used for deepcopy."""

    def __init__(self, offset=None, name=None):
        FixedOffsetBase.__init__(self, offset, name)

# Fixed offset timezone representing UTC
UTC = FixedOffset(0, "UTC")
