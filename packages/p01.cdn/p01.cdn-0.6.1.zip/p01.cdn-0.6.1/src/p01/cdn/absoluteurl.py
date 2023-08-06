##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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

import urllib
import zope.component
import zope.interface
import zope.i18nmessageid
import zope.location.interfaces
from zope.proxy import sameProxiedObjects
from zope.publisher.browser import BrowserView
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.publisher.interfaces.browser import IBrowserRequest

from p01.cdn import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')

_insufficientContext = _("There isn't enough context to get URL information. "
                         "This is probably due to a bug in setting up location "
                         "information.")

_safe = '@+' # Characters that we don't want to have quoted


class AbsoluteURLForCDNResource(BrowserView):

    zope.interface.implementsOnly(IAbsoluteURL)
    zope.component.adapts(interfaces.ICDNResource, IBrowserRequest)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        uri = self.context()
        return urllib.quote(uri.encode('utf-8'), _safe)

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        # We do this here do maintain the rule that we must be wrapped
        context = zope.location.interfaces.ILocation(context, context)
        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(_insufficientContext)

        if sameProxiedObjects(context, request.getVirtualHostRoot()) or \
               isinstance(context, Exception):
            return ({'name':'', 'url': self.request.getApplicationURL()}, )

        base = tuple(zope.component.getMultiAdapter(
                (container, request), name='absolute_url').breadcrumbs())

        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError(_insufficientContext)

        if name:
            base += ({'name': name, 'url': str(self)},)

        return base
