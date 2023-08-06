##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

import base64
import zope.i18nmessageid
from zope.traversing import api
from zope.traversing.browser import absoluteURL

from z3c.table import column

_ = zope.i18nmessageid.MessageFactory('z3c')


class RenameColumn(column.NameColumn):
    """Rename column."""

    weight = 20
    errorMessages = {}

    @property
    def isExecuted(self):
        renameAction = self.table.actions.get('rename')
        if renameAction and renameAction.isExecuted():
            return True

    def getSortKey(self, item):
        return api.getName(item)

    def getItemValue(self, item):
        return api.getName(item)

    def getItemKey(self, item):
        name = self.getItemValue(item)
        base64Name = base64.urlsafe_b64encode(name.encode('utf-8'))
        base64Name = base64Name.decode('utf-8')
        return '%s-%s-rename' % (self.id, base64Name)

    def getRenameValue(self, item):
        key = self.getItemKey(item)
        return self.request.get(key)

    def renderLink(self, item):
        return '<a href="%s">%s</a>' % (absoluteURL(item, self.request), 
            api.getName(item))

    def renderCell(self, item):
        key = self.getItemKey(item)
        value = self.getItemValue(item)
        itemLink = self.renderLink(item)
        newName = self.getRenameValue(item)
        if newName is None:
            newName = self.getItemValue(item)
        if self.isExecuted and item in self.table.selectedItems:
            msg = self.errorMessages.get(key, u'')
            return u'%s&nbsp;<input type="text" name="%s" value="%s" />%s' % (
                itemLink, key, newName, msg)
        else:
            return itemLink

