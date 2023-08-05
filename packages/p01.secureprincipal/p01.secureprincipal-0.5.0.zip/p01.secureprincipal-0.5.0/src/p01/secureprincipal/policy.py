##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

import zope.interface

from zope.security.checker import CheckerPublic
from zope.security.management import system_user
from zope.security.simplepolicies import ParanoidSecurityPolicy
from zope.security.interfaces import ISecurityPolicy
from zope.security.proxy import removeSecurityProxy

from zope.securitypolicy.interfaces import Allow
from zope.securitypolicy.interfaces import Deny
from zope.securitypolicy.interfaces import Unset
from zope.securitypolicy.interfaces import IRolePermissionMap
from zope.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.principalpermission import principalPermissionManager
from zope.securitypolicy.rolepermission import rolePermissionManager
from zope.securitypolicy.principalrole import principalRoleManager

from p01.secureprincipal import interfaces


globalPrincipalPermissionSetting = principalPermissionManager.getSetting
globalRolesForPermission = rolePermissionManager.getRolesForPermission
globalRolesForPrincipal = principalRoleManager.getRolesForPrincipal

# enhance SettingAsBoolean with True:True, False:False allows us to use
# True, False and None as markers in key/value storage items. See m01.mongo
# for more information
SettingAsBoolean = {Allow: True, Deny: False, Unset: None, None: None,
                    True: True, False: False}

class CacheEntry:
    pass

class PrincipalAliasSecurityPolicy(ParanoidSecurityPolicy):
    """Security policy without groups but with alias roles."""

    zope.interface.classProvides(ISecurityPolicy)

    anonymousRole = 'zope.Anonymous'  # Everybody has Anonymous

    def __init__(self, *args, **kw):
        ParanoidSecurityPolicy.__init__(self, *args, **kw)
        self._cache = {}

    def invalidate_cache(self):
        self._cache = {}

    def cache(self, parent):
        cache = self._cache.get(id(parent))
        if cache:
            cache = cache[0]
        else:
            cache = CacheEntry()
            self._cache[id(parent)] = cache, parent
        return cache

    def cached_decision(self, parent, principal, permission):
        # Return the decision for a principal and permission

        aid = None
        aliasRoles = []
        if interfaces.IAliasPrincipal.providedBy(principal):
            aliasRoles = principal.roles
            aid = principal.alias

        pid = principal.id

        cache = self.cache(parent)
        try:
            cache_decision = cache.decision
        except AttributeError:
            cache_decision = cache.decision = {}

        cache_decision_prin = cache_decision.get(pid)
        if not cache_decision_prin:
            cache_decision_prin = cache_decision[pid] = {}

        try:
            return cache_decision_prin[permission]
        except KeyError:
            pass

        # cache_decision_prin[permission] is the cached decision for a
        # principal and permission.

        # 1. check principal.id - permission settings
        decision = self.cached_prinper(parent, pid, permission)
        if decision is not None:
            cache_decision_prin[permission] = decision
            return decision

        # 2. check principal.alias - permission settings
        if aid is not None:
            decision = self.cached_prinper(parent, aid, permission)
            if decision is not None:
                cache_decision_prin[permission] = decision
                return decision

        # 3. get all roles
        roles = self.cached_roles(parent, permission)
        if roles:
            # 4. check built in principal roles based - permission settings
            if aliasRoles:
                # but only if we have an IAliasPrincipal
                for role, setting in roles.items():
                    if setting and (role in aliasRoles):
                        cache_decision_prin[permission] = decision = True
                        return decision
            # 5. check principal.id based role - permission settings
            prin_roles = self.cached_principal_roles(parent, pid)
            for role, setting in prin_roles.items():
                if setting and (role in roles):
                    cache_decision_prin[permission] = decision = True
                    return decision
            # 6. check principal.alias based role - permission settings
            if aid is not None:
                # but only if we have an IAliasPrincipal
                prin_roles = self.cached_principal_roles(parent, aid)
                for role, setting in prin_roles.items():
                    if setting and (role in roles):
                        cache_decision_prin[permission] = decision = True
                        return decision

        cache_decision_prin[permission] = decision = False
        return decision

    def cached_prinper(self, parent, pid, permission):
        # Compute the permission, if any, for the principal.
        cache = self.cache(parent)
        try:
            cache_prin = cache.prin
        except AttributeError:
            cache_prin = cache.prin = {}

        cache_prin_per = cache_prin.get(pid)
        if not cache_prin_per:
            cache_prin_per = cache_prin[pid] = {}

        try:
            return cache_prin_per[permission]
        except KeyError:
            pass

        if parent is None:
            prinper = SettingAsBoolean[
                globalPrincipalPermissionSetting(permission, pid, None)
                ]
            cache_prin_per[permission] = prinper
            return prinper

        ppm = IPrincipalPermissionMap(parent, None)
        if ppm is not None:
            prinper = SettingAsBoolean[
                ppm.getSetting(permission, pid, None)
                ]
            if prinper is not None:
                cache_prin_per[permission] = prinper
                return prinper

        parent = removeSecurityProxy(getattr(parent, '__parent__', None))
        prinper = self.cached_prinper(parent, pid, permission)
        cache_prin_per[permission] = prinper
        return prinper

    def cached_roles(self, parent, permission):
        cache = self.cache(parent)
        try:
            cache_roles = cache.roles
        except AttributeError:
            cache_roles = cache.roles = {}
        try:
            return cache_roles[permission]
        except KeyError:
            pass

        if parent is None:
            roles = dict(
                [(role, 1)
                 for (role, setting) in globalRolesForPermission(permission)
                 if SettingAsBoolean[setting]
                 ]
               )
            cache_roles[permission] = roles
            return roles

        roles = self.cached_roles(
            removeSecurityProxy(getattr(parent, '__parent__', None)),
            permission)
        rpm = IRolePermissionMap(parent, None)
        if rpm:
            roles = roles.copy()
            for role, setting in rpm.getRolesForPermission(permission):
                setting = SettingAsBoolean[setting]
                if setting:
                    roles[role] = 1
                elif role in roles:
                    del roles[role]

        cache_roles[permission] = roles
        return roles

    def cached_principal_roles(self, parent, principal):
        cache = self.cache(parent)
        try:
            cache_principal_roles = cache.principal_roles
        except AttributeError:
            cache_principal_roles = cache.principal_roles = {}
        try:
            return cache_principal_roles[principal]
        except KeyError:
            pass

        if parent is None:
            roles = dict(
                [(role, SettingAsBoolean[setting])
                 for (role, setting) in globalRolesForPrincipal(principal)
                 ]
                 )
            roles[self.anonymousRole] = True # Everybody has Anonymous
            cache_principal_roles[principal] = roles
            return roles

        roles = self.cached_principal_roles(
            removeSecurityProxy(getattr(parent, '__parent__', None)),
            principal)

        prinrole = IPrincipalRoleMap(parent, None)
        if prinrole:
            roles = roles.copy()
            for role, setting in prinrole.getRolesForPrincipal(principal):
                roles[role] = SettingAsBoolean[setting]

        cache_principal_roles[principal] = roles
        return roles

    def checkPermission(self, permission, object):
        if permission is CheckerPublic:
            return True

        object = removeSecurityProxy(object)
        seen = {}
        for participation in self.participations:
            principal = participation.principal
            if principal is system_user:
                return True

            if principal.id in seen:
                continue

            if self.cached_decision(object, principal, permission) is True:
                # first (True) Allow will win, even if a following participation
                # will return (False) Deny which we do not check, just return
                # True.
                return True

            seen[principal.id] = 1

        return False
