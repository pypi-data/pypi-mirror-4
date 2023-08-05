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
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from z3c.form import field
from zope.container.contained import Contained
from zope.interface import implements, Interface
from zope.schema import TextLine
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.geoportal.schema import LocationField
from ztfy.skin.form import AddForm, EditForm
from ztfy.skin.menu import MenuItem


class IGeoportalTest(Interface):
    """GeoPortal test interface"""

    title = TextLine(title=u"Title", required=True)

    location = LocationField(title=u"GPS location", required=False)


class GeoportalTest(Persistent, Contained):
    """GeoPortal test class"""

    implements(IGeoportalTest)

    title = FieldProperty(IGeoportalTest['title'])
    location = FieldProperty(IGeoportalTest['location'])


class GeoportalTestAddFormMenuItem(MenuItem):
    """GeoPortal test add menu item"""
    title = ":: Add GeoPortal test..."


class GeoportalTestAddForm(AddForm):
    """GeoPortal test add form"""

    fields = field.Fields(IGeoportalTest)

    def create(self, data):
        test = GeoportalTest()
        test.title = data.get('title')
        return test

    def add(self, object):
        self.context[object.title] = object

    def nextURL(self):
        return '%s/@@contents.html' % absoluteURL(self.context, self.request)


class GeoportalTestEditForm(EditForm):
    """GeoPortal test edit form"""

    fields = field.Fields(IGeoportalTest)
