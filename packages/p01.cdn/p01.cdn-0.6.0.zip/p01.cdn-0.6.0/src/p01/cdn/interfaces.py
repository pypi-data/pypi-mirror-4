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
import zope.schema


class IResourceManager(zope.interface.Interface):
    """Resource manager (adapter) adapting the resource layer"""

    rawURI = zope.schema.ASCIILine(
        title=u'Raw resource base uri including fomratting arguments',
        description=u'Raw resource base uri including fomratting arguments',
        default='',
        required=False)

    uri = zope.schema.ASCIILine(
        title=u'Formatted resource base uri',
        description=u'Formatted resource base uri',
        default=None,
        required=False)

    version = zope.schema.ASCIILine(
        title=u'Resource manger version',
        description=u'Resource manger version',
        required=True)

    # optional uri substitution arguments
    namespace = zope.schema.ASCIILine(
        title=u'Resource manager namespace',
        description=u'Resource manager namespace',
        default='',
        required=False)

    skin = zope.schema.ASCIILine(
        title=u'Skin name',
        description=u'Skin name',
        default='',
        required=False)

    site = zope.schema.ASCIILine(
        title=u'Site name',
        description=u'Site name',
        default='',
        required=False)

    # Note, this output is optional and only required for resource extraction
    # If this output is None, the p01.recipe.cdn output script option is used.
    # See p01.recipe.cdn extract.py for more information
    # Note: if a recipe output option is used, the namespace will get ignored
    # too
    output = zope.schema.ASCIILine(
        title=u'Resource extract output dir path',
        description=u'Resource extract output dir path',
        default=None,
        required=False)

    def getURI(name=None):
        """Build the correct url based on the uri, namespace and version and
        resource name.

        We also, allow to use * as a version manager marker.

        An initial devmode uri could look like:

        http://localhost:8080/++skin++Admin/%(version)s/@@
        
        If your applicaiton uses site and subsite and each sub site is useing
        another resource manager, the relative subsite path could get used
        as namespace. Then you uri could look like:
        
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

        """


class ICDNResource(zope.interface.Interface):
    """Offloacdnd resource.

    This offload resource allows us to configure resources with custom urls. 
    This is used if you like to offload static resources form the zope and 
    it's fornt end proxy server. Each off load resource contains it's own url
    which can point to another subdomain.
    
    Note, take care if you use SSL, make sure that you use a wildcard 
    certificate which is valid for different subdomains. This is a new kind of
    certificate which only some certificate seller offer. One of such a seller
    is www.godaddy.com. Take care and don't get confused, normaly a wildcard 
    certificate is only valid for one domain but for more then one server IP 
    address.
    """


class IZRTCDNResource(ICDNResource):
    """CDN zrt resource."""


class II18nCDNResource(ICDNResource):
    """CDN i18n resource."""


class ICDNResourceDirectory(ICDNResource):
    """CDN resource directory."""
