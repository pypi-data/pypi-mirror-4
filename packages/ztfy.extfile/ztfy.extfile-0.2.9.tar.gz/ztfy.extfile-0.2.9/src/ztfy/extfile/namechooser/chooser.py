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
import pytz
from datetime import datetime
from mimetypes import guess_extension

# import Zope3 interfaces

# import local interfaces
from ztfy.extfile.namechooser.interfaces import IExtFileNameChooser

# import Zope3 packages
from zope.interface import implements

# import local packages


class TimestampNameChooser(object):
    """A timestamp based file name chooser"""

    implements(IExtFileNameChooser)

    def getName(self, parent, extfile, name):
        d = datetime.now(pytz.UTC)
        ext = guess_extension(extfile.contentType.split(';')[0])
        return d.strftime('/%Y/%m/%d-%H%M%S-%%d%%s') % (d.microsecond, ext)
