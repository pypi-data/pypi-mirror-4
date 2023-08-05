from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable

class HiddenLDAPProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return [ "LDAPUserFolder" ]
