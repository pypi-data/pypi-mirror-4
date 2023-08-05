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
"""Resource factories and resources

Note; our resource factories defined below, will process the uri based on the
given resource maanger during resource lookup. This is required since we
support the z3c.baseregistry. If you need more speedup, you can define your
own resource factories and use them in the resource zcml directives.

Especialy if you only use one resource manager, you can simply define a
resource manger and override the getResourceManager method in the resource
factories defined below.

$Id:$
"""
__docformat__ = "reStructuredText"


import os
import time
try:
    from email.utils import formatdate, parsedate_tz, mktime_tz
except ImportError: # python 2.4
    from email.Utils import formatdate, parsedate_tz, mktime_tz

import zope.interface
import zope.component
import zope.location
import zope.publisher.http
from zope.site import hooks
from zope.contenttype import guess_content_type
from zope.publisher.interfaces import NotFound
from zope.i18n.interfaces import INegotiator
from zope.publisher.interfaces.browser import IBrowserPublisher

from z3c.zrtresource.processor import ZRTProcessor
from z3c.zrtresource.replace import Replace

from p01.cdn import interfaces


# 10 years expiration date
DEFAULT_CACHE_TIMEOUT = 10 * 365 * 24 * 60 * 60

_marker = object()


def empty():
    return ''


def setCacheControl(response, secs=DEFAULT_CACHE_TIMEOUT):
    # 10 years cache timeout by default
    response.setHeader('Cache-Control', 'public,max-age=%s' % secs)
    t = time.time() + secs
    response.setHeader('Expires', formatdate(t, usegmt=True))


class File(object):
    
    def __init__(self, path, name):
        self.path = path
        self.__name__ = name

        f = open(path, 'rb')
        data = f.read()
        f.close()

        self.content_type = guess_content_type(path, data)[0]
        self.lmt = float(os.path.getmtime(path)) or time.time()
        self.lmh = formatdate(self.lmt, usegmt=True)


# factories
class ResourceFactory(object):
    """Resource factory"""

    def __init__(self, path, checker, manager, name, rPath=None):
        self.__file = File(path, name)
        self.__checker = checker
        self.__manager = manager
        self.__name = name
        # setup relative resource name if given
        if rPath is not None:
            self.__rPath = rPath
        else:
            # otherwise usethe resource name
            self.__rPath = name

    def getResourceManager(self, request):
        """Retruns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self.__manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        uri = manager.getURI(self.__rPath)
        resource = CDNResource(manager, self.__file, request, uri)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource


class ZRTResourceFactory(object):
    """ZRT Resource factory."""

    def __init__(self, path, checker, manager, name, rPath=None):
        self.__file = File(path, name)
        self.__checker = checker
        self.__manager = manager
        self.__name = name
        # setup relative resource name if given
        if rPath is not None:
            self.__rPath = rPath
        else:
            # otherwise usethe resource name
            self.__rPath = name

    def getResourceManager(self, request):
        """Retruns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self.__manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        uri = manager.getURI(self.__rPath)
        resource = ZRTCDNResource(manager, self.__file, request, uri)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource


class I18nResourceFactory(object):
    """I18n resource factory."""

    def __init__(self, data, manager, name, defaultLanguage, checker):
        self.__data = data
        self.__uris = []
        self.__manager = manager
        self.__name = name
        self.__defaultLanguage = defaultLanguage
        self.__checker = checker

    def getResourceManager(self, request):
        """Retruns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self.__manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        resource =  I18nCDNResource(manager, self.__data, request,
            self.__defaultLanguage)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource


class SubDirectoryResourceFactory(object):
    """Sub directory factory"""

    def __init__(self, data, path, checker, manager, name, rName, excludeNames):
        self.data = data
        self.__path = path
        self.__checker = checker
        self.__manager = manager
        self.__name = name
        self.__rName = rName
        self.__excludeNames = excludeNames

    def getResourceManager(self, request):
        """Retruns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self.__manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        resource = CDNResourceDirectory(manager, self.data,  self.__path,
            self.__name, self.__rName, request, self.__excludeNames)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource


class DirectoryResourceFactory(object):

    data = {}

    def __init__(self, path, checker, manager, name, excludeNames):
        self.__path = path
        self.__checker = checker
        self.__manager = manager
        self.__name = name
        self.__excludeNames = excludeNames
        self.setupData()

    def getStructure(self, basePath, path, data):
        """Populate the directory structure with the right factories during
        zcml configuration loading.
        
        This allows us to read and setup the directory and file factories
        without to define the uri during zcml configuration. The uri will still
        get built based on the resource manager during resource access. 

        """
        for name in os.listdir(path):
            if name.startswith('.'):
                continue
            if name in self.__excludeNames:
                continue
            data[name] = {}
            objPath = os.path.join(path, name)
            # setup relative path, including convert windows os.sep to '/'
            rPath = objPath.replace(basePath + os.sep, '').replace('\\', '/')
            if os.path.isdir(objPath):
                subData = self.getStructure(basePath, objPath, {})
                data[name]['factory'] = SubDirectoryResourceFactory(subData,
                    path, self.__checker, self.__manager, name, rPath,
                    self.__excludeNames)
            else:
                data[name]['factory'] = ResourceFactory(objPath,
                    self.__checker, self.__manager, name, rPath)
        return data

    def setupData(self):
        """Setup directory structure"""
        # condition
        if not os.path.isdir(self.__path):
            raise TypeError("p01.cdnDirectory must be a directory", self.__path)
        # get base path for given directory and start producing nested
        # directory and file structure
        basePath = os.path.dirname(self.__path)
        self.data = self.getStructure(basePath, self.__path, {})

    def getResourceManager(self, request):
        """Retruns the correct resource manager"""
        return zope.component.getAdapter(request, interfaces.IResourceManager,
            name=self.__manager)

    def __call__(self, request):
        manager = self.getResourceManager(request)
        resource = CDNResourceDirectory(manager, self.data,  self.__path,
            self.__name, self.__name, request, self.__excludeNames)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource


class ResourcePublisher(object):
    """Knows how to serv a resource."""

    zope.interface.implements(IBrowserPublisher)

    # 10 years expiration date
    cacheTimeout = DEFAULT_CACHE_TIMEOUT

    def publishTraverse(self, request, name):
        """Raise NotFound if someone tries to traverse it.
        """
        raise NotFound(None, name)

    def browserDefault(self, request):
        """Return a callable for processing browser requests."""
        return getattr(self, request.method), ()

    def GET(self):
        """Return the file data for downloading with GET requests."""
        request = self.request
        response = request.response

        setCacheControl(response, self.cacheTimeout)

        # HTTP If-Modified-Since header handling..
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:
                mod_since = long(mktime_tz(parsedate_tz(header)))
            except:
                mod_since = None
            if mod_since is not None:
                if getattr(self.context, 'lmt', None):
                    last_mod = long(self.context.lmt)
                else:
                    last_mod = 0L
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        response.setHeader('Content-Type', self.context.content_type)
        response.setHeader('Last-Modified', self.context.lmh)

        f = open(self.context.path, 'rb')
        data = f.read()
        f.close()
        return data

    def HEAD(self):
        """Return proper headers and no content for HEAD requests."""
        response = self.request.response
        response.setHeader('Content-Type', self.context.content_type)
        response.setHeader('Last-Modified', self.context.lmh)
        setCacheControl(response, self.cacheTimeout)
        return ''


class CDNResource(ResourcePublisher, zope.location.Location):
    """CDN resource implementation."""

    zope.interface.implements(interfaces.ICDNResource)

    def __init__(self, manager, context, request, uri):
        self.manager = manager
        self.context = context
        self.path = context.path
        self.request = request
        self.uri = uri

    def __call__(self):
        return self.uri

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class ZRTCDNResource(CDNResource):
    """ZRT CDN resource implementation."""

    zope.interface.implements(interfaces.IZRTCDNResource)

    def _encodeResult(self, data):
        response = self.request.response
        encoding = zope.publisher.http.getCharsetUsingRequest(
            self.request) or 'utf-8'
        content_type = response.getHeader('Content-Type')

        if isinstance(data, unicode):
            major, minor, params = zope.contenttype.parse.parse(content_type)

            if 'charset' in params:
                encoding = params['charset']

            try:
                data = data.encode(encoding)
            except UnicodeEncodeError:
                # RFC 2616 section 10.4.7 allows us to return an
                # unacceptable encoding instead of 406 Not Acceptable
                # response.
                encoding = 'utf-8'
                data = data.encode(encoding)

            params['charset'] = encoding
            content_type = "%s/%s;" % (major, minor)
            content_type += ";".join(k + "=" + v for k, v in params.items())
            response.setHeader('Content-Type', content_type)

        # set lenght
        response.setHeader('Content-Length', str(len(data)))
        return data

    def GET(self):
        data = super(ZRTCDNResource, self).GET()
        zp = ZRTProcessor(data, commands={'replace': Replace})
        # Note: we run into a ValueError because of using unicode
        # with application/javascript content_type.
        # Use a DirectResult which will bypass the _implicitResult
        # method from zope.publisher.http line 799
        # return zp.process(hooks.getSite(), self.request)

        # bugfix, encode and use DirectResult
        data = zp.process(hooks.getSite(), self.request)
        body = self._encodeResult(data)
        return zope.publisher.http.DirectResult((body,))


class I18nCDNResource(ResourcePublisher, zope.location.Location):
    """I18n CDN resource implementation."""

    zope.interface.implements(interfaces.II18nCDNResource)

    def __init__(self, manager, data, request, defaultLanguage):
        self.manager = manager
        self._data = data
        self.request = request
        self.defaultLanguage = defaultLanguage

    def getURI(self, lang):
        f = self._data[language]
        return self.manager.getURI(f.__name__)

    def getPath(self, lang):
        f = self._data[language]
        return f.path

    def getPaths(self):
        """Used for extract paths, see p01.recipe.cdn/extract.py"""
        for f in self._data.values():
            yield f.path

    def getURIs(self):
        """Used for extract uris, see p01.recipe.cdn/extract.py"""
        for f in self._data.values():
            yield self.manager.getURI(f.__name__)

    def __call__(self):
        langs = self._data.keys()
        negotiator = zope.component.getUtility(INegotiator)
        language = negotiator.getLanguage(langs, self.request)
        try:
            return self.getURI(language)
        except KeyError:
            return self.getURI(self.defaultLanguage)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


# Directory resource
class CDNResourceDirectory(ResourcePublisher, zope.location.Location):

    zope.interface.implements(interfaces.ICDNResourceDirectory)

    def __init__(self, manager, data, path, name, rName, request,
        excludeNames=[]):
        self.manager = manager
        self.data = data
        self.path = path
        self.__name__ = name
        self.__rName = rName
        self.request = request
        self.excludeNames = excludeNames

    def publishTraverse(self, request, name):
        """See interface IBrowserPublisher"""
        return self.get(name)

    def browserDefault(self, request):
        """See interface IBrowserPublisher"""
        return empty, ()

    @property
    def uri(self):
        return self()

    def __call__(self):
        return self.manager.getURI(self.__rName)

    def __getitem__(self, name):
        res = self.get(name, None)
        if res is None:
            raise KeyError(name)
        return res

    def get(self, name, default=_marker):
        if name not in self.excludeNames:
            data = self.data.get(name)
            if data is not None:
                factory = data['factory']
                resource = factory(self.request)
                resource.__parent__ = self
                return resource
            else:
                raise NotFound(self.__name__, name)
