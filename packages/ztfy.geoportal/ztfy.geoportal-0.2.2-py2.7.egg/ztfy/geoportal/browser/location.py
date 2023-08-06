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
from z3c.form.interfaces import HIDDEN_MODE

# import local interfaces
from ztfy.geoportal.interfaces import IGeoportalConfigurationUtility, \
                                      IGeoportalLocation, IGeoportalLocationEditForm
from ztfy.skin.interfaces import IDialogDisplayFormButtons

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from zope.component import queryUtility
from zope.interface import implements

# import local packages
from ztfy.geoportal.location import GeoportalLocation
from ztfy.skin.form import DialogEditForm
from ztfy.utils.property import cached_property


class GeoportalLocationEditForm(DialogEditForm):
    """Geoportal location edit form"""

    implements(IGeoportalLocationEditForm)

    prefix = 'location.'
    fields = field.Fields(IGeoportalLocation)
    buttons = button.Buttons(IDialogDisplayFormButtons)

    def updateWidgets(self):
        super(GeoportalLocationEditForm, self).updateWidgets()
        self.widgets['longitude'].mode = HIDDEN_MODE
        self.widgets['latitude'].mode = HIDDEN_MODE

    def getContent(self):
        location = IGeoportalLocation(self.context, None)
        if location is not None:
            return location
        else:
            return GeoportalLocation()

    @cached_property
    def config(self):
        return queryUtility(IGeoportalConfigurationUtility)

    @property
    def geoportal_key(self):
        config = self.config
        if config is not None:
            return config.api_key

    @property
    def geoportal_version(self):
        config = self.config
        if config is not None:
            return config.version

    @property
    def geoportal_devel(self):
        config = self.config
        if config is not None:
            return config.development

    @jsaction.handler(buttons['dialog_close'])
    def close_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    def applyChanges(self, data):
        pass

    def getOutput(self, writer, parent, changes=()):
        return writer.write({ 'output': u'PASS' })
