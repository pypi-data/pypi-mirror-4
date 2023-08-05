from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class GroupIntrospectionMixin:
    """Implement Products.PlonePAS.interfaces.plugins.IGroupIntrospection
    """
    security = ClassSecurityInfo()

    security.declarePrivate('getGroupById')
    def getGroupById(self, group_id, default=None):
        plugins = self._getPAS()._getOb('plugins')

        group_id = self._verifyGroup(plugins, group_id=group_id)
        title = None

        if not group_id:
            return default

        return self._findGroup(plugins, group_id, title)

    security.declarePrivate('getGroups')
    def getGroups(self):
        groups = [self.getGroupById(x['id']) for x in self.enumerateGroups() if x]
        return groups


    security.declarePrivate('getGroupIds')
    def getGroupIds(self):
        groupIds = [x['id'] for x in self.enumerateGroups() if x]
        return tuple(groupIds)

    security.declarePrivate('getGroupMembers')
    def getGroupMembers(self, group_id):
        groups = ((group_id, None),)
        members = self.acl_users.getGroupedUsers(groups)

        usernames = [x.getId() for x in members if x]

        return usernames


InitializeClass(GroupIntrospectionMixin)

