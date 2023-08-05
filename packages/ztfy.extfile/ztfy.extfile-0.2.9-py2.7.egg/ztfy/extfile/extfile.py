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
import os, tempfile
import logging
logger = logging.getLogger('ZTFY.extfile')

# import Zope3 interfaces
from zope.container.interfaces import IContained

# import local interfaces
from hurry.query.interfaces import IQuery
from ztfy.extfile.handler.interfaces import MissingHandlerError, IExtFileHandler
from ztfy.extfile.interfaces import IBaseExtFile, IExtFile, IExtImage

# import Zope3 packages
from zope.app.file.file import File
from zope.app.file.image import Image, getImageInfo
from zope.component import getUtility, queryUtility
from zope.interface import implements
from zope.traversing.api import getParent, getName

# import local packages
from hurry.query.value import Eq
from ztfy.extfile.namechooser.config import getTempPath, getFullPath
from ztfy.utils import catalog

from ztfy.extfile import _


BLOCK_SIZE = 1 << 16


class BaseExtFile(File):
    """A persistent content class handling data stored in an external file"""

    implements(IBaseExtFile, IContained)

    _filename = None
    _deleted = False
    _handler = ''
    _size = 0L

    def __init__(self, data='', contentType='', nameChooser='', handler='', source=None, keep_source=False):
        self.__parent__ = self.__name__ = None
        self.contentType = contentType
        self._handleFile = False
        self._nameChooser = nameChooser
        self._handler = handler
        if data:
            self.data = data
        elif source:
            if os.path.exists(source):
                self._v_filename = source
                self._size = os.stat(source)[os.path.stat.ST_SIZE]
                self._handleFile = not keep_source

    def _getData(self):
        """See `IFile` interface"""
        filename = getattr(self, '_v_filename', None)
        if filename:
            f = open(filename, 'rb')
            data = f.read()
            f.close()
            return data
        filename = getattr(self, '_filename', None)
        if not filename:
            return None
        handler = queryUtility(IExtFileHandler, self._handler)
        if handler is not None:
            return handler.readFile(filename, self)
        return None

    def _setData(self, data):
        """See `IFile` interface"""
        self._saveTempFile(data)

    data = property(_getData, _setData)

    @property
    def filename(self):
        return self._filename

    def getSize(self):
        """See `IFile` interface"""
        return self._size

    def __nonzero__(self):
        return self._size > 0

    def _saveTempFile(self, data):
        """Save data to a temporary local file"""
        filename = self._getTempFilename()
        # Check if data is empty but filename exists
        if (not data) and os.path.isfile(filename):
            return
        # Set a flag to know that we handle the file...
        self._handleFile = True
        # Check if data is a unicode string (copied from zope.app.file.File class
        if isinstance(data, unicode):
            data = data.encode('UTF-8')
        # Create temporary location directories, if needed
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Write data to requested file
        f = open(filename, 'wb')
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

    def _getTempFilename(self):
        """Get temporary file name"""
        pathname = getTempPath(self._nameChooser)
        fd, filename = tempfile.mkstemp(prefix='extfile_', suffix='.tmp', dir=pathname)
        os.close(fd)
        self._v_filename = filename
        return filename

    def _getCurrentFilename(self):
        """Get current file name"""
        return getattr(self, '_filename', None) or getattr(self, '_v_filename', None)

    def moveTempFile(self):
        """Move temporary file to it's final location"""
        if hasattr(self, '_v_version'):
            delattr(self, '_v_version')
        else:
            if self.filename:
                query = getUtility(IQuery)
                files = query.searchResults(Eq(('Catalog', 'filename'), self.filename))
                if (len(files) > 0) and not hasattr(self, '_v_filename'):
                    return
            self._filename = getFullPath(getParent(self), self, getName(self), self._nameChooser)
            if hasattr(self, '_v_filename'):
                handler = queryUtility(IExtFileHandler, self._handler)
                if handler is None:
                    raise MissingHandlerError, _("You have to define an IExtFileHandler utility to use external files !")
                if self._handleFile:
                    handler.moveFile(self._v_filename, self._filename)
                else:
                    handler.copyFile(self._v_filename, self._filename)
                delattr(self, '_v_filename')
        # reindex file so that 'filename' property is indexed correctly
        catalog.indexObject(self, 'Catalog', 'filename')

    def deleteFile(self, temporary=False):
        """Mark external file for deletion"""
        if temporary:
            logger.debug(" >>> removing temporary file...")
            filename = getattr(self, '_v_filename', None)
            if filename:
                logger.debug("   > file = %s" % filename)
                self._v_deleted_filename = filename
                delattr(self, '_v_filename')
                self._deleted = True
        elif self._filename:
            logger.debug(" >>> trying to delete external file...")
            # remove this file from catalog
            catalog.unindexObject(self, 'Catalog', 'filename')
            # look for other ExtFiles with same filename
            query = getUtility(IQuery)
            files = query.searchResults(Eq(('Catalog', 'filename'), self._filename))
            # remove physical file only when not shared with another file
            if len(files) > 0:
                logger.debug("   > remaining contents linked to same file, not deleted !")
                for f in files:
                    logger.debug("   > file = %s %s %s" % (getName(getParent(f)),
                                                           getName(f),
                                                           f.filename))
                return
            logger.debug("   < deleted %s" % self._filename)
            self._deleted_filename = self._filename
            self._filename = None
            self._deleted = True

    def commitDeletedFile(self):
        """Delete pointed file if handled by context"""
        logger.debug(" >>> commitDeletedFile...")
        if not (self._handleFile and self._deleted):
            logger.debug("   < not deleted !!")
            return
        filename = getattr(self, '_deleted_filename', None)
        logger.debug("   > filename =" + str(filename))
        if filename:
            handler = queryUtility(IExtFileHandler, self._handler)
            if handler is None:
                raise MissingHandlerError, _("You have to define an IExtFileHandler utility to use external files !")
            handler.deleteFile(filename)
            delattr(self, '_deleted_filename')

    def resetFile(self, filename):
        """Reset file content to given filename"""
        self.deleteFile()
        self._filename = filename
        handler = queryUtility(IExtFileHandler, self._handler)
        if handler is not None:
            self._size = handler.getSize(self._filename)
        # reindex file so that 'filename' property is indexed correctly
        catalog.indexObject(self, 'Catalog', 'filename')


class ExtFile(BaseExtFile):

    implements(IExtFile)


class ExtImage(BaseExtFile, Image):

    implements(IExtImage)

    def _setData(self, data):
        BaseExtFile._setData(self, data)
        _contentType, self._width, self._height = getImageInfo(data)

    data = property(BaseExtFile._getData, _setData)
