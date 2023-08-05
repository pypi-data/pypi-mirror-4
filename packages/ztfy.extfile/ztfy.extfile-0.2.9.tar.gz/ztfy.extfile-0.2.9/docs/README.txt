====================
ZTFY.extfile package
====================

.. contents::

What is ztfy.extfile ?
======================

ztfy.extfile is a package which allows storing File and Image objects data
outside of the Zope database (ZODB), into 'external' files.
Files can be stored in the local file system, or remotely via protocols like
SFTP or NFS (even HTTP is possible) ; an efficient cache system allows to
store local copies of the remote files locally.

Finally, external files can be stored via Blob objects, provided by the latest
versions of the ZODB.


How to use ztfy.extfile ?
=========================

A set of ztfy.extfile usages are given as doctests in ztfy/extfile/doctests/README.txt.
