from Products.PlonePAS.interfaces.capabilities import IDeleteCapability
from Products.PlonePAS.interfaces.capabilities import IGroupCapability
from Products.PlonePAS.interfaces.capabilities import IPasswordSetCapability
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin
from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PluggableAuthService.interfaces.plugins import (
    IUserEnumerationPlugin, IGroupsPlugin, IGroupEnumerationPlugin,
    IRoleEnumerationPlugin, IUserAdderPlugin,
    IAuthenticationPlugin, IRolesPlugin,
    ICredentialsResetPlugin, IPropertiesPlugin)
from zope.interface.verify import verifyClass

from Products.PloneLDAP.tests.integrationcase import PloneLDAPIntegrationTestCase
from Products.PloneLDAP.plugins.base import PloneLDAPPluginBaseMixin
from Products.PloneLDAP.plugins.ldap import PloneLDAPMultiPlugin
from Products.PloneLDAP.plugins.ad import PloneActiveDirectoryMultiPlugin


class TestInterfaces(PloneLDAPIntegrationTestCase):
    """Test that the plugins implement the interfaces correctly.

    If we say we implement an interface, we should have the required
    attributes and methods.  Otherwise, we can get errors.  For
    example, the AD plugin used to claim to implement
    IGroupCapability, but it did not have the mixin class that
    delivered the required methods.  So when Plone displays the groups
    of a user that is a member of an AD group, this would give a
    traceback because Plone tried to use one of the advertised
    methods.

    In most cases here we do not mind much if a plugin claims to
    implement an interface or not, but IF it implements it, it must
    fulfill that promise, otherwise we raise an assertion error.

    We would want to use verifyClass, but that fails because the
    PlonePAS interfaces are wrongly defined with 'self', which means a
    test like this would always fail:

    from zope.interface.verify import verifyClass
    self.assertTrue(verifyClass(IGroupCapability, PloneLDAPMultiPlugin))

    It works for the PluggableAuthService interfaces though.
    """

    def _testGroupCapability(self, klass):
        if IGroupCapability.implementedBy(klass):
            # This may or may not be true, but if it is true, then the
            # following should be true as well.
            self.assertTrue(hasattr(klass, 'allowGroupAdd'))
            self.assertTrue(hasattr(klass, 'allowGroupRemove'))

    def _testGroupIntrospection(self, klass):
        if IGroupIntrospection.implementedBy(klass):
            self.assertTrue(hasattr(klass, 'getGroupById'))
            self.assertTrue(hasattr(klass, 'getGroupIds'))
            self.assertTrue(hasattr(klass, 'getGroupMembers'))
            self.assertTrue(hasattr(klass, 'getGroups'))

    def _testGroupManagement(self, klass):
        if IGroupManagement.implementedBy(klass):
            self.assertTrue(hasattr(klass, 'addGroup'))
            self.assertTrue(hasattr(klass, 'addPrincipalToGroup'))
            self.assertTrue(hasattr(klass, 'removeGroup'))
            self.assertTrue(hasattr(klass, 'removePrincipalFromGroup'))
            self.assertTrue(hasattr(klass, 'setRolesForGroup'))
            self.assertTrue(hasattr(klass, 'updateGroup'))

    def _testMutableProperties(self, klass):
        if IMutablePropertiesPlugin.implementedBy(klass):
            self.assertTrue(hasattr(klass, 'deleteUser'))
            self.assertTrue(hasattr(klass, 'getPropertiesForUser'))
            self.assertTrue(hasattr(klass, 'setPropertiesForUser'))

    def _testDeleteCapability(self, klass):
        if IDeleteCapability.implementedBy(klass):
            self.assertTrue(hasattr(klass, 'allowDeletePrincipal'))

    def _testPasswordSetCapability(self, klass):
        if IPasswordSetCapability.implementedBy(klass):
            self.assertTrue(hasattr(klass, 'allowPasswordSet'))

    def _testUserManagement(self, klass):
        if IUserManagement.implementedBy(klass):
            self.assertTrue(hasattr(klass, 'doChangeUser'))
            self.assertTrue(hasattr(klass, 'doDeleteUser'))

    def _verify(self, iface, klass):
        if iface.implementedBy(klass):
            self.assertTrue(verifyClass(iface, klass))

    def _testAuthentication(self, klass):
        self._verify(IAuthenticationPlugin, klass)

    def _testRoles(self, klass):
        self._verify(IRolesPlugin, klass)

    def _testCredentialsReset(self, klass):
        self._verify(ICredentialsResetPlugin, klass)

    def _testProperties(self, klass):
        self._verify(IPropertiesPlugin, klass)

    def _testGroupEnumeration(self, klass):
        self._verify(IGroupEnumerationPlugin, klass)

    def _testUserEnumeration(self, klass):
        self._verify(IUserEnumerationPlugin, klass)

    def _testGroups(self, klass):
        self._verify(IGroupsPlugin, klass)

    def _testRoleEnumeration(self, klass):
        self._verify(IRoleEnumerationPlugin, klass)

    def _testUserAdder(self, klass):
        self._verify(IUserAdderPlugin, klass)

    def testPluginBaseMixin(self):
        klass = PloneLDAPPluginBaseMixin
        self._testGroupCapability(klass)
        self._testGroupIntrospection(klass)
        self._testGroupManagement(klass)
        self._testMutableProperties(klass)
        self._testDeleteCapability(klass)
        self._testPasswordSetCapability(klass)
        self._testUserManagement(klass)
        self._testAuthentication(klass)
        self._testRoles(klass)
        self._testCredentialsReset(klass)
        self._testProperties(klass)
        self._testGroupEnumeration(klass)
        self._testUserEnumeration(klass)
        self._testGroups(klass)
        self._testRoleEnumeration(klass)
        self._testUserAdder(klass)

    def testPluginAD(self):
        klass = PloneActiveDirectoryMultiPlugin
        self._testGroupCapability(klass)
        self._testGroupIntrospection(klass)
        self._testGroupManagement(klass)
        self._testMutableProperties(klass)
        self._testDeleteCapability(klass)
        self._testPasswordSetCapability(klass)
        self._testUserManagement(klass)
        self._testAuthentication(klass)
        self._testRoles(klass)
        self._testCredentialsReset(klass)
        self._testProperties(klass)
        self._testGroupEnumeration(klass)
        self._testUserEnumeration(klass)
        self._testGroups(klass)
        self._testRoleEnumeration(klass)
        self._testUserAdder(klass)

    def testPluginLDAP(self):
        klass = PloneLDAPMultiPlugin
        self._testGroupCapability(klass)
        self._testGroupIntrospection(klass)
        self._testGroupManagement(klass)
        self._testMutableProperties(klass)
        self._testDeleteCapability(klass)
        self._testPasswordSetCapability(klass)
        self._testUserManagement(klass)
        self._testAuthentication(klass)
        self._testRoles(klass)
        self._testCredentialsReset(klass)
        self._testProperties(klass)
        self._testGroupEnumeration(klass)
        self._testUserEnumeration(klass)
        self._testGroups(klass)
        self._testRoleEnumeration(klass)
        self._testUserAdder(klass)

    def testADImplements(self):
        # The above checks are testing that IF we implement an
        # interface we really DO implement it in practice.  If an
        # interface is not implemented, we are fine with it.  But in
        # this test, we check that some interfaces really are
        # implemented.  This should contain all interfaces that are
        # set with the 'class Implements' directive of the klass.
        klass = PloneActiveDirectoryMultiPlugin

        self.assertTrue(IAuthenticationPlugin.implementedBy(klass))
        self.assertTrue(ICredentialsResetPlugin.implementedBy(klass))
        self.assertTrue(IGroupEnumerationPlugin.implementedBy(klass))
        self.assertTrue(IGroupIntrospection.implementedBy(klass))
        self.assertTrue(IGroupsPlugin.implementedBy(klass))
        self.assertTrue(IMutablePropertiesPlugin.implementedBy(klass))
        self.assertTrue(IPropertiesPlugin.implementedBy(klass))
        self.assertTrue(IRoleEnumerationPlugin.implementedBy(klass))
        self.assertTrue(IRolesPlugin.implementedBy(klass))
        self.assertTrue(IUserEnumerationPlugin.implementedBy(klass))

    def testLDAPImplements(self):
        klass = PloneLDAPMultiPlugin

        self.assertTrue(IAuthenticationPlugin.implementedBy(klass))
        self.assertTrue(ICredentialsResetPlugin.implementedBy(klass))
        self.assertTrue(IDeleteCapability.implementedBy(klass))
        self.assertTrue(IGroupCapability.implementedBy(klass))
        self.assertTrue(IGroupEnumerationPlugin.implementedBy(klass))
        self.assertTrue(IGroupIntrospection.implementedBy(klass))
        self.assertTrue(IGroupManagement.implementedBy(klass))
        self.assertTrue(IGroupsPlugin.implementedBy(klass))
        self.assertTrue(IMutablePropertiesPlugin.implementedBy(klass))
        self.assertTrue(IPasswordSetCapability.implementedBy(klass))
        self.assertTrue(IPropertiesPlugin.implementedBy(klass))
        self.assertTrue(IRoleEnumerationPlugin.implementedBy(klass))
        self.assertTrue(IRolesPlugin.implementedBy(klass))
        self.assertTrue(IUserAdderPlugin.implementedBy(klass))
        self.assertTrue(IUserEnumerationPlugin.implementedBy(klass))
        self.assertTrue(IUserManagement.implementedBy(klass))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestInterfaces))
    return suite
