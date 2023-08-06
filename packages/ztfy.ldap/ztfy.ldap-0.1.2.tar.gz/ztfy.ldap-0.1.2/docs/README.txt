=================
ztfy.ldap package
=================

.. contents::

What is ztfy.ldap ?
===================

ztfy.ldap is a small set of utilities and classes to make LDAP interaction
easier within a ZTK/ZopeApp based application.

The main class is LDAPGroupsFolder, which is an authentication plug-in used
to enable LDAP groups as authentication principals. This class is extending
ZTFY.security package so that LDAP groups can be used everywhere where a
principal can be selected to grant a role.

LDAPGroupsFolder code is mainly based on "ldapgroups" package, which seems
actually unmaintained.

Based on ldappool package, ztfy.ldap also provides a pooled LDAP adapter, which
stores it's connections within a pool.

Adapters for some of **ztfy.mail** interfaces are also provided.


How to use ztfy.ldap ?
======================
ztfy.ldap usages will be described on `ZTFY home page`_


.. _`ZTFY home page`: http://www.ztfy.org
