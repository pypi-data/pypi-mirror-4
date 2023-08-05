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
from ztfy.extfile.namechooser.interfaces import IExtFileNameChooserConfig

# import Zope3 packages
from zope.component import queryUtility
from zope.component.zcml import utility

# import local packages
from config import ExtFileConfig


def configureExtFileNameChooser(temp_path, base_path, chooser, name=''):
    config = queryUtility(IExtFileNameChooserConfig, name)
    if config is not None:
        config.path = temp_path
        config.base_path = base_path
        config.chooser = chooser()


def config(context, temp_path, base_path, chooser, name=''):
    utility(context, IExtFileNameChooserConfig, factory=ExtFileConfig, name=name)
    context.action(discriminator=('onf.component.extfile', 'config', name),
                   callable=configureExtFileNameChooser,
                   args=(temp_path, base_path, chooser, name))
