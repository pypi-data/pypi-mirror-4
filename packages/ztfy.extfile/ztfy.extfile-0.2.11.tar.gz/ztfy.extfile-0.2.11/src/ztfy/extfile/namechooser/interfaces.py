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
from zope.configuration.fields import Path, GlobalObject
from zope.interface import Interface
from zope.schema import TextLine

# import local packages

from ztfy.extfile import _


class IExtFileNameChooserConfig(Interface):
    """Informations required to define a name chooser"""

    name = TextLine(title=_("Configuration name"),
                    description=_("Name of the ExtFile name chooser configuration"),
                    default=u'',
                    required=False)

    temp_path = Path(title=_("Temporary path name"),
                     description=_("Absolute path of temporary files"),
                     default=u'/var/tmp',
                     required=True)

    base_path = Path(title=_("Base path name"),
                     description=_("Absolute base path of final files"),
                     default=u'/var/local/zope/files',
                     required=True)

    chooser = GlobalObject(title=_("Filename chooser class"),
                           description=_("Name of an external files names chooser, implementing IExtFileNameChooser"),
                           required=True)


class IExtFileNameChooser(Interface):
    """An interface called to define the final name of an external file"""

    def getName(parent, extfile, name):
        """Generate a new relative file path
        
        This file is relative to NameChooser base_path parameter, but can start with 'os.path.sep'.
        WARNING : when using several name choosers, each one may generate "statistically" unique names,
        otherwise conflicts and errors may occur
        """
