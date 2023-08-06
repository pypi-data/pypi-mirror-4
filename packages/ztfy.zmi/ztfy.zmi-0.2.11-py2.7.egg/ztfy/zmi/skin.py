### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.skin.interfaces import IDefaultView
from ztfy.zmi.layer import IZMILayer

# import Zope3 packages
from zope.app.publisher.browser.managementviewselector import ManagementViewSelector
from zope.browsermenu.menu import getFirstMenuItem
from zope.component import adapts
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages


class DefaultViewAdapter(object):

    adapts(Interface, IZMILayer, Interface)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@SelectedManagementView.html'

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class ZMIManagementViewSelector(ManagementViewSelector):
    """Custom ZMI management view selector"""

    def __call__(self):
        redirect_url = absoluteURL(self.context, self.request)
        item = getFirstMenuItem('zmi_views', self.context, self.request)
        if item:
            action = item['action']
            if not (action.startswith('../') or \
                    action.lower().startswith('javascript:') or \
                    action.lower().startswith('++')):
                redirect_url = '%s/%s' % (redirect_url, action)
        self.request.response.redirect(redirect_url) # Redirect to content/
        return u''
