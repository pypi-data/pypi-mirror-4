from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class UserManagementMixin:
    """Implement Products.PlonePAS.interfaces.plugins.IUserManagement,
    Products.PlonePAS.interfaces.plugins.IPasswordSetCapability and
    Products.PlonePAS.interfaces.plugins.IDeleteCapability.
    """
    security = ClassSecurityInfo()

    security.declarePrivate('doAddUser')
    def doChangeUser(self, login, password, **kw):
        """ Change a user's password. Only implements password changing
        which is required by IUserManagement."""
        acl = self._getLDAPUserFolder()

        if acl is not None:
            user = acl.getUser(login)

            if user is not None:
                user_dn = user.getUserDN()
                acl.manage_editUserPassword(user_dn, password)


    security.declarePrivate('doDeleteUser')
    def doDeleteUser(self , login):
        """ Remove a user record from a User Manager. """
        acl = self._getLDAPUserFolder()

        if acl is not None:
            user = acl.getUser(login)

            if user is not None:
                user_dn = user.getUserDN()

                acl.manage_deleteUsers(dns=[user_dn])

                view_name = self.getId() + '_enumerateUsers'
                self.ZCacheable_invalidate(view_name = view_name,)


    def allowDeletePrincipal(self, id):
        """Check if we can remove a user."""
        return self._getUser(id) is not None


    def allowPasswordSet(self, id):
        """Check if we can set a users password."""
        return self._getUser(id) is not None


InitializeClass(UserManagementMixin)

