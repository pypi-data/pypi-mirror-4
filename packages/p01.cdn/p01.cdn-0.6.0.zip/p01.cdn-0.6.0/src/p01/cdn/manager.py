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

import posixpath

import zope.interface
from zope.schema.fieldproperty import FieldProperty

from p01.cdn import interfaces


class ResourceManager(object):
    """Resource Manager"""

    zope.interface.implements(interfaces.IResourceManager)

    _version = FieldProperty(interfaces.IResourceManager['version'])
    _namespace = FieldProperty(interfaces.IResourceManager['namespace'])
    _skin = FieldProperty(interfaces.IResourceManager['skin'])
    _site = FieldProperty(interfaces.IResourceManager['site'])
    rawURI = FieldProperty(interfaces.IResourceManager['rawURI'])
    _uri = FieldProperty(interfaces.IResourceManager['uri'])
    _output = FieldProperty(interfaces.IResourceManager['output'])

    def __init__(self, version, uri, output=None, namespace=None, skin=None,
        site=None):
        # set uri arguments
        self.version = version
        self.namespace = namespace
        self.skin = skin
        self.site = site
        # setup converted uri
        self.uri = uri
        # setup output
        self.output = output

    def _convert(self):
        """Converts previous set uri with dynamic values
        
        This ensures that we convert the uri during change on everytime we
        access them.
        """
        version = self.version or 'missing-version'
        namespace = self.namespace or 'missing-namespace'
        skin = self.skin or 'missing-skin'
        site = self.site or 'missing-site'
        self._uri = self.rawURI % {'version': version,
            'namespace': namespace, 'skin': skin, 'site': site}

    @apply
    def version():
        def fget(self):
            return self._version
        def fset(self, value):
            self._version = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    @apply
    def namespace():
        def fget(self):
            return self._namespace
        def fset(self, value):
            self._namespace = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    @apply
    def skin():
        def fget(self):
            return self._skin
        def fset(self, value):
            self._skin = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    @apply
    def site():
        def fget(self):
            return self._site
        def fset(self, value):
            self._site = value
            # convertraw uri to uri
            self._convert()
        return property(fget, fset)

    @apply
    def uri():
        def fget(self):
            return self._uri
        def fset(self, uri):
            # keep a reference to the uri including formatting strings
            self.rawURI = uri
            self._convert()
        return property(fget, fset)

    @apply
    def output():
        """Return dynamicly converted output path"""
        def fget(self):
            if self._output is not None:
                return self._output % {'version': self.version,
                                       'namespace': self.namespace}
            else:
                return self._output
        def fset(self, output):
            self._output = output
        return property(fget, fset)

    def getURI(self, name=None):
        """Get the correct url based on the uri, namespace and version and
        resource name.

        We also, allow to use * as a version manager marker.

        An initial devmode uri could look like:

        http://localhost:8080/++skin++Admin/%(version)s/@@

        If your applicatiton uses site and subsite and each sub site is using
        another resource manager, the relative subsite path could get used
        as namespace. Then your uri could look like:

        http://localhost:8080/++skin++Admin/%(namespace)s/%(version)s/@@

        And the sub site could be set to something like: "root/subsite"

        A production setup does not require any special uri setup in general.
        It fully depends on your web servers rewrite rule and your extracted
        resource location. You will probably use a sub domain like:

        http://%(namespace)s.foobar.com/%(version)s/@@

        or with an additional namespace:

        http://cdn.foobar.com/%(namespace)s/%(version)s/@@

        or just as minimal as possible

        http://cdn.foobar.com/%(version)s/@@

        Note: you can also use the site and skin as a part of the uri
        formatting.

        """
        if name is None:
            # return base uri
            return self.uri
        else:
            # return resource uri
            return posixpath.join(self.uri, name)

    def __call__(self, request):
        """Let the instance act as an adapter if needed"""
        return self

    def __repr__(self):
        return '<%s %r at %r>' %(self.__class__.__name__, self.version,
            self.uri)
