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
from decimal import Decimal

# import Zope3 interfaces
from z3c.form.interfaces import NO_VALUE, IFieldWidget, IMultiWidget

# import local interfaces
from ztfy.geoportal.schema import ILocationField
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.browser.multi import MultiWidget
from z3c.form.converter import SequenceDataConverter
from z3c.form.widget import FieldWidget
from zope.component import adapter, adapts
from zope.interface import implementer, implements

# import local packages
from ztfy.geoportal.browser import ztfy_geoportal


class ILocationWidget(IMultiWidget):
    """Location widget interface"""


class LocationDataConverter(SequenceDataConverter):
    """Location data converter"""

    adapts(ILocationField, ILocationWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return None
        return str(value[0]), str(value[1])

    def toFieldValue(self, value):
        if not value:
            return None
        return (Decimal(value[0]), Decimal(value[1]))


class LocationWidget(MultiWidget):
    """Location widget"""

    implements(ILocationWidget)

    @property
    def longitude_id(self):
        return '%s-longitude' % self.id

    @property
    def longitude_name(self):
        return '%s.longitude' % self.name

    @property
    def longitude(self):
        return self.value and self.value[0] or ''

    @property
    def latitude_id(self):
        return '%s-latitude' % self.id

    @property
    def latitude_name(self):
        return '%s.latitude' % self.name

    @property
    def latitude(self):
        return self.value and self.value[1] or ''

    def extract(self, default=NO_VALUE):
        longitude = self.request.get(self.longitude_name)
        latitude = self.request.get(self.latitude_name)
        if not (longitude and latitude):
            return default
        return (longitude, latitude)

    def render(self):
        result = super(LocationWidget, self).render()
        if result:
            ztfy_geoportal.need()
        return result

@adapter(ILocationField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def LocationFieldWidgetFactory(field, request):
    """ILocationField widget factory"""
    return FieldWidget(field, LocationWidget(request))
