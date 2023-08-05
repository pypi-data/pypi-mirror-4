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
from ztfy.extfile.handler.interfaces import IExtFileHandler
from ztfy.extfile.handler.local.interfaces import ILocalExtFileHandlerConfig

# import Zope3 packages
from zope.component import queryUtility
from zope.component.zcml import utility

# import local packages
from ztfy.extfile.handler.local import LocalExtFileHandler


def configureLocalExtFileHandler(local_root='', name=''):
    config = queryUtility(ILocalExtFileHandlerConfig, name)
    if config is not None:
        config.local_root = local_root


def config(context, local_root='', name=''):
    handler = LocalExtFileHandler()
    utility(context, IExtFileHandler, component=handler, name=name)
    utility(context, ILocalExtFileHandlerConfig, component=handler, name=name)
    context.action(discriminator=('ztfy.extfile.handler.local', name),
                   callable=configureLocalExtFileHandler,
                   args=(local_root, name))
