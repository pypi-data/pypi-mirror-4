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
import os
from persistent import Persistent
from threading import Lock

# import Zope3 interfaces
from lovely.memcached.interfaces import IMemcachedClient
from zope.annotation.interfaces import IAnnotations
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.lock.interfaces import ILockingHelper, \
                                 IFileLockingInfo, IFileLockingHelper, IFileLockingTarget, \
                                 IMemcachedLockingInfo, IMemcachedLockingHelper, IMemcachedLockingTarget

# import Zope3 packages
from zc.lockfile import LockFile, LockError
from zope.component import adapter, queryUtility
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.interface import implementer, implements, classProvides
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.utils.catalog import getIntIdUtility

from ztfy.lock import _


#
# Inner process locking
#

_ThreadLocks = {}

class ThreadLockingHelper(object):
    """Thread locking helper"""

    implements(ILockingHelper)

    marker_interface = None

    def getLock(self, utility, target):
        intids = getIntIdUtility()
        oid = intids.register(target)
        if oid in _ThreadLocks:
            return None
        lock = _ThreadLocks[oid] = Lock()
        lock.acquire(blocking=False)
        return (oid, lock)

    def releaseLock(self, lock):
        assert isinstance(lock, tuple)
        oid, lock = lock
        assert isinstance(lock, Lock)
        if oid in _ThreadLocks:
            lock.release()
            del _ThreadLocks[oid]

ThreadLockingHelper = ThreadLockingHelper()


#
# File locking classes
#

FILE_LOCKING_INFO_KEY = 'ztfy.lock.lockfile'

class FileLockingInfo(Persistent):
    """File locking infos"""

    implements(IFileLockingInfo)

    locks_path = FieldProperty(IFileLockingInfo['locks_path'])


@adapter(IFileLockingTarget)
@implementer(IFileLockingInfo)
def FileLockingInfoFactory(context):
    """File locker info factory"""
    annotations = IAnnotations(context)
    helper = annotations.get(FILE_LOCKING_INFO_KEY)
    if helper is None:
        helper = annotations[FILE_LOCKING_INFO_KEY] = FileLockingInfo()
    return helper


class FileLockingHelper(object):
    """File locking helper"""

    implements(IFileLockingHelper)

    marker_interface = IFileLockingTarget

    def getLock(self, utility, target):
        info = IFileLockingInfo(utility, None)
        if (info is None) or (not info.locks_path):
            raise Exception(_("Locking utility is not configured to use file locking !"))
        intids = getIntIdUtility()
        lock_path = os.path.join(info.locks_path, 'uid-%d.lock' % intids.register(target))
        try:
            return LockFile(lock_path)
        except LockError:
            return None

    def releaseLock(self, lock):
        assert isinstance(lock, LockFile)
        lock.close()
        if os.path.exists(lock._path):
            os.unlink(lock._path)

FileLockingHelper = FileLockingHelper()


#
# Memcached locking classes
#

MEMCACHED_LOCKING_INFO_KEY = 'ztfy.lock.memcached'

class MemcachedLockingInfo(Persistent):
    """Memcached locking infos"""

    implements(IMemcachedLockingInfo)

    memcached_client = FieldProperty(IMemcachedLockingInfo['memcached_client'])
    locks_namespace = FieldProperty(IMemcachedLockingInfo['locks_namespace'])


@adapter(IMemcachedLockingTarget)
@implementer(IMemcachedLockingInfo)
def MemcachedLockingInfoFactory(context):
    """Memcached locking info factory"""
    annotations = IAnnotations(context)
    helper = annotations.get(MEMCACHED_LOCKING_INFO_KEY)
    if helper is None:
        helper = annotations[MEMCACHED_LOCKING_INFO_KEY] = MemcachedLockingInfo()
    return helper


class MemcachedLockingHelper(object):
    """Memcached locking helper"""

    implements(IMemcachedLockingHelper)

    marker_interface = IMemcachedLockingTarget

    def getLock(self, utility, target):
        info = IMemcachedLockingInfo(utility, None)
        if (info is None) or (not info.memcached_client):
            raise Exception(_("Locking utility is not configured to use memcached locking !"))
        memcached = queryUtility(IMemcachedClient, info.memcached_client)
        if memcached is None:
            raise Exception(_("Memcached client '%s' can't be found !") % info.memcached_client)
        intids = getIntIdUtility()
        key = 'uid-%d.lock' % intids.register(target)
        result = memcached.client.add(key, 'LOCKED')
        if not result:
            return None
        else:
            return (memcached, key)

    def releaseLock(self, lock):
        assert isinstance(lock, tuple)
        memcached, key = lock
        memcached.client.delete(key)

MemcachedLockingHelper = MemcachedLockingHelper()


#
# Locking helpers vocabulary
#

class LockingHelpersVocabulary(UtilityVocabulary):
    """Locking helpers vocabulary"""

    classProvides(IVocabularyFactory)

    interface = ILockingHelper
    nameOnly = True
