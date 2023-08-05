===============================
Principal Alias Security Policy
===============================

This package implements a role-based security policy. The security policy is
responsible for deciding whether an interaction has a permission on an object.

This implementation dos not support groups or group aware principal. It offers
support for declare roles and an alias id in the principal class. This means
we have a kind of principal type. Each principal type which is different then 
another needs an own principal implementation.

The reason why we implemented this concept was to build a faster security 
declaration lookup for a given principal. The new alias and roles aware
securitypolicy doesn't lookup the IAuthentication utility for groups. Every
security declaration could be expressed by the given principal if we check the
permission for a given object. Only the object and it's parent chain is
involved in the securitypolicy. This is (probably) a small improvment but
since this get calculated on every request it's still a win. At least it offers
grouping principals of a same type and work with local roles and permissions
for such a set of grouped principals without the need for a local group
setup in your site.


This security policy does this using grant and denial information. Managers
can grant or deny:

  - roles to principals,

  - permissions to principals, and

  - permissions to roles

Grants and denials are stored as annotations on objects.  To store
grants and denials, objects must be annotatable:

  >>> import zope.interface
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> class Ob:
  ...     zope.interface.implements(IAttributeAnnotatable)

  >>> ob = Ob()

We use objects to represent principals.  These objects implement an
interface named ``IPrincipal``, but the security policy only uses the ``id``
and ``alias`` and ``roleNames`` attributes. The alias defines an alias principal
id which get handled as the same as a principal id does. But the alias id is
shared across all principal instances. This principal id should not get 
changed in the different principal instance objects. The principal object also
defines a list of roles. If a principal defins such a list of role ids, this
means the principal has this roles. In the default zope security policy the
role for principal assignment is done via groups which menas we need to use 
an additional indirection.

Note, this concept only works if you exactly know which user belongs to which
principal and based on the principal settings what role he has. Setup different
principal types is very simple if you use z3c.authentication.

Let's setup a principal based on our IAliasPrincipal base class:

  >>> from p01.secureprincipal.principal import AliasPrincipalBase
  >>> class User(object):
  ...     title = u''
  ...     description = u''
  ...     def __init__(self, name):
  ...         self.__name__ = name

  >>> class AliasPrincipal(AliasPrincipalBase):
  ...     _alias = u'MyPrincipals'
  ...     _roles = [u'my.role', u'another.role']

  >>> user = User('bob')
  >>> principal = AliasPrincipal(user)
  >>> principal
  <AliasPrincipal bob>

Roles and permissions are also represented by objects, however, for
the purposes of the security policy, only string ``ids`` are used.

The security policy provides a factory for creating interactions:

  >>> import p01.secureprincipal.policy
  >>> interaction = p01.secureprincipal.policy.PrincipalAliasSecurityPolicy()

An interaction represents a specific interaction between some principals
(normally users) and the system. Normally, we are only concerned with the
interaction of one principal with the system, although we can have interactions
of multiple principals. Multiple-principal interactions normally occur when
untrusted users store code on a system for later execution.  When untrusted
code is executing, the authors of the code participate in the interaction.
An interaction has a permission on an object only if all of the principals
participating in the interaction have access to the object.

The ``checkPermission`` method on interactions is used to test whether an
interaction has a permission for an object. An interaction without participants
always has NO permission:

  >>> interaction.checkPermission('P1', ob)
  False

In this example, 'P1' is a permission id.

Normaly, interactions have participants:

  >>> class Participation:
  ...     interaction = None
  >>> participation = Participation()
  >>> participation.principal = principal
  >>> interaction.add(participation)

If we have participants, then we don't have a permission unless there
are grants:

  >>> interaction.checkPermission('P1', ob)
  False

Note, however, that we always have the CheckerPublic permission:

  >>> from zope.security.checker import CheckerPublic
  >>> interaction.checkPermission(CheckerPublic, ob)
  True

We make grants and denials on objects by adapting them to various
granting interfaces.  The objects returned from the adaptation are 
object-specific manager objects:

  >>> from zope.securitypolicy import interfaces
  >>> roleper  = interfaces.IRolePermissionManager(ob)
  >>> prinrole = interfaces.IPrincipalRoleManager(ob)
  >>> prinper  = interfaces.IPrincipalPermissionManager(ob)

The computations involved in checking permissions can be
significant. To reduce the computational cost, caching is used
extensively. We could invalidate the cache as we make grants, but the
adapters for making grants will automatically invalidate the cache of
the current interaction.  They use the security-management apis to do
this. To take advantage of the cache invalidation, we'll need to let
the security-management system manage our interactions.  First, we'll
set our security policy as the default:

  >>> import zope.security.management
  >>> oldpolicy = zope.security.management.setSecurityPolicy(
  ...      p01.secureprincipal.policy.PrincipalAliasSecurityPolicy)

and then we'll create a new interaction:

  >>> participation = Participation()
  >>> participation.principal = principal
  >>> zope.security.management.newInteraction(participation)
  >>> interaction = zope.security.management.getInteraction()

We normally provide access by granting permissions to roles for an object:

  >>> roleper.grantPermissionToRole('P1', 'R1')

and then granting roles to principals for an object (local roles):

  >>> prinrole.assignRoleToPrincipal('R1', 'bob')

The combination of these grants, which we call a role-based grant,
provides the permission:

  >>> interaction.checkPermission('P1', ob)
  True

We can also provide a permission directly:

  >>> prinper.grantPermissionToPrincipal('P2', 'bob')
  >>> interaction.checkPermission('P2', ob)
  True

Permission grants or denials override role-based grant or denials.  So
if we deny P1:

  >>> prinper.denyPermissionToPrincipal('P1', 'bob')

we cause the interaction to lack the permission, despite the role
grants:

  >>> interaction.checkPermission('P1', ob)
  False

Similarly, even if we have a role-based denial of P2:

  >>> roleper.denyPermissionToRole('P2', 'R1')

we still have access, because of the permission-based grant:

  >>> interaction.checkPermission('P2', ob)
  True

A role-based denial doesn't actually deny a permission; rather it
prevents the granting of a permission. So, if we have both grants and
denials based on roles, we have access:

  >>> roleper.grantPermissionToRole('P3', 'R1')
  >>> roleper.grantPermissionToRole('P3', 'R2')
  >>> roleper.denyPermissionToRole('P3', 'R3')
  >>> prinrole.removeRoleFromPrincipal('R2', 'bob')
  >>> prinrole.assignRoleToPrincipal('R3', 'bob')

  >>> interaction.checkPermission('P3', ob)
  True


Global grants
-------------

Grants made to an object are said to be "local".  We can also make
global grants:

  >>> from zope.securitypolicy.rolepermission import \
  ...     rolePermissionManager as roleperG
  >>> from zope.securitypolicy.principalpermission import \
  ...     principalPermissionManager as prinperG
  >>> from zope.securitypolicy.principalrole import \
  ...     principalRoleManager as prinroleG

And the same rules apply to global grants and denials.

  >>> roleperG.grantPermissionToRole('P1G', 'R1G', False)

In these tests, we aren't bothering to define any roles, permissions,
or principals, so we pass an extra argument that tells the granting
routines not to check the validity of the values.

  >>> prinroleG.assignRoleToPrincipal('R1G', 'bob', False)
  >>> interaction.checkPermission('P1G', ob)
  True

  >>> prinperG.grantPermissionToPrincipal('P2G', 'bob', False)
  >>> interaction.checkPermission('P2G', ob)
  True

  >>> prinperG.denyPermissionToPrincipal('P1G', 'bob', False)
  >>> interaction.checkPermission('P1G', ob)
  False

  >>> roleperG.denyPermissionToRole('P2G', 'R1G', False)
  >>> interaction.checkPermission('P2G', ob)
  True

  >>> roleperG.grantPermissionToRole('P3G', 'R1G', False)
  >>> roleperG.grantPermissionToRole('P3G', 'R2G', False)
  >>> roleperG.denyPermissionToRole('P3G', 'R3G', False)
  >>> prinroleG.removeRoleFromPrincipal('R2G', 'bob', False)
  >>> prinroleG.assignRoleToPrincipal('R3G', 'bob', False)
  >>> interaction.checkPermission('P3G', ob)
  True


Local versus global grants
--------------------------

We, of course, acquire global grants by default:

  >>> interaction.checkPermission('P1G', ob)
  False
  >>> interaction.checkPermission('P2G', ob)
  True
  >>> interaction.checkPermission('P3G', ob)
  True

Local role-based grants do not override global principal-specific denials:

  >>> roleper.grantPermissionToRole('P1G', 'R1G')
  >>> prinrole.assignRoleToPrincipal('R1G', 'bob')
  >>> interaction.checkPermission('P1G', ob)
  False

And local role-based denials don't override global
principal-grants:

  >>> roleper.denyPermissionToRole('P2G', 'R1G')
  >>> interaction.checkPermission('P2G', ob)
  True

A local role-based deny can cancel a global role-based grant:

  >>> roleper.denyPermissionToRole('P3G', 'R1G')
  >>> interaction.checkPermission('P3G', ob)
  False

and a local role-based grant can override a global role-based denial:

  >>> roleperG.denyPermissionToRole('P4G', 'R1G', False)
  >>> prinroleG.assignRoleToPrincipal('R1G', "bob", False)
  >>> interaction.checkPermission('P4G', ob)
  False
  >>> roleper.grantPermissionToRole('P4G', 'R1G')
  >>> interaction.checkPermission('P4G', ob)
  True
  >>> prinroleG.removeRoleFromPrincipal('R1G', "bob", False)
  >>> interaction.checkPermission('P4G', ob)
  True

Of course, a local permission-based grant or denial overrides any
global setting and overrides local role-based grants or denials:

  >>> prinper.grantPermissionToPrincipal('P3G', 'bob')
  >>> interaction.checkPermission('P3G', ob)
  True

  >>> prinper.denyPermissionToPrincipal('P2G', 'bob')
  >>> interaction.checkPermission('P2G', ob)
  False


Sublocations
------------

We can have sub-locations. A sublocation of a location is an object
whose ``__parent__`` attribute is the location:

  >>> ob2 = Ob()
  >>> ob2.__parent__ = ob

By default, sublocations acquire grants from higher locations:

  >>> interaction.checkPermission('P1', ob2)
  False
  >>> interaction.checkPermission('P2', ob2)
  True
  >>> interaction.checkPermission('P3', ob2)
  True
  >>> interaction.checkPermission('P1G', ob2)
  False
  >>> interaction.checkPermission('P2G', ob2)
  False
  >>> interaction.checkPermission('P3G', ob2)
  True
  >>> interaction.checkPermission('P4G', ob2)
  True

Sublocation role-based grants do not override their parent
principal-specific denials:

  >>> roleper2  = interfaces.IRolePermissionManager(ob2)
  >>> prinrole2 = interfaces.IPrincipalRoleManager(ob2)
  >>> prinper2  = interfaces.IPrincipalPermissionManager(ob2)

  >>> roleper2.grantPermissionToRole('P1', 'R1')
  >>> prinrole2.assignRoleToPrincipal('R1', 'bob')
  >>> interaction.checkPermission('P1', ob2)
  False

And local role-based denials don't override their parents
principal-grant:

  >>> roleper2.denyPermissionToRole('P2', 'R1')
  >>> interaction.checkPermission('P2', ob2)
  True

A local role-based deny can cancel a parent role-based grant:

  >>> roleper2.denyPermissionToRole('P3', 'R1')
  >>> interaction.checkPermission('P3', ob2)
  False

and a local role-based grant can override a parent role-based denial:

  >>> roleper.denyPermissionToRole('P4', 'R1')
  >>> prinrole.assignRoleToPrincipal('R1', 'bob')
  >>> interaction.checkPermission('P4', ob2)
  False
  >>> roleper2.grantPermissionToRole('P4', 'R1')
  >>> interaction.checkPermission('P4', ob2)
  True
  >>> prinrole.removeRoleFromPrincipal('R1', 'bob')
  >>> interaction.checkPermission('P4', ob2)
  True


Of course, a local permission-based grant or denial overrides any
global setting and overrides local role-based grants or denials:

  >>> prinper.grantPermissionToPrincipal('P3', 'bob')
  >>> interaction.checkPermission('P3', ob2)
  True

  >>> prinper.denyPermissionToPrincipal('P2', 'bob')
  >>> interaction.checkPermission('P2', ob2)
  False

If an object is not annotatable, but does have a parent, it will get
its grants from its parent:

  >>> class C:
  ...     pass

  >>> ob3 = C()
  >>> ob3.__parent__ = ob

  >>> interaction.checkPermission('P1', ob3)
  False
  >>> interaction.checkPermission('P2', ob3)
  False
  >>> interaction.checkPermission('P3', ob3)
  True
  >>> interaction.checkPermission('P1G', ob3)
  False
  >>> interaction.checkPermission('P2G', ob3)
  False
  >>> interaction.checkPermission('P3G', ob3)
  True
  >>> interaction.checkPermission('P4G', ob3)
  True

The same results will be had if there are multiple non-annotatable
objects:

  >>> ob3.__parent__ = C()
  >>> ob3.__parent__.__parent__ = ob

  >>> interaction.checkPermission('P1', ob3)
  False
  >>> interaction.checkPermission('P2', ob3)
  False
  >>> interaction.checkPermission('P3', ob3)
  True
  >>> interaction.checkPermission('P1G', ob3)
  False
  >>> interaction.checkPermission('P2G', ob3)
  False
  >>> interaction.checkPermission('P3G', ob3)
  True
  >>> interaction.checkPermission('P4G', ob3)
  True

and if an object doesn't have a parent:

  >>> ob4 = C()

it will have whatever grants were made globally:

  >>> interaction.checkPermission('P1', ob4)
  False
  >>> interaction.checkPermission('P2', ob4)
  False
  >>> interaction.checkPermission('P3', ob4)
  False
  >>> interaction.checkPermission('P1G', ob4)
  False
  >>> interaction.checkPermission('P2G', ob4)
  True
  >>> interaction.checkPermission('P3G', ob4)
  False
  >>> interaction.checkPermission('P4G', ob4)
  False

  >>> prinroleG.assignRoleToPrincipal('R1G', "bob", False)
  >>> interaction.checkPermission('P3G', ob4)
  True

We'll get the same result if we have a non-annotatable parent without a
parent:

  >>> ob3.__parent__ = C()

  >>> interaction.checkPermission('P1', ob3)
  False
  >>> interaction.checkPermission('P2', ob3)
  False
  >>> interaction.checkPermission('P3', ob3)
  False
  >>> interaction.checkPermission('P1G', ob3)
  False
  >>> interaction.checkPermission('P2G', ob3)
  True
  >>> interaction.checkPermission('P3G', ob3)
  True
  >>> interaction.checkPermission('P4G', ob3)
  False

The Anonymous role
------------------

The security policy defines a special role named "zope.Anonymous".  All
principals have this role and the role cannot be taken away.

  >>> roleperG.grantPermissionToRole('P5', 'zope.Anonymous', False)
  >>> interaction.checkPermission('P5', ob2)
  True

Proxies
-------

Objects may be proxied:

  >>> from zope.security.checker import ProxyFactory
  >>> ob = ProxyFactory(ob)
  >>> interaction.checkPermission('P1', ob)
  False
  >>> interaction.checkPermission('P2', ob)
  False
  >>> interaction.checkPermission('P3', ob)
  True
  >>> interaction.checkPermission('P1G', ob)
  False
  >>> interaction.checkPermission('P2G', ob)
  False
  >>> interaction.checkPermission('P3G', ob)
  True
  >>> interaction.checkPermission('P4G', ob)
  True

as may their parents:

  >>> ob3 = C()
  >>> ob3.__parent__ = ob

  >>> interaction.checkPermission('P1', ob3)
  False
  >>> interaction.checkPermission('P2', ob3)
  False
  >>> interaction.checkPermission('P3', ob3)
  True
  >>> interaction.checkPermission('P1G', ob3)
  False
  >>> interaction.checkPermission('P2G', ob3)
  False
  >>> interaction.checkPermission('P3G', ob3)
  True
  >>> interaction.checkPermission('P4G', ob3)
  True


Permission for Principal Alias
------------------------------

AliasPrincipals have an alias id. An alias id is a shared principal id across
all (same) principals. Normal this is done by define an alias id for a given
class implementation by define/share an alias id as class variable. But any
other concept for apply the same alias id to a set of different principals can
be used.

The PrincipalAliasSecurityPolicy is able to lookup permissions and roles for
such a principal alias id additional to the principals unique instance based
principal id.

Grant's for such a mapping can be done with the IPrincipalPermissionManager.

We can test the principal alias id by set a permission or role for such an
alias. Let's setup a permission for such an alias. Let's check if we have 
permisstion for access the object.

  >>> interaction.checkPermission('P1', ob)
  False

  >>> alias = principal.alias
  >>> alias
  u'MyPrincipals'

  >>> prinper.grantPermissionToPrincipal('P1', alias)

As you can see we do not have permission but we shouldn't. No we should not
because there is still a permission deny grant for our principal.

  >>> interaction.checkPermission('P1', ob)
  False

Let's unset the deny grant for our principal and you can see that we get the
permisson based on the alias id:

  >>> prinper.unsetPermissionForPrincipal('P1', 'bob')
  >>> interaction.checkPermission('P1', ob)
  True

We can ensure this by unset the alias based permission. If we remove them, we
should not have access anymore:

  >>> prinper.unsetPermissionForPrincipal('P1', alias)
  >>> interaction.checkPermission('P1', ob)
  False


Role for Principal Alias
------------------------

We can also define role ids for an AliasPrincipal. Grant's for such a mapping
can be done with the IPrincipalRoleManager.

Now let's define a permission for a role which the AliasPrincipal uses. But
first ensure that we don't have the permission:

  >>> interaction.checkPermission('P1', ob)
  False

No set the local role for our alias:

  >>> prinrole.assignRoleToPrincipal('R1', 'MyPrincipals')

Then we should get the permission for our principal based on the given
role/principal settings for our principal alias:

  >>> interaction.checkPermission('P1', ob)
  True

Now let's unset the role for our principal alias:

  >>> prinrole.unsetRoleForPrincipal('R1', 'MyPrincipals')
  >>> interaction.checkPermission('P1', ob)
  False


Permission for Principal Roles
------------------------------

The AliasPrincipal can also define roles directly in it's instance. We use this
as a group/role mapping replacement. Grant's for such a mapping can be done
with the IRolePermissionManager:

  >>> principal.roles
  [u'my.role', u'another.role']

Now let's ensure we do not have the permission ``P1``:

  >>> interaction.checkPermission('P1', ob)
  False

And define a local permission for one of our built in roles:

  >>> roleper.grantPermissionToRole('P1', 'my.role')
  >>> interaction.checkPermission('P1', ob)
  True

As you can see, we will get the permission based on our built in role:

Let's unset and test:

  >>> roleper.unsetPermissionFromRole('P1', 'my.role')
  >>> interaction.checkPermission('P1', ob)
  False


Multiple participations
-----------------------

Now check if we will get the same result if we use more then one participation.
this will more or less only test if we collect seen principal ids in the
coverage test. This is the reason why we use the same user and principal
as before.

Note, the first participation which returns Allow (True) wins all
possible Deny in the following participation are not checked.

Let's setup a second participation:

  >>> user2 = User('bob')
  >>> principal2 = AliasPrincipal(user)
  >>> participation2 = Participation()
  >>> participation2.principal = principal2
  >>> interaction.add(participation2)
  >>> interaction.checkPermission('P1', ob)
  False

Now we can grant and check the permission for the system user:

  >>> prinper.grantPermissionToPrincipal('P1', alias)
  >>> interaction.checkPermission('P1', ob)
  True

Unset and test:

  >>> prinper.unsetPermissionForPrincipal('P1', alias)
  >>> interaction.checkPermission('P1', ob)
  False


System User
-----------

Check if the system user will allways be allowed to access anything.
We need ot start a new interaction with the system user as participant.
as you can see the current principal does not has the permission ``P1``:

  >>> participation3 = Participation()
  >>> participation3.principal = zope.security.management.system_user

  >>> interaction.checkPermission('P1', ob)
  False

  >>> interaction.add(participation3)

Now we can check the permission for te system user:

  >>> interaction.checkPermission('P1', ob)
  True


cleanup
-------

We clean up the changes we made in these examples:

  >>> zope.security.management.endInteraction()
  >>> ignore = zope.security.management.setSecurityPolicy(oldpolicy)
