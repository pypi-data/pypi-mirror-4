### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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
from zope.app.file.interfaces import IFile, IImage
from zope.component.interfaces import IObjectEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import TextLine

# import local packages

from ztfy.extfile import _


class IBaseExtFileInfo(Interface):
    """Base properties of external files"""

    filename = TextLine(title=_("External file name"),
                        description=_("Identify the file name on the file system"),
                        required=True)

    def hasData(self):
        """Check to know if file actually handles data"""


class IBaseExtFileWriter(Interface):
    """External file writing methods"""

    def moveTempFile(self):
        """Move temporary file to it's final location"""

    def deleteFile(self, temporary=False):
        """Remove external file data on the file system"""

    def commitDeletedFile(self):
        """Really purge external file data when transaction is committed"""

    def resetFile(self, filename):
        """Reset file data to given filename"""


class IBaseExtFile(IBaseExtFileInfo, IBaseExtFileWriter, IFile):
    """External files base interface"""


class IExtFile(IBaseExtFile):
    """External files main interface"""


class IBaseExtImage(IBaseExtFileInfo, IBaseExtFileWriter, IImage):
    """External images base interface"""


class IExtImage(IBaseExtImage):
    """External images main interface"""


class IBaseBlobFile(Interface):
    """Marker base interface for blob files"""

    def getBlob(self, mode='r'):
        """Return internal blob"""


class IBlobFile(IBaseBlobFile, IFile):
    """Marker interface for blob files"""


class IBlobImage(IBaseBlobFile, IImage):
    """Marker interface for blob images"""


# Events interfaces

class IExtFileModifiedEvent(IObjectModifiedEvent):
    """An external file is modified"""


class IExtFileAfterAddedEvent(IObjectEvent):
    """An external file was added to a container"""


class IExtFileAfterModifiedEvent(IObjectEvent):
    """An external file has been modified and moved to it's final location"""
