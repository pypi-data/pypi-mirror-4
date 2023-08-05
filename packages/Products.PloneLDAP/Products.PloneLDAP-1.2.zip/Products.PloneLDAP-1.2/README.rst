Introduction
============
The PloneLDAP product is intended to make it easier to use LDAP connections in
a Plone website. It builds upon the excellent LDAPMultiPlugins_ and
LDAPUserFolder_ products which provide the basic LDAP infrastructure. 

For Plone 3.3 or higher, we recommend using `plone.app.ldap`_ for
having a nicer user interface for using LDAP with Plone.  This uses
``PloneLDAP``.

.. _`plone.app.ldap`: http://pypi.python.org/pypi/plone.app.ldap

The extra functionality provided by this product require features
beyond that are not part of the standard Pluggable Authentication Service,
which is why they are not included in LDAPMultiPlugins.

.. _LDAPMultiPlugins: http://www.dataflake.org/software/ldapmultiplugins
.. _LDAPUserFolder: http://www.dataflake.org/software/ldapuserfolder

PloneLDAP integrates LDAP fully into your Plone site:

* users in an LDAP database can be used as normal users in Plone. You
  can search for them, assign roles to them, create them and remove them.

* groups in an LDAP database can be used as normal groups in Plone. You
  can view them, manage group members, create new groups and remove them.
  LDAP groups can only have LDAP users as members. LDAP users can be
  group members of non-LDAP groups.

* member properties for LDAP users need not be stored completely in the
  LDAP database: you can mix LDAP and ZODB-stored properties.


Active Directory
================

Please note that if you are using Active Directory (AD) all access is
read-only.  For example, you cannot add AD users to AD groups.


Requirements
============

* Plone 3.0 or later
* python-ldap_
* LDAPUserFolder 2.8 or later
* LDAPMultiPlugins 1.5 or later

.. _python-ldap: http://python-ldap.sourceforge.net/

Products.PloneLDAP depends on LDAPMultiPlugins and LDAPUserFolder, so they
will be installed automatically.

For the record, it has been tested with these most recent versions::

  Plone = 4.2.2
  Products.LDAPMultiPlugins = 1.14
  Products.LDAPUserFolder = 2.24
  dataflake.fakeldap = 1.1
  python-ldap = 2.4.10


Installation
============

First you need to install the python-ldap package. Once that has been
installed you need to add the Products.PloneLDAP egg to your Plone instance.
If you use buildout just add ``Products.PloneLDAP`` to the list of required
eggs. Otherwise you will need to use ``easy_install``. See the documentation
on plone.org for more information on installing third party packages.

  **Do not install LDAPUserFolder from the Plone site setup screen. This
  will break your Plone site.**

PloneLDAP provides PAS plugins that you can use to get your site talking to
LDAP or Active Directory. To install them go the acl_users folder in your
site. Select the right plugin from the dropdown menu in the top right: use
'Plone LDAP Plugin' if you want to connect to a standard LDAP server or
'Plone Active Directory Plugin' if you want to connect to a Microsoft Active
Directory server. 

After selecting the plugin type you will see a screen where you need to
submit the configuration information. Consult your LDAP or AD administrator
if you are not sure what the correct information is.

After creating the plugin it has to be activated. To do this go to the
plugin in the ZMI and go to the 'navigate' tab, select all plugin types
and click on the 'Update' button.

As a final change you will need to reorder the plugin order. Reodering
can be done by clicking on the name of a plugin type, selecting a plugin
in the 'Active Plugins' list and using the up and down arrows to change
the ordering. The required ordering changes are:

* Properties: LDAP has to be the top plugin
* Group_Management: LDAP should be the top plugin if you want to
  create groups in the LDAP database
* User_Adder: has to be the top plugin if you want new users to be
  created in LDAP
* User_Management: LDAP has to be the top plugin


LDAP caveats
============

LDAPUserFolder
--------------
Inside the PloneLDAP PAS plugin you will see another acl_users user folder.
This is a ''LDAPUserFolder'' instance, which is used to manage the low-level
communication with the LDAP server. By updating its properties you can
reconfigure your LDAP connection.

The LDAPUserFolder instance is only used to communicate with the LDAP server.
Its user and group management facilities are not used. You can use it to
quickly test if your LDAP connection is correctly configured.

If you make any changes in users or groups through the LDAPUserFolder ZMI
interfaces these will be applied to the LDAP server but the caches used
by the PloneLDAP plugin will not be invalidated correctly. This may lead
to unexpected results and it is strongly recommended to only use the Plone
interface to update users and groups.


Credits
=======

Funding
    CentrePoint_

Implementation
    Simplon_, Wichert Akkerman
 

.. _Simplon: http://www.simplon.biz/
.. _CentrePoint: http://centrepoint.org.uk/


Copyright
=========

PloneLDAP is copyright 2007,2008 by Simplon_ and licensed under the Zope
Public License, version 2.1.

