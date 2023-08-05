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
from ztfy.extfile.handler.interfaces import IExtFileHandler
from ztfy.extfile.handler.sftp.interfaces import ISFTPExtFileHandlerConfig, SFTPExtFileHandlerConfigException

# import Zope3 packages
from zope.component import queryUtility
from zope.component.zcml import utility

# import local packages
from ztfy.extfile.handler.sftp import SFTPExtFileHandler

from ztfy.extfile import _


def configureSFTPExtFileHandler(hostname, username, remote_root,
                                port=22, password=None, private_key=None, cache_root=None, name=''):
    config = queryUtility(ISFTPExtFileHandlerConfig, name)
    if config is not None:
        config.hostname = hostname
        config.port = port
        config.username = username
        config.password = password
        config.private_key = private_key
        config.remote_root = remote_root
        config.cache_root = cache_root


def config(context, hostname, username, remote_root,
           port=22, password=None, private_key=None, cache_root=None, name=''):
    if not (private_key or password):
        raise SFTPExtFileHandlerConfigException, _("You have to define private_key file or password !")
    handler = SFTPExtFileHandler()
    utility(context, IExtFileHandler, component=handler, name=name)
    utility(context, ISFTPExtFileHandlerConfig, component=handler, name=name)
    context.action(discriminator=('ztfy.extfile.handler.sftp', name),
                   callable=configureSFTPExtFileHandler,
                   args=(hostname, username, remote_root, port, password, private_key, cache_root, name))
