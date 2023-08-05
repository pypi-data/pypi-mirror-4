##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 203 2007-03-04 01:03:24Z roger.ineichen $
"""

__docformat__ = 'restructuredtext'

import zope.component


def getIconTag(item, request, name='icon'):
    tag = ''
    icon = zope.component.queryMultiAdapter((item, request), name=name)
    if icon:
        try:
            tag = icon()
        except:
            return tag
    return tag



def getIconURL(item, request, name='icon'):
    url = ''
    icon = zope.component.queryMultiAdapter((item, request), name=name)
    if icon:
        try:
            url = icon.url()
        except:
            return url
    return url
