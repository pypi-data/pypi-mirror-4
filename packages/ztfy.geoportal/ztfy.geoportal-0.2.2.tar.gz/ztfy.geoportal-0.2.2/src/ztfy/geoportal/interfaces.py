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

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import TextLine, Bool

# import local packages
from ztfy.utils.schema import DottedDecimalField

from ztfy.geoportal import _


class IGeoportalConfigurationUtility(Interface):
    """GeoPortal utility configuration interface"""

    api_key = TextLine(title=_("GeoPortal API key"),
                       required=True)

    version = TextLine(title=_("GeoPortal version"),
                       required=True,
                       default=u'latest')

    development = Bool(title=_("Use development version ?"),
                       required=True,
                       default=False)


class IGeoportalLocation(Interface):
    """Geoportal location fields interface"""

    longitude = DottedDecimalField(title=_("Longitude"),
                                   description=_("Longitude field in WGS84 coordinates system"),
                                   required=False)

    latitude = DottedDecimalField(title=_("Latitude"),
                                  description=_("Latitude field in WGS84 coordinates system"),
                                  required=False)


class IGeoportalLocationEditForm(Interface):
    """Geoportal location edit form marker interface"""
