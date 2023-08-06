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

import lxml
import zope.component
import zope.interface
from zope.annotation.interfaces import IAnnotations
from zope.container.interfaces import IContainer
from zope.container.interfaces import IContained
from zope.container import btree
from zope.copypastemove import ContainerItemRenamer
from zope.copypastemove import ObjectMover
from zope.copypastemove import ObjectCopier
from zope.copypastemove import PrincipalClipboard
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.copypastemove.interfaces import IObjectMover
from zope.copypastemove.interfaces import IObjectCopier
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.index.text.interfaces import ISearchableText

from zope.site.testing import siteSetUp, siteTearDown
from zope.traversing import testing as traversing

import z3c.macro.tales
import z3c.layer.ready2go
import z3c.table.testing
import z3c.contents.value


###############################################################################
#
# test component
#
###############################################################################

@zope.interface.implementer(IContainer)
class SampleContainer(btree.BTreeContainer):
    """Sample container."""


class IContentsTestBrowserLayer(z3c.layer.ready2go.IReady2GoBrowserLayer):
        """test layer."""


class IContentsTestBrowserSkin(IContentsTestBrowserLayer):
    """The browser skin."""


class IContent(zope.interface.Interface):

    title = zope.schema.TextLine(title=u'Title')
    number = zope.schema.Int(title=u'Number')


@zope.interface.implementer(IContent)
class Content(object):
    """Sample content which is pickable for copy test."""


    def __init__(self, title, number):
        self.title = title
        self.number = number

    def __repr__(self):
        return u'<%s %s %s>' % (self.__class__.__name__, self.title,
            self.number)


@zope.interface.implementer(ISearchableText)
@zope.component.adapter(IContent)
class SearchableTextForContent:

    def __init__(self, content):
        self.content = content

    def getSearchableText(self):
        return '%s %d' % (self.content.title, self.content.number)


###############################################################################
#
# testing helper
#
###############################################################################

def printElement(browser, xpath, multiple=False, serialize=True):
    """Print method to use with z3c.etestbrowser"""
    result = [serialize and lxml.etree.tounicode(elem) or elem
              for elem in browser.etree.xpath(xpath)]
    if not multiple:
        print(result[0])
        return
    for elem in result:
        print(elem)


@zope.interface.implementer(IAnnotations)
class PrincipalAnnotations(dict):
    data = {}
    def __new__(class_, context=None):
        try:
            annotations = class_.data[str(context)]
        except KeyError:
            annotations = dict.__new__(class_)
            class_.data[str(context)] = annotations
        return annotations
    def __init__(self, context):
        pass
    def __repr__(self):
        return "<%s.PrincipalAnnotations object>" % __name__


###############################################################################
#
# testing setup
#
###############################################################################

def setUp(test):
    test.globs = {'root': siteSetUp(True)}

    traversing.setUp()

    from zope.browserpage import metaconfigure
    metaconfigure.registerType('macro', z3c.macro.tales.MacroExpression)

    zope.component.provideAdapter(ObjectCopier, (IContained,), IObjectCopier)
    zope.component.provideAdapter(ObjectMover, (IContained,), IObjectMover)
    zope.component.provideAdapter(ContainerItemRenamer, (IContainer,),
        IContainerItemRenamer)

    zope.component.provideAdapter(PrincipalClipboard, (IAnnotations,),
        IPrincipalClipboard)
    # use None as principal
    zope.component.provideAdapter(PrincipalAnnotations, (None,),
        IAnnotations)

    # dublin core stub adapter
    zope.component.provideAdapter(z3c.table.testing.DublinCoreAdapterStub)

    # value adapter
    zope.component.provideAdapter(z3c.contents.value.SearchableValues)


def tearDown(test):
    siteTearDown()


def doctestSetUp(test):
    from zope.app.testing import functional
    functional.FunctionalTestSetup().setUp()
    test.globs['getRootFolder'] = functional.getRootFolder
    test.globs['printElement'] = printElement

def doctestTearDown(test):
    from zope.app.testing import functional
    functional.FunctionalTestSetup().tearDown()
