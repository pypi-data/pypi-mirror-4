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
from ztfy.geoportal.interfaces import IGeoportalConfigurationUtility, \
                                      IGeoportalLocation
from ztfy.skin.interfaces import IDialogDisplayFormButtons

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility

# import local packages
from ztfy.geoportal.location import GeoportalLocation
from ztfy.skin.form import DialogEditForm


class GeoportalLocationEditForm(DialogEditForm):
    """Geoportal location edit form"""

    prefix = 'location.'
    fields = field.Fields(IGeoportalLocation)
    buttons = button.Buttons(IDialogDisplayFormButtons)

    widgets_prefix = ViewPageTemplateFile('templates/location.pt')

    def getContent(self):
        location = IGeoportalLocation(self.context, None)
        if location is not None:
            return location
        else:
            return GeoportalLocation()

    @property
    def geoportal_key(self):
        config = queryUtility(IGeoportalConfigurationUtility)
        if config is not None:
            return config.api_key

    @jsaction.handler(buttons['dialog_close'])
    def close_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    def applyChanges(self, data):
        pass

    def getOutput(self, writer, parent, changes=()):
        return writer.write({ 'output': u'PASS' })
