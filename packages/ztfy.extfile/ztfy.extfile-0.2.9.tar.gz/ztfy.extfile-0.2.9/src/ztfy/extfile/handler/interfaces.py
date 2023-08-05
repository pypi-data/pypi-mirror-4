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

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface

# import local packages


class MissingFilenameError(Exception):
    """Exception class raised when an external file doesn't have any 'filename' property"""


class MissingFileError(Exception):
    """Exception class raised when an external file target doesn't exist"""


class MissingHandlerError(Exception):
    """Exception class raised when no IExtFileHandler utility is registered"""


class IExtFileHandlerReader(Interface):
    """Interface of utilities used to get access to external files"""

    def exists(path):
        """Check to know if a given external file exists"""

    def getSize(path):
        """Get file size, in bytes"""

    def getFile(path, parent=None):
        """Get a read-only file handle of the given file"""

    def readFile(path, parent=None):
        """Get content of the given of the given file"""


class IExtFileHandlerWriter(Interface):
    """Interface of utilities used to write external files"""

    def moveFile(source, dest):
        """Move data stored in a local temporary file to it's final destination"""

    def copyFile(source, dest):
        """Copy data stored in a local temporary file to it's final destination"""

    def deleteFile(path):
        """Remove selected file"""


class IExtFileHandler(IExtFileHandlerReader, IExtFileHandlerWriter):
    """Marker interface used to identify external files handlers"""
