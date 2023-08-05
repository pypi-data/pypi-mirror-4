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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.configuration.fields import Path
from zope.interface import Interface
from zope.schema import TextLine

# import local packages

from ztfy.extfile import _


class LocalExtFileHandlerException(Exception):
    """Exception used when handling local ExtFile files"""


class ILocalExtFileHandlerConfig(Interface):

    name = TextLine(title=_("Handler config name"),
                    description=_("Name with which the utility is registered"),
                    required=False,
                    default=u'')

    local_root = Path(title=_("Local root"),
                      description=_("Local root of ExtFile files, added to namechooser base path"),
                      required=False,
                      default=u'')
