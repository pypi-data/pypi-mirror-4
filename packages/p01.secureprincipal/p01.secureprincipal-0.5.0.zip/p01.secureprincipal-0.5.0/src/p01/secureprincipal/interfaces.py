##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

import zope.schema
import zope.i18nmessageid
from zope.security.interfaces import IPrincipal

_ = zope.i18nmessageid.MessageFactory('p01')


class IAliasPrincipal(IPrincipal):
    """Alias and roles beased principal.
    
    An alias id can be used for set local permission. Such an alias id is
    shared by all principal of the same type. Wihtout such an alias, we have
    to set the permission for every principal based on their principal id.

    """

    alias = zope.schema.TextLine(
        title=_("Alias ID"),
        description=_("The unique alias identification of the principal."),
        required=True,
        readonly=False)

    roles = zope.schema.List(
        title=_("Roles"),
        description=_("The built-in principal roles."),
        value_type = zope.schema.TextLine(
            title=_("Role"),
            description=_("The built-in principal role."),
            required=True),
        default=[])