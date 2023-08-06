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

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import Choice, TextLine

# import local packages
from ztfy.utils.schema import StringLine

from ztfy.lock import _


class ILockingUtility(Interface):
    """Locking utility interface"""

    policy = Choice(title=_("Locking policy"),
                    description=_("Locking policy can be used to create locks in multi-processes and/or multi-hosts environments"),
                    vocabulary="ZTFY locking helpers",
                    required=False)

    def getLock(self, target, wait=False):
        """Try to get lock for given object"""

    def releaseLock(self, lock):
        """Release given lock
        
        Input value is the one returned by getLock()
        """


class ILockingHelper(Interface):
    """Base interface for locker informations"""

    marker_interface = Attribute(_("Class name of lock helper target marker interface"))

    def getLock(self, utility, target):
        """Try to get lock for given object"""

    def releaseLock(self, lock):
        """Release given lock
        
        Input value is the one returned by getLock()
        """


#
# File locking interfaces
#

class IFileLockingInfo(Interface):
    """File locking info"""

    locks_path = TextLine(title=_("Locks base path"),
                          description=_("Full path of server's directory storing locks"),
                          required=True,
                          default=u'/var/lock')


class IFileLockingHelper(ILockingHelper):
    """File locking utility"""


class IFileLockingTarget(Interface):
    """Marker interface for lockers using file locking"""


#
# Memcached locking interfaces
#

class IMemcachedLockingInfo(Interface):
    """Memcached locker info"""

    memcached_client = TextLine(title=_("Memcached client"),
                                description=_("Name of memcached client connection"),
                                required=True)

    locks_namespace = StringLine(title=_("Locks namespace"),
                                 description=_("Memcached namespace used to define locks"),
                                 required=True,
                                 default='ztfy.lock')


class IMemcachedLockingHelper(ILockingHelper):
    """Memcached locking helper utility"""


class IMemcachedLockingTarget(Interface):
    """Marker interface for lockers using memcached locking"""
