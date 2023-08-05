import logging
from Globals import InitializeClass
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.PluggableAuthService.utils import createViewName
from Products.PluggableAuthService.PluggableAuthService import \
        _SWALLOWABLE_PLUGIN_EXCEPTIONS
from Products.PluggableAuthService.interfaces.plugins import \
    IRolesPlugin, IPropertiesPlugin, IGroupEnumerationPlugin

from Products.PlonePAS.plugins.group import PloneGroup

logger = logging.getLogger("PloneLDAP")


class PloneLDAPPluginBaseMixin:
    security = ClassSecurityInfo()

    security.declarePrivate("_getUser")
    def _getUser(self, uid):
        """Utility method to get a user by userid."""

        acl = self._getLDAPUserFolder()
        if acl is not None:
            return acl.getUserById(uid)
        return None

    # The following _ methods gracefuly adapted from PlonePAS.group.GroupManager
    security.declarePrivate('_createGroup')
    def _createGroup(self, plugins, group_id, name):
        """ Create group object. For users, this can be done with a
        plugin, but I don't care to define one for that now. Just uses
        PloneGroup.  But, the code's still here, just commented out.
        This method based on PluggableAuthervice._createUser
        """

        #factories = plugins.listPlugins(IUserFactoryPlugin)

        #for factory_id, factory in factories:

        #    user = factory.createUser(user_id, name)

        #    if user is not None:
        #        return user.__of__(self)

        return PloneGroup(group_id, name).__of__(self)

    security.declarePrivate('_findGroup')
    def _findGroup(self, plugins, group_id, title=None, request=None):
        """ group_id -> decorated_group
        This method based on PluggableAuthService._findGroup
        """

        # See if the group can be retrieved from the cache
        view_name = '_findGroup-%s' % group_id
        keywords = {'group_id': group_id,
                    'title': title}
        group = self.ZCacheable_get(view_name=view_name,
                                    keywords=keywords,
                                    default=None)

        if group is None:

            group = self._createGroup(plugins, group_id, title)

            propfinders = plugins.listPlugins(IPropertiesPlugin)
            for propfinder_id, propfinder in propfinders:

                data = propfinder.getPropertiesForUser(group, request)
                if data:
                    group.addPropertysheet(propfinder_id, data)

            groups = self._getPAS()._getGroupsForPrincipal(group, request,
                                                           plugins=plugins)
            group._addGroups(groups)

            rolemakers = plugins.listPlugins(IRolesPlugin)

            for rolemaker_id, rolemaker in rolemakers:

                roles = rolemaker.getRolesForPrincipal(group, request)

                if roles:
                    group._addRoles(roles)

            group._addRoles(['Authenticated'])

            # Cache the group if caching is enabled
            base_group = aq_base(group)
            if getattr(base_group, '_p_jar', None) is None:
                self.ZCacheable_set(base_group, view_name=view_name,
                                    keywords=keywords)

        return group

    security.declarePrivate('_verifyGroup')
    def _verifyGroup(self, plugins, group_id=None, title=None):

        """ group_id -> boolean
        This method based on PluggableAuthService._verifyUser
        """
        criteria = {}

        if group_id is not None:
            criteria['id'] = group_id
            criteria['exact_match'] = True

        if title is not None:
            criteria['title'] = title

        if criteria:
            view_name = createViewName('_verifyGroup', group_id)
            cached_info = self.ZCacheable_get(view_name=view_name,
                                              keywords=criteria,
                                              default=None)

            if cached_info is not None:
                return cached_info

            enumerators = plugins.listPlugins(IGroupEnumerationPlugin)

            for enumerator_id, enumerator in enumerators:
                try:
                    info = enumerator.enumerateGroups(**criteria)

                    if info:
                        id = info[0]['id']
                        # Put the computed value into the cache
                        self.ZCacheable_set(id, view_name=view_name,
                                            keywords=criteria)
                        return id

                except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                    logger.exception(
                        'PluggableAuthService: GroupEnumerationPlugin '
                        '%s error', enumerator_id)

        return 0


InitializeClass(PloneLDAPPluginBaseMixin)
