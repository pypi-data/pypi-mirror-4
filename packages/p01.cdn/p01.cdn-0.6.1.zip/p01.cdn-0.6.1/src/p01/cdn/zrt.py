##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Templated Resource Processor

$Id: zrt.py 3665 2013-03-12 13:52:38Z roger.ineichen $
"""
__docformat__='restructuredtext'

import re
import zope.interface
import zope.component

import z3c.zrtresource.interfaces
import z3c.zrtresource.replace
import z3c.zrtresource.processor



class CDNInputExpression(z3c.zrtresource.replace.BaseExpression):
    """A simple string input expression"""
    zope.interface.implements(z3c.zrtresource.interfaces.IZRTOutputExpression)

# XXX: Backport to z3c.zrtresource
# XXX: probably RegexInputExpression is also broken
    def process(self, text, outputExpr, count=None):
        """Process simple string without backslash convertion

        Prevent backslash convertion, see re.sub documenations which says:
        any backslash escapes in it are processed. That is, \n is converted
        to a single newline character.
        This shold fix an issue with json2.js which has the following code:

        meta = {    // table of character substitutions
           '\b': '\\b',
           '\t': '\\t',
           '\n': '\\n',
           '\f': '\\f',
           '\r': '\\r',
           '"' : '\\"',
           '\\': '\\\\'
        },
        """
        regex = re.compile(re.escape(r'%s' % self.source))
        return regex.subn(r'%s' % outputExpr.process(), r'%s' % text, count or 0)


class CDNIncludeOutputExpression(z3c.zrtresource.replace.BaseExpression):
    """CDN resource include expression"""

    zope.interface.implements(z3c.zrtresource.interfaces.IZRTOutputExpression)

    def process(self, **kw):
        # Ignore any keyword arguments, since this is static replacement
        name = self.source
        resource = zope.component.queryAdapter(self.request, name=name)
        f = open(resource.path, 'rb')
        data = f.read()
        f.close()
        data = data.decode('utf-8', 'replace')
        # NOTE, this replaces the missing structure concept and prevents from
        # replace '\n' with '' and '\\n' with '\n' see json2.js as a sample
        return data.replace('\\', '\\\\')


class CDNReplace(z3c.zrtresource.replace.Replace):
    """ASame as Replace with additional cdn include expression
    
    You can use this additional expression as:
    
    /* zrt-replace:"REPLACE_THIS" include"RESOURCE_NAME" */
    REPLACE_THIS
    """
    zope.interface.implements(z3c.zrtresource.interfaces.IZRTCommand)

    inputExpressions = {
        '': CDNInputExpression,
        'str': CDNInputExpression,
        're': z3c.zrtresource.replace.RegexInputExpression,
        }

    outputExpressions = {
        '': z3c.zrtresource.replace.StringOutputExpression,
        'str': z3c.zrtresource.replace.StringOutputExpression,
        'tal': z3c.zrtresource.replace.TALESOutputExpression,
        'include': CDNIncludeOutputExpression,
        }
