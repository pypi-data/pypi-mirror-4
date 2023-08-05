from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService.PluggableAuthService import \
                registerMultiPlugin
from Products.PloneLDAP.plugins.ldap import PloneLDAPMultiPlugin
from Products.PloneLDAP.plugins.ad import PloneActiveDirectoryMultiPlugin
from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPluginForm
from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
from Products.PloneLDAP.factory  \
        import manage_addPloneActiveDirectoryMultiPluginForm
from Products.PloneLDAP.factory \
        import manage_addPloneActiveDirectoryMultiPlugin

registerMultiPlugin(PloneLDAPMultiPlugin.meta_type)
registerMultiPlugin(PloneActiveDirectoryMultiPlugin.meta_type)


def initialize(context):

    context.registerClass(
            PloneLDAPMultiPlugin,
            permission=add_user_folders,
            constructors=(manage_addPloneLDAPMultiPluginForm,
                manage_addPloneLDAPMultiPlugin),
            icon="www/ldapmultiplugin.png",
            visibility=None)

    context.registerClass(
            PloneActiveDirectoryMultiPlugin,
            permission=add_user_folders,
            constructors=(manage_addPloneActiveDirectoryMultiPluginForm,
                manage_addPloneActiveDirectoryMultiPlugin),
            icon="www/admultiplugin.png",
            visibility=None)

