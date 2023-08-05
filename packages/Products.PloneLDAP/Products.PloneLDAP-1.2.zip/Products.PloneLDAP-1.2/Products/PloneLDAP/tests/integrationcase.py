"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase

ZopeTestCase.installProduct("PloneLDAP")

class PloneLDAPIntegrationTestCase(ZopeTestCase.ZopeTestCase):
    """Base class for PloneLDAP integration cases.
    """

