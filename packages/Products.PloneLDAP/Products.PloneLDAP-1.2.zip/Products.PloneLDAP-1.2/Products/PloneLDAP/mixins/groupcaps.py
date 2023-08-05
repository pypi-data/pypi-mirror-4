from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class GroupCapabilityMixin:
    """Implement Products.PlonePAS.interfaces.capabilities.IGroupCapability
    """
    security = ClassSecurityInfo()

    def allowGroupAdd(self, principal_id, group_id):
        plugins = self._getPAS()._getOb('plugins')

        group_id = self._verifyGroup(plugins, group_id=group_id)
        user = self.acl_users.getUserById(principal_id)

        if group_id and user:
            return True

        return False

    def allowGroupRemove(self, principal_id, group_id):
        return self.allowGroupAdd(principal_id, group_id)


InitializeClass(GroupCapabilityMixin)

