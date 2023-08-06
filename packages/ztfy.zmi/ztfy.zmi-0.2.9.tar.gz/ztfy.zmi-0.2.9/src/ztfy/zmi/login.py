### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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
from zope.authentication.interfaces import IAuthentication
from zope.security.interfaces import IUnauthorized

# import local interfaces
from ztfy.skin.interfaces import IDefaultView

# import Zope3 packages
from z3c.form import field, button
from zope.component import getUtility, queryMultiAdapter
from zope.interface import Interface
from zope.schema import TextLine, Password
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.form import AddForm

from ztfy.zmi import _


class ILoginFormFields(Interface):
    """Login form fields interface"""

    username = TextLine(title=_("login-field", "Login"),
                        description=_("Principal ID"),
                        required=True)

    password = Password(title=_("password-field", "Password"),
                        description=_("User password"),
                        required=True)


class LoginForm(AddForm):
    """ZMI login form"""

    title = _("Login form")
    legend = _("Please enter valid credentials to login")

    fields = field.Fields(ILoginFormFields)

    @button.buttonAndHandler(_("login-button", "Login"))
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.request.form['login'] = data['username']
        self.request.form['password'] = data['password']
        auth = getUtility(IAuthentication)
        principal = auth.authenticate(self.request)
        if principal is not None:
            if IUnauthorized.providedBy(self.context):
                context, _layer, _permission = self.context.args
                self.request.response.redirect(absoluteURL(context, self.request))
            else:
                target = queryMultiAdapter((self.context, self.request, Interface), IDefaultView)
                if target is not None:
                    self.request.response.redirect('%s/%s' % (absoluteURL(self.context, self.request), target.viewname))
                else:
                    self.request.response.redirect('%s/@@SelectedManagementView.html' % absoluteURL(self.context, self.request))
                return ''
        else:
            auth.unauthorized(None, self.request)
