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
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces
from ztfy.lock.interfaces import ILockingUtility, ILockingHelper

# import Zope3 packages
from zope.component import queryUtility, getUtility
from zope.container.contained import Contained
from zope.interface import implements, alsoProvides, noLongerProvides
from zope.schema.fieldproperty import FieldProperty
from ztfy.lock.helper import ThreadLockingHelper

# import local packages


class LockingUtility(Persistent, Contained):
    """Locker utility class"""

    implements(ILockingUtility)

    _policy = FieldProperty(ILockingUtility['policy'])

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        if value != self._policy:
            if self._policy is not None:
                locker = queryUtility(ILockingHelper, self._policy)
                if (locker is not None) and \
                   (locker.marker_interface is not None) and \
                   locker.marker_interface.providedBy(self):
                    noLongerProvides(self, locker.marker_interface)
            self._policy = value
            if value:
                locker = getUtility(ILockingHelper, value)
                if locker.marker_interface is not None:
                    alsoProvides(self, locker.marker_interface)

    def _getLocker(self):
        if not self._policy:
            return ThreadLockingHelper
        else:
            return getUtility(ILockingHelper, self._policy)

    def getLock(self, target, wait=False):
        helper = self._getLocker()
        if helper is not None:
            lock = helper.getLock(target)
            while (lock is None) and wait:
                lock = helper.getLock(self, target)
            if lock is not None:
                return (helper, lock)
        return None

    def releaseLock(self, lock):
        if lock is None:
            return
        helper, lock = lock
        helper.releaseLock(lock)
