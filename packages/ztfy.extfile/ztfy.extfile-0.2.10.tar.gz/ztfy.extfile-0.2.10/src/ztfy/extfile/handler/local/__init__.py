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
import os, shutil

# import Zope3 interfaces

# import local interfaces
from ztfy.extfile.handler.interfaces import IExtFileHandler

# import Zope3 packages
from zope.interface import implements

# import local packages


class LocalExtFileHandler(object):

    implements(IExtFileHandler)

    def _getPath(self, path):
        if path.startswith(os.path.sep):
            path = path[1:]
        return os.path.join(self.local_root, path)

    def exists(self, path):
        path = self._getPath(path)
        return os.path.exists(path)

    def getSize(self, path):
        path = self._getPath(path)
        if os.path.isfile(path):
            return os.stat(path)[os.path.stat.ST_SIZE]
        return None

    def getFile(self, path, parent=None):
        path = self._getPath(path)
        if not os.path.isfile(path):
            return None
        return open(path, 'rb')

    def readFile(self, path, parent=None):
        f = self.getFile(path, parent)
        if f is None:
            return ''
        try:
            return f.read()
        finally:
            f.close()

    def moveFile(self, source, dest):
        dest = self._getPath(dest)
        directory = os.path.dirname(dest)
        if not os.path.exists(directory):
            os.makedirs(directory)
        shutil.move(source, dest)

    def copyFile(self, source, dest):
        dest = self._getPath(dest)
        directory = os.path.dirname(dest)
        if not os.path.exists(directory):
            os.makedirs(directory)
        shutil.copy(source, dest)

    def deleteFile(self, path):
        path = self._getPath(path)
        if not os.path.exists(path):
            return
        os.unlink(path)
