### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from zope.schema.interfaces import ITuple

# import local interfaces

# import Zope3 packages
from zope.interface import implements
from zope.schema import Tuple

# import local packages
from ztfy.utils.schema import DottedDecimalField


class ILocationField(ITuple):
    """Location (longitude/latitude) field interface"""


class LocationField(Tuple):
    """Longitude/latitude location field"""

    implements(ILocationField)

    def __init__(self, value_type=None, unique=False, **kw):
        super(LocationField, self).__init__(min_length=2, max_length=2,
                                            value_type=DottedDecimalField(), unique=False, **kw)
