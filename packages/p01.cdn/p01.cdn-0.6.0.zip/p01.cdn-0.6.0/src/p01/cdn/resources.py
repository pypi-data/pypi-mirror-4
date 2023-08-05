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

import zope.interface
import zope.component
import zope.location
from zope.publisher.interfaces import NotFound
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher

from p01.cdn import interfaces


def empty():
    return ''


class Resources(BrowserView):
    """A view that can be traversed further to access browser resources."""

    zope.interface.implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.browser.IBrowserPublisher interface"""
        resource = zope.component.queryAdapter(request, name=name)
        if resource is None:
            raise NotFound(self, name)

        zope.location.locate(resource, self.context, name)
        return resource

    def browserDefault(self, request):
        """See zope.publisher.interfaces.browser.IBrowserPublisher interface"""
        return empty, ()

    def __getitem__(self, name):
        """A helper method to make this view usable from templates,
        so resources can be acessed in template like context/@@/<resourcename>.
        """
        return self.publishTraverse(self.request, name)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class VersionResources(Resources):
    """Version resource"""

    _version = None

    @property
    def version(self):
        if self._version is None:
            vm = interfaces.IResourceManager(self.request)
            self._version = vm.version
        return self._version

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.browser.IBrowserPublisher interface"""
        # first check the version
        if self.version == name:
            resource = Resources(self.context, self.request)
        else:
            resource = zope.component.queryAdapter(request, name=name)
            if resource is None:
                raise NotFound(self, name)

        zope.location.locate(resource, self.context, name)
        return resource

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._version)
