### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
import logging
logger = logging.getLogger("ZTFY.extfile")

import paramiko
import os
import time
import traceback
from hashlib import md5

# import Zope3 interfaces

# import local interfaces
from ztfy.extfile.handler.interfaces import IExtFileHandler
from zope.dublincore.interfaces import IZopeDublinCore

# import Zope3 packages
from zope.interface import implements

# import local packages

from ztfy.extfile import _


class SFTPExtFileHandler(object):

    implements(IExtFileHandler)

    hostname = 'localhost'
    port = 22
    username = ''
    password = None
    private_key = '~/.ssh/id_rsa'
    _remote_root = '/'
    _cache_root = None

    # External properties
    def _getRemoteRoot(self):
        return self._remote_root

    def _setRemoteRoot(self, path):
        if not path.endswith(os.path.sep):
            path += os.path.sep
        self._remote_root = path

    remote_root = property(_getRemoteRoot, _setRemoteRoot)

    def _getCacheRoot(self):
        return self._cache_root

    def _setCacheRoot(self, path):
        if not path.endswith(os.path.sep):
            path += os.path.sep
        self._cache_root = path

    cache_root = property(_getCacheRoot, _setCacheRoot)

    # Internal methods
    def _connect(self):
        transport = paramiko.Transport((self.hostname, self.port))
        transport.start_client()
        if self.private_key:
            key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.private_key))
            transport.auth_publickey(self.username, key)
        else:
            transport.auth_password(self.username, self.password)
        return transport

    def _getClient(self):
        try:
            transport = self._connect()
            return transport, transport.open_sftp_client()
        except:
            transport = self._connect()
            return transport, transport.open_sftp_client()

    def _getCachePath(self, path):
        if not self.cache_root:
            return None
        sign = md5(path)
        digest = sign.hexdigest()
        path = os.path.join(self.cache_root, digest[:2], digest[2:4])
        if not os.path.exists(path):
            os.makedirs(path, 0755)
        return os.path.join(path, digest[4:])

    def _getRemotePath(self, path):
        if path.startswith(os.path.sep):
            path = path[1:]
        return os.path.join(self.remote_root, path)

    # IExtFileHandler methods
    def exists(self, path):
        transport, client = self._getClient()
        try:
            remote_path = self._getRemotePath(path)
            try:
                _attrs = client.stat(remote_path)
                return True
            except:
                return False
        finally:
            client.close()
            transport.stop_thread()

    def getSize(self, path):
        transport, client = self._getClient()
        try:
            remote_path = self._getRemotePath(path)
            try:
                attrs = client.stat(remote_path)
                return attrs.st_size
            except:
                return 0
        finally:
            client.close()
            transport.stop_thread()

    def getFile(self, path, parent=None):
        client = None
        try:
            cache_path = self._getCachePath(path)
            remote_path = self._getRemotePath(path)
            try:
                if cache_path:
                    copy_to_cache = True
                    if os.path.exists(cache_path):
                        cache_stats = os.stat(cache_path)
                        if parent is not None:
                            modified = long(time.mktime(IZopeDublinCore(parent).modified.timetuple()))
                            copy_to_cache = cache_stats[os.path.stat.ST_MTIME] < modified
                        else:
                            transport, client = self._getClient()
                            remote_stats = client.stat(remote_path)
                            copy_to_cache = cache_stats[os.path.stat.ST_MTIME] < remote_stats.st_mtime
                    if copy_to_cache:
                        try:
                            if client is None:
                                transport, client = self._getClient()
                            client.get(remote_path, cache_path)
                        except:
                            logger.warning(" >>> Can't read remote file (%s)" % remote_path)
                            if not os.path.exists(cache_path):
                                raise
                            logger.warning("   > Using previously cached file...")
                    f = open(cache_path, 'rb')
                else:
                    transport, client = self._getClient()
                    f = client.open(remote_path, 'rb')
                return f
            except:
                traceback.print_exc()
                return ''
        finally:
            if client is not None:
                client.close()
                transport.stop_thread()

    def readFile(self, path, parent=None):
        f = self.getFile(path, parent)
        if f is None:
            return ''
        try:
            return f.read()
        finally:
            f.close()

    def moveFile(self, source, dest):
        transport, client = self._getClient()
        try:
            remote_path = self._getRemotePath(dest)
            directories = remote_path.split(os.path.sep)
            current = ''
            for directory in directories[1:-1]:
                current += os.path.sep + directory
                try:
                    _stat = client.stat(current)
                except:
                    client.mkdir(current)
            client.put(source, remote_path)
            cache_path = self._getCachePath(dest)
            if cache_path:
                os.rename(source, cache_path)
            else:
                os.unlink(source)
        finally:
            client.close()
            transport.stop_thread()

    def copyFile(self, source, dest):
        transport, client = self._getClient()
        try:
            remote_path = self._getRemotePath(dest)
            directories = remote_path.split(os.path.sep)
            current = ''
            for directory in directories[1:-1]:
                current += os.path.sep + directory
                try:
                    _stat = client.stat(current)
                except:
                    client.mkdir(current)
            client.put(source, remote_path)
        finally:
            client.close()
            transport.stop_thread()

    def deleteFile(self, path):
        transport, client = self._getClient()
        try:
            remote_path = self._getRemotePath(path)
            try:
                client.unlink(remote_path)
            except:
                pass
            cache_path = self._getCachePath(path)
            if cache_path and os.path.exists(cache_path):
                os.unlink(cache_path)
        finally:
            client.close()
            transport.stop_thread()
