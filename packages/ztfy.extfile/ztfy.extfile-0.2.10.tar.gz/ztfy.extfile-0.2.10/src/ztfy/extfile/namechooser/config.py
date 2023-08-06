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

# import local interfaces
from ztfy.extfile.namechooser.interfaces import IExtFileNameChooserConfig

# import Zope3 packages
from zope.component import queryUtility, getAllUtilitiesRegisteredFor
from zope.interface import implements

# import local packages


DEFAULT_TEMP_DIR = '/var/tmp'
DEFAULT_BASE_DIR = '/var/local/zope/extfiles'


class ExtFileConfig(object):
    """Global utility used to configure chooser of external file's name"""

    implements(IExtFileNameChooserConfig)

    name = u''
    chooser = None
    _temp_path = DEFAULT_TEMP_DIR
    _base_path = DEFAULT_BASE_DIR

    def _getTempPath(self):
        return self._temp_path

    def _setTempPath(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self._temp_path = path

    temp_path = property(_getTempPath, _setTempPath)

    def _getBasePath(self):
        return self._base_path

    def _setBasePath(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self._base_path = path

    base_path = property(_getBasePath, _setBasePath)


def getConfigs():
    """Get list of available name choosers"""
    return getAllUtilitiesRegisteredFor(IExtFileNameChooserConfig)


def getConfig(name=''):
    """Get configuration for a given name chooser"""
    config = queryUtility(IExtFileNameChooserConfig, name)
    if (config is None) and name:
        config = queryUtility(IExtFileNameChooserConfig)
    return config


def getTempPath(config_name=''):
    """Get temp path for given name chooser"""
    config = getConfig(config_name)
    if config is not None:
        return config.temp_path
    return DEFAULT_TEMP_DIR


def getBasePath(config_name=''):
    """Get base path for given name chooser"""
    config = getConfig(config_name)
    if config is not None:
        return config.base_path
    return DEFAULT_BASE_DIR


def getFullPath(parent, extfile, name, config_name=''):
    """Get full path for specified extfile"""
    config = getConfig(config_name)
    if config is not None:
        base_path = config.base_path
        file_path = config.chooser.getName(parent, extfile, name)
        if file_path.startswith(os.path.sep):
            file_path = file_path[1:]
        return os.path.join(base_path, file_path)
    return None
