from Products.PloneLDAP.tests.integrationcase import PloneLDAPIntegrationTestCase
from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
from Products.PloneLDAP.factory import manage_addPloneActiveDirectoryMultiPlugin
from Products.PloneLDAP.plugins.ldap import PloneLDAPMultiPlugin
from Products.PloneLDAP.plugins.ad import PloneActiveDirectoryMultiPlugin


class TestLDAPCreation(PloneLDAPIntegrationTestCase):
    def afterSetUp(self):
        manage_addPloneLDAPMultiPlugin(self.folder, "ldap",
                title="title", login_attr="uid", uid_attr="mail",
                users_base="ou=Users", users_scope=0,
                roles="CustomRole", groups_base="ou=Groups",
                groups_scope=1, binduid="cn=admin", bindpwd="XXX",
                rdn_attr="cn", LDAP_server=None)

    def testBasicLDAPCreation(self):
        self.failUnless("ldap" in self.folder.objectIds())

    def testMetaType(self):
        self.assertEqual(self.folder.ldap.meta_type,
                PloneLDAPMultiPlugin.meta_type)

    def testLDAPAttributes(self):
        luf=self.folder.ldap._getLDAPUserFolder()
        self.assertEqual(luf.users_base, "ou=Users")
        self.assertEqual(luf.users_scope, 0)
        self.assertEqual(luf.groups_base, "ou=Groups")
        self.assertEqual(luf.groups_scope, 1)
        self.assertEqual(luf._binduid, "cn=admin")
        self.assertEqual(luf._bindpwd, "XXX")
        self.assertEqual(luf._uid_attr, "mail")
        self.assertEqual(luf._delegate.login_attr, "uid")
        self.assertEqual(luf._delegate.rdn_attr, "cn")
        self.assertEqual(luf._roles, ["CustomRole"])
        self.assertEqual(luf.getServers(), ())


class TestADCreation(TestLDAPCreation):
    def afterSetUp(self):
        manage_addPloneActiveDirectoryMultiPlugin(self.folder, "ldap",
                title="title", login_attr="uid", uid_attr="mail",
                users_base="ou=Users", users_scope=0,
                roles="CustomRole", groups_base="ou=Groups",
                groups_scope=1, binduid="cn=admin", bindpwd="XXX",
                rdn_attr="cn", LDAP_server=None)

    def testMetaType(self):
        self.assertEqual(self.folder.ldap.meta_type,
                PloneActiveDirectoryMultiPlugin.meta_type)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestLDAPCreation))
    suite.addTest(makeSuite(TestADCreation))
    return suite

