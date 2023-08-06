### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.lock.interfaces import ILockingUtility, \
                                 IFileLockingInfo, IMemcachedLockingInfo
from ztfy.skin.interfaces import IDefaultView, IPropertiesMenuTarget
from ztfy.skin.layer import IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from zope.component import adapts
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.form import EditForm, DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.lock import _


class LockingUtilityDefaultViewAdapter(object):
    """Locking utility default view adapter"""

    adapts(ILockingUtility, IZTFYBackLayer, Interface)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@properties.html'

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class LockingUtilityEditForm(EditForm):
    """Locking utility edit form"""

    implements(IPropertiesMenuTarget)

    fields = field.Fields(ILockingUtility)


class LockingUtilityFileLockingInfoEditForm(DialogEditForm):
    """Dialog edit form for file locking info"""

    fields = field.Fields(IFileLockingInfo)


class LockingUtilityFileLockingInfoEditFormMenu(DialogMenuItem):
    """Dialog edit form menu item for file locking info"""

    title = _(":: File locks properties...")
    target = LockingUtilityFileLockingInfoEditForm


class LockingUtilityMemcachedLockingInfoEditForm(DialogEditForm):
    """Dialog edit form for memcached locking info"""

    fields = field.Fields(IMemcachedLockingInfo)


class LockingUtilityMemcachedLockingInfoEditFormMenu(DialogMenuItem):
    """Dialog edit form menu item for memcached locking info"""

    title = _(":: Memcached locks properties...")
    target = LockingUtilityMemcachedLockingInfoEditForm
