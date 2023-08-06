.. contents::

Introduction
============

ZTFY.lock is a small package which can be used to get locks on persistent objects
in several contexts.

These contexts include:

- simple 'threading' locking, in a single-process environment

- file locking (using 'zc.lockfile' package), in a multi-processes environment where
  all processes are handled on a single host

- memcached locking (using 'lovely.memcached' package), in a multi-process environment
  where processes are handled on several hosts.


Locking utility
===============

Locking is handled by a utility implementing ILockingUtility interface and registered
for that interface. Locking policy have to be chosen on that utility to define the locking
helper which will be used.

According to the selected policy, additional parameters will have to be defined to set
the file locks path or the memcached client connection.
