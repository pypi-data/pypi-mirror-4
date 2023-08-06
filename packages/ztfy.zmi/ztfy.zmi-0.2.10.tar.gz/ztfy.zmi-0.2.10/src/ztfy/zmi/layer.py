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
from zope.app.basicskin import IDefaultBrowserLayer

# import local interfaces
from ztfy.skin.layer import IZTFYBackLayer
from ztfy.skin.skin import IZTFYBackSkin

# import Zope3 packages

# import local packages


class IZMILayer(IZTFYBackLayer, IDefaultBrowserLayer):
    """ZMI layer interface"""


class IZMISkin(IZTFYBackSkin, IZMILayer):
    """ZMI skin interface"""
