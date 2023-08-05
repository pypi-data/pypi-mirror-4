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
"""Tests the zope policy.

$Id: test_zopepolicy.py 98094 2009-03-14 15:50:25Z nadako $
"""

import unittest
from zope.component import provideAdapter
from zope.component.testing import setUp as componentSetUp
from zope.component.testing import tearDown as componentTearDown
from zope.testing.doctest import DocFileSuite
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.security.management import endInteraction

from zope.securitypolicy.interfaces import IGrantInfo
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.principalpermission import \
     AnnotationPrincipalPermissionManager
from zope.securitypolicy.principalrole import \
     AnnotationPrincipalRoleManager
from zope.securitypolicy.rolepermission import \
     AnnotationRolePermissionManager
from zope.securitypolicy.grantinfo import \
     AnnotationGrantInfo


def setUp(test):
    componentSetUp()
    endInteraction()
    provideAdapter(AttributeAnnotations)
    provideAdapter(AnnotationPrincipalPermissionManager, (IAnnotatable,),
                   IPrincipalPermissionManager)
    provideAdapter(AnnotationPrincipalRoleManager, (IAnnotatable,),
                   IPrincipalRoleManager)
    provideAdapter(AnnotationRolePermissionManager, (IAnnotatable,),
                   IRolePermissionManager)
    provideAdapter(AnnotationGrantInfo, (IAnnotatable,), IGrantInfo)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
            package='p01.secureprincipal',
            setUp=setUp, tearDown=componentTearDown),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
