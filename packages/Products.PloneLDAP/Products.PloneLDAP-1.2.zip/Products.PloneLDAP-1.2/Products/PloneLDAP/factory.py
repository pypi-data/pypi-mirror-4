from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.LDAPUserFolder import manage_addLDAPUserFolder
from Products.PloneLDAP.plugins.ldap import PloneLDAPMultiPlugin
from Products.PloneLDAP.plugins.ad import PloneActiveDirectoryMultiPlugin


manage_addPloneLDAPMultiPluginForm = PageTemplateFile("www/addLdapPlugin",
                                                        globals())

manage_addPloneActiveDirectoryMultiPluginForm = PageTemplateFile("www/addAdPlugin",
                                                        globals())

def genericPluginCreation(self, klass, id, title, login_attr, uid_attr,
        users_base, users_scope, roles, groups_base, groups_scope, binduid,
        bindpwd, binduid_usage=1, rdn_attr='cn', local_groups=0, use_ssl=0,
        encryption='SHA', read_only=0, LDAP_server=None,
        obj_classes='pilotPerson,uidObject', REQUEST=None):
    # Make sure we really are working in our container (the
    # PluggableAuthService object)
    self = self.this()

    # First we create the plugin
    plugin = klass(id, title)
    self._setObject(id, plugin)
    plugin = getattr(aq_base(self), id)

    # And then we have to create an LDAPUserFolder inside it
    manage_addLDAPUserFolder(plugin)
    luf=getattr(aq_base(plugin), "acl_users")

    # Figure out the LDAP port number to use
    if LDAP_server is not None:
        host_elems = LDAP_server.split(':')
        host = host_elems[0]
        if len(host_elems) > 1:
            port = host_elems[1]
        else:
            if use_ssl:
                port = '636'
            else:
                port = '389'
        luf.manage_addServer(host, port=port, use_ssl=use_ssl, op_timeout=10)

    # clean out the __allow_groups__ bit because it is not needed here
    # and potentially harmful
    plugin_base = aq_base(plugin)
    if hasattr(plugin_base, '__allow_groups__'):
        del plugin_base.__allow_groups__

    # Configure the LDAPUserFolder
    luf.manage_edit(title, login_attr, uid_attr, users_base, users_scope,
            roles, groups_base, groups_scope, binduid, bindpwd,
            binduid_usage=binduid_usage, rdn_attr=rdn_attr,
            local_groups=local_groups, encryption=encryption,
            read_only=read_only, obj_classes=obj_classes,
            REQUEST=None)

    return luf

def manage_addPloneLDAPMultiPlugin(self, id, title, LDAP_server, login_attr,
        uid_attr, users_base, users_scope, roles, groups_base, groups_scope,
        binduid, bindpwd, binduid_usage=1, rdn_attr='cn', local_groups=0,
        use_ssl=0, encryption='SHA', read_only=0, REQUEST=None):
    """Add a Plone LDAP plugin to the site"""

    luf=genericPluginCreation(self, PloneLDAPMultiPlugin, id=id, title=title,
            login_attr=login_attr, uid_attr=uid_attr, users_base=users_base,
            users_scope=users_scope, roles=roles, groups_base=groups_base,
            groups_scope=groups_scope, binduid=binduid, bindpwd=bindpwd,
            binduid_usage=binduid_usage, rdn_attr=rdn_attr,
            local_groups=local_groups, use_ssl=use_ssl, encryption=encryption,
            read_only=read_only, LDAP_server=LDAP_server, REQUEST=None)

    luf._ldapschema["cn"]["public_name"]="fullname"
    luf.manage_addLDAPSchemaItem("mail", "Email Address",
            public_name="email")

    # Redirect back to the user folder
    if REQUEST is not None:
        return REQUEST["RESPONSE"].redirect("%s/manage_workspace?manage_tabs_message=AutoGroup+plugin+added" %
                self.absolute_url())




def manage_addPloneActiveDirectoryMultiPlugin(self, id, title,
        login_attr, uid_attr, users_base, users_scope, roles, groups_base,
        groups_scope, binduid, bindpwd, binduid_usage=1, rdn_attr='cn',
        local_groups=0, use_ssl=0, encryption='SHA', read_only=0,
        LDAP_server=None, REQUEST=None):
    """Add a Plone Active Directory plugin to the site"""

    luf=genericPluginCreation(self, klass=PloneActiveDirectoryMultiPlugin,
            id=id, title=title, login_attr=login_attr, uid_attr=uid_attr,
            users_base=users_base, users_scope=users_scope, roles=roles,
            groups_base=groups_base, groups_scope=groups_scope,
            binduid=binduid, bindpwd=bindpwd, binduid_usage=binduid_usage,
            rdn_attr=rdn_attr, local_groups=local_groups, use_ssl=use_ssl,
            encryption=encryption, read_only=read_only,
            LDAP_server=LDAP_server, REQUEST=None)

    luf._ldapschema =   { 'cn' : { 'ldap_name' : 'cn'
                                , 'friendly_name' : 'Canonical Name'
                                , 'multivalued' : ''
                                , 'public_name' : ''
                                }
                       , 'sn' : { 'ldap_name' : 'sn'
                                , 'friendly_name' : 'Last Name'
                                , 'multivalued' : ''
                                , 'public_name' : 'last_name'
                                }
                       }
    luf.manage_addLDAPSchemaItem('dn', 'Distinguished Name',
                                public_name='dn')
    luf.manage_addLDAPSchemaItem('sAMAccountName', 'Windows Login Name',
                                public_name='windows_login_name')
    luf.manage_addLDAPSchemaItem('objectGUID', 'AD Object GUID',
                                public_name='objectGUID')
    luf.manage_addLDAPSchemaItem('givenName', 'First Name',
                                public_name='first_name')
    luf.manage_addLDAPSchemaItem('sn', 'Last Name',
                                public_name='last_name')
    luf.manage_addLDAPSchemaItem('memberOf',
                                'Group DNs',
                                public_name='memberOf',
                                multivalued=True)
    filters = [ ]
    # Ignore disabled accounts. This prevents disabled accounts from showing
    # up in user searches (ACCOUNTDISABLE flag).
    filters.append("(!(userAccountControl:1.2.840.113556.1.4.803:=2))")
    # Only accept normal accounts, not computer/workstation trust accounts
    # or temporary duplicate (local user) accounts (NORMAL_ACCOUNT flag).
    filters.append("(userAccountControl:1.2.840.113556.1.4.803:=512)")
    # Ignore accounts which do not require a password. These accounts are
    # used by services such as IIS (PASSWD_NOTREQD flag)
    filters.append("(!(userAccountControl:1.2.840.113556.1.4.803:=32))")

    luf._extra_user_filer = "(&%s)" % "".join(filters)

    # Redirect back to the user folder
    if REQUEST is not None:
        return REQUEST["RESPONSE"].redirect("%s/manage_workspace?manage_tabs_message=AutoGroup+plugin+added" %
                self.absolute_url())
