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
from zope.configuration.fields import Path
from zope.interface import Interface
from zope.schema import TextLine, Int, Password

# import local packages

from ztfy.extfile import _


class SFTPExtFileHandlerConfigException(Exception):
    """An exception used to handler ExtFile handler config exceptions"""


class ISFTPExtFileHandlerConfig(Interface):

    name = TextLine(title=_("Handler config name"),
                    description=_("Name with which the utility is registered"),
                    required=False,
                    default=u'')

    hostname = TextLine(title=_("Host name"),
                        description=_("SFTP server name"),
                        required=True,
                        default=u'localhost')

    port = Int(title=_("Host port number"),
               description=_("SFTP server port number"),
               required=False,
               default=22)

    username = TextLine(title=_("User name"),
                        description=_("SFTP session user name"),
                        required=True)

    password = Password(title=_("User password"),
                        description=_("SFTP session user password"),
                        required=False)

    private_key = Path(title=_("Private key file"),
                       description=_("Path name to private key file"),
                       required=False,
                       default=u'~/.ssh/id_rsa')

    remote_root = Path(title=_("Remote root"),
                       description=_("Remote root of ExtFile files"),
                       required=True,
                       default=u'/')

    cache_root = Path(title=_("Cache root"),
                      description=_("Local root of cached files"),
                      required=False)
