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
import os

# import Zope3 interfaces
from zope.container.interfaces import IContained

# import local interfaces
from ztfy.extfile.interfaces import IBaseBlobFile, IBlobFile, IBlobImage

# import Zope3 packages
from ZODB.blob import Blob
from zope.app.file.file import File
from zope.app.file.image import Image, getImageInfo
from zope.interface import implements

# import local packages


BLOCK_SIZE = 1 << 16


class BaseBlobFile(File):
    """A persistent content class handling data stored in an external blob"""

    implements(IBaseBlobFile, IContained)

    def __init__(self, data='', contentType='', source=None):
        self.__parent__ = self.__name__ = None
        self.contentType = contentType
        self._blob = None
        if data:
            self.data = data
        elif source:
            if os.path.exists(source):
                try:
                    f = open(source, 'rb')
                    self.data = f.read()
                finally:
                    f.close()

    def getBlob(self):
        if self._blob is None:
            return None
        return self._blob.open(mode='r')

    def _getData(self):
        f = self.getBlob()
        if f is None:
            return None
        try:
            data = f.read()
            return data
        finally:
            f.close()

    def _setData(self, data):
        if self._blob is None:
            self._blob = Blob()
        if isinstance(data, unicode):
            data = data.encode('UTF-8')
        f = self._blob.open('w')
        try:
            if hasattr(data, 'read'):
                self._size = 0
                _data = data.read(BLOCK_SIZE)
                size = len(_data)
                while size > 0:
                    f.write(_data)
                    self._size += size
                    _data = data.read(BLOCK_SIZE)
                    size = len(_data)
            else:
                f.write(data)
                self._size = len(data)
        finally:
            f.close()

    data = property(_getData, _setData)

    def getSize(self):
        return self._size

    def __nonzero__(self):
        return self._size > 0


class BlobFile(BaseBlobFile):
    """Content class for BLOB files"""

    implements(IBlobFile)


class BlobImage(BaseBlobFile, Image):
    """Content class for BLOB images"""

    implements(IBlobImage)

    def _setData(self, data):
        BaseBlobFile._setData(self, data)
        contentType, self._width, self._height = getImageInfo(data)
        if contentType:
            self.contentType = contentType

    data = property(BaseBlobFile._getData, _setData)
