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

# import Zope3 interfaces

# import local interfaces
from ldapadapter.interfaces import ILDAPAdapter
from ldappas.interfaces import ILDAPAuthentication
from ztfy.mail.interfaces import IPrincipalMailInfo
from ztfy.ldap.auth.interfaces import ILDAPGroupInfo, ILDAPPrincipalInfo, ILDAPAuthenticationPlugin

# import Zope3 packages
from zope.component import adapts, queryUtility, getAllUtilitiesRegisteredFor
from zope.interface import implements

# import local packages


class LDAPPrincipalMailInfo(object):
    """LDAP principal mail info adapte"""

    adapts(ILDAPPrincipalInfo)
    implements(IPrincipalMailInfo)

    def __init__(self, context):
        self.context = context

    def getAddresses(self):
        """Get mail address of adapted principal"""
        id = self.context.id
        for plugin in getAllUtilitiesRegisteredFor(ILDAPAuthentication):
            if not id.startswith(plugin.principalIdPrefix):
                continue
            internal_id = id[len(plugin.principalIdPrefix):]
            da = queryUtility(ILDAPAdapter, name=plugin.adapterName)
            if da is None:
                continue
            try:
                conn = da.connect()
                filter = ldap.filter.filter_format('(%s=%s)', (plugin.idAttribute, internal_id))
                res = conn.search(plugin.searchBase, plugin.searchScope,
                                  filter=filter,
                                  attrs=[plugin.titleAttribute, 'mail'])
                dn, entry = res[0]
                return [ (entry[plugin.titleAttribute][0],
                          entry['mail'][0]) ]
            except:
                return None


class LDAPGroupMailInfo(object):
    """LDAPGroup mail info adapter"""

    adapts(ILDAPGroupInfo)
    implements(IPrincipalMailInfo)

    def __init__(self, context):
        self.context = context

    def getAddresses(self):
        """Get mail addresses of adapted group"""

        result = None
        plugin = self.context.plugin
        if plugin.mailMode == u'none':
            result = []
            for principal_id in plugin.getPrincipalsForGroup(self.context.id):
                for auth_plugin in getAllUtilitiesRegisteredFor(ILDAPAuthenticationPlugin):
                    principal_info = auth_plugin.principalInfo(principal_id)
                    if principal_info is not None:
                        info = IPrincipalMailInfo(principal_info, None)
                        if info is not None:
                            result.extend(info.getAddresses())
                            break
            return result

        auth = plugin.authenticator
        if auth is None:
            return None
        internal_id = self.context.id[len(plugin.groupIdPrefix):]

        if plugin.mailMode == u'internal':
            # Use internal group attribute
            res = plugin._search({ auth.groupIdAttribute: internal_id },
                                 attrs=[plugin.titleAttribute, plugin.mailAttribute],
                                 queryType='group')
            try:
                _dn, entry = res[0]
                return [ (entry[plugin.titleAttribute][0],
                          entry[plugin.mailAttribute][0]) ]
            except:
                return result

        elif plugin.mailMode == u'redirect':
            # Use another group attribute in another LDAP branch
            res = plugin._search({ auth.groupIdAttribute: internal_id },
                                 attrs=[auth.groupIdAttribute],
                                 queryType='group')
            try:
                dn, _entry = res[0]
            except:
                return result
            else:
                source, target = plugin.dnReplaceExpression.split('|')
                target_dn = dn.replace(source, target)
                res = plugin._search({ 'objectClass': '*' },
                                     base=target_dn,
                                     scope=ldap.SCOPE_BASE,
                                     attrs=[plugin.titleAttribute, plugin.mailAttribute],
                                     queryType=None)
                try:
                    _dn, entry = res[0]
                    return [ (entry[plugin.titleAttribute][0],
                              entry[plugin.mailAttribute][0]) ]
                except:
                    return result
