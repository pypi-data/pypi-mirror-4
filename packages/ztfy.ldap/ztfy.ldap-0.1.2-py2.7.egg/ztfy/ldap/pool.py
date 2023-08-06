### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
import ldap
from ldappool import ConnectionManager
from threading import RLock

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ldapadapter.utility import ManageableLDAPAdapter, LDAPConnection


_pool = {}
_pool_lock = RLock()


class ManageableLDAPPoolAdapter(ManageableLDAPAdapter):
    """LDAP adapter using connection pool"""

    def connect(self, dn=None, password=None):
        conn_str = self.getServerURL()
        connection = _pool.get(conn_str)
        if connection is None:
            with _pool_lock:
                connection = _pool[conn_str] = ConnectionManager(conn_str)
        if dn is None:
            dn = self.bindDN or ''
            password = self.bindPassword or ''
        with connection.connection(dn, password) as conn:
            try:
                conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            except ldap.LDAPError:
                raise Exception("Server should be LDAP v3")
            return LDAPConnection(conn)
