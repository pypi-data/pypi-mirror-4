import logging
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

logger = logging.getLogger("PloneLDAP")

class UserAdderMixin:
    """Implement Products.PluggableAuthService.interfaces.plugins.IUserAdderPlugin
    """
    security = ClassSecurityInfo()

    security.declarePrivate('doAddUser')
    def doAddUser(self , login , password):
        """ Fulfill the UserAdderPlugin requirements """
        acl = self._getLDAPUserFolder()

        if acl is None:
            return False

        attrs = {}
        attrs['dn'] = login
        attrs['user_pw'] = attrs['confirm_pw'] = password
        # For uid and loginname we assume that they are the same. This
        # need not be true, but PlonePAS treats them the same when creating
        # users.
        for key in ( acl._uid_attr, acl._login_attr, acl._rdnattr):
            if key not in attrs:
                attrs[key] = login

        # Evil: grab all schema attributes and will them with a default
        # text. This is needed to be able to create LDAP entries where
        # attributes besides uid, login and rdn are required.
        for (key,name) in acl.getLDAPSchema():
            if key not in attrs:
                attrs[key]="unset"

        res=acl.manage_addUser(kwargs=attrs)

        if res:
            logger.error('manage_addUser failed with %s' % res)

        view_name = self.getId() + '_enumerateUsers'
        self.ZCacheable_invalidate(view_name = view_name,)

        return not res

InitializeClass(UserAdderMixin)

