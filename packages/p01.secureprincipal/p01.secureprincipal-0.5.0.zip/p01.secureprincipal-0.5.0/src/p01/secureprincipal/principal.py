##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface

from p01.secureprincipal import interfaces


class AliasPrincipalBase(object):
    """Base class for IAuthenticatedPrincipal principals.

    The PrincipalAliasSecurityPolicy policy will work with any IAuthentication
    utility as long as your principal implements IAliasPrincipal.

    """

    zope.interface.implements(interfaces.IAliasPrincipal)

    # customize this attributes
    _alias = None
    _roles = []

    def __init__(self, context):
        """We offer no access to the user object itself."""
        self.id = context.__name__
        self.title = context.title
        self.description = context.description

    @property
    def alias(self):
        return self._alias

    @property
    def roles(self):
        return self._roles

    def __repr__(self):
        return "<%s %s>" %(self.__class__.__name__, self.id)
