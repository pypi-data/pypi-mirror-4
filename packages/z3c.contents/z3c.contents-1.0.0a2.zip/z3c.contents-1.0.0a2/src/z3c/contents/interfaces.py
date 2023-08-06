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

import zope.schema
import zope.i18nmessageid

from z3c.table import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


class IContentsPage(interfaces.ITable):
    """Container management page."""

    searchForm = zope.interface.Attribute('Search form')

    allowCut = zope.schema.Bool(
        title=u'Allow cut',
        description=(u'Allow cut operation if available.'),
        default=True)

    allowCopy = zope.schema.Bool(
        title=u'Allow copy',
        description=(u'Allow copy operation if available.'),
        default=True)

    allowDelete = zope.schema.Bool(
        title=u'Allow delete',
        description=(u'Allow delete operation if available.'),
        default=True)

    allowPaste = zope.schema.Bool(
        title=u'Allow paste',
        description=(u'Allow paste operation if available.'),
        default=True)

    allowRename = zope.schema.Bool(
        title=u'Allow rename',
        description=(u'Allow rename operation if available.'),
        default=True)

    allowSearch = zope.schema.Bool(
        title=u'Allow search',
        description=(u'Allow search.'),
        default=True)
