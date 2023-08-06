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
from persistent import Persistent

# import Zope3 interfaces
from zope.app.authentication.groupfolder import IGroupInformation
from zope.app.authentication.interfaces import IAuthenticatorPlugin, IQueriableAuthenticator, \
                                               IQuerySchemaSearch, IPrincipalInfo, \
                                               IAuthenticatedPrincipalCreated
from zope.security.interfaces import IGroupAwarePrincipal

# import local interfaces
from ldap import LDAPError
from ldapadapter.interfaces import ServerDown, NoSuchObject
from ldappas.interfaces import ILDAPAuthentication
from ztfy.cache.metadirectives import ICacheProxyHandlerBase
from ztfy.ldap.auth.interfaces import ILDAPGroupsFolder, ILDAPGroupsMailInfo, ILDAPGroupSearchSchema, \
                                      ILDAPGroupInfo

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.container.contained import Contained
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


class LDAPGroupInformation(object):
    """LDAP group information"""

    implements(IPrincipalInfo, IGroupInformation, ILDAPGroupInfo)

    def __init__(self, plugin, id, title, description):
        self.plugin = plugin
        self.id = id
        self.title = title
        self.description = description

    @property
    def principals(self):
        return self.plugin.getPrincipalsForGroup(self.id)

    def __repr__(self):
        return 'LDAPGroupInformation(%r)' % self.id

    def __eq__(self, other):
        return self.id == other.id


class LDAPGroupsFolder(Persistent, Contained):
    """LDAP groups folder authentication plug-in"""

    implements(IAuthenticatorPlugin, ILDAPGroupsFolder, ILDAPGroupsMailInfo,
               IQueriableAuthenticator, IQuerySchemaSearch)

    _authenticatorName = FieldProperty(ILDAPGroupsFolder['authenticatorName'])
    groupIdPrefix = FieldProperty(ILDAPGroupsFolder['groupIdPrefix'])
    titleAttribute = FieldProperty(ILDAPGroupsFolder['titleAttribute'])
    descriptionAttribute = FieldProperty(ILDAPGroupsFolder['descriptionAttribute'])
    groupRequiredClass = FieldProperty(ILDAPGroupsFolder['groupRequiredClass'])
    principalRequiredClass = FieldProperty(ILDAPGroupsFolder['principalRequiredClass'])
    queryMode = FieldProperty(ILDAPGroupsFolder['queryMode'])
    groupPrincipalsAttribute = FieldProperty(ILDAPGroupsFolder['groupPrincipalsAttribute'])
    groupModeQueryFilter = FieldProperty(ILDAPGroupsFolder['groupModeQueryFilter'])
    principalGroupsAttribute = FieldProperty(ILDAPGroupsFolder['principalGroupsAttribute'])
    principalModeQueryFilter = FieldProperty(ILDAPGroupsFolder['principalModeQueryFilter'])
    cacheProxyName = FieldProperty(ILDAPGroupsFolder['cacheProxyName'])

    mailMode = FieldProperty(ILDAPGroupsMailInfo['mailMode'])
    dnReplaceExpression = FieldProperty(ILDAPGroupsMailInfo['dnReplaceExpression'])
    mailAttribute = FieldProperty(ILDAPGroupsMailInfo['mailAttribute'])

    def __init__(self, auth='', prefix=''):
        super(LDAPGroupsFolder, self).__init__()
        if auth:
            self.authenticatorName = auth
        if prefix:
            self.groupIdPrefix = prefix

    @property
    def authenticatorName(self):
        return self._authenticatorName

    @authenticatorName.setter
    def authenticatorName(self, value):
        self._authenticatorName = value
        if hasattr(self, '_v_auth'):
            delattr(self, '_v_auth')

    @property
    def authenticator(self):
        if not hasattr(self, '_v_auth'):
            self._v_auth = queryUtility(ILDAPAuthentication, self.authenticatorName)
        return self._v_auth


    # IAuthenticatorPlugin interface methods

    def authenticateCredentials(self, credentials):
        """Group folder doesn't authenticate !"""
        pass

    def principalInfo(self, id):
        auth = self.authenticator
        if id.startswith(self.groupIdPrefix):
            id = id[len(self.groupIdPrefix):]
            res = self._search({auth.groupIdAttribute: id},
                               attrs=[auth.groupIdAttribute,
                                      self.titleAttribute,
                                      self.descriptionAttribute],
                               queryType='group')
            if res and (len(res) == 1):
                dn, entry = res[0]
                id_attr = auth.groupIdAttribute
                if id_attr == 'dn':
                    id = dn
                elif entry.get(id_attr):
                    id = entry[id_attr][0]
                else:
                    raise KeyError
                id = self.groupIdPrefix + id
                return self._getGroupInfoFromEntry(id, entry)


    # IQuerySearchSchema interface methods

    schema = ILDAPGroupSearchSchema

    def search(self, query, start=None, batch_size=None):
        auth = self.authenticator
        res = self._search(query, attrs=[auth.groupIdAttribute], queryType='group')
        infos = []
        for dn, entry in res:
            try:
                infos.append(self.groupIdPrefix + entry[auth.groupIdAttribute][0])
            except (KeyError, IndexError):
                pass
        if start is None:
            start = 0
        if batch_size is not None:
            return infos[start:start + batch_size]
        else:
            return infos[start:]


    # ILDAPGroupsFolder interface methods

    def getGroupsForPrincipal(self, principal_id):
        """Get principal groups"""

        auth = self.authenticator
        if auth is None:
            return None
        groups = []
        internal_id = principal_id[len(auth.principalIdPrefix):]

        # Start to get principal's DN
        try:
            attrs = [auth.idAttribute]
            if self.queryMode == 'principal':
                attrs.append(self.principalGroupsAttribute)
            res = self._search({ auth.idAttribute: internal_id },
                               attrs=attrs, queryType='principal')
            user_dn, user_entry = res[0]
        except (KeyError, IndexError):
            return None

        # Check for query filter
        if self.queryMode == 'group':
            attr, value = self.groupModeQueryFilter.split('=')
        else:
            attr, value = self.principalModeQueryFilter.split('=')
        if '%(dn)s' in value:
            dn = user_dn
        elif '%(uid)s' in value:
            uid = internal_id
        value = value % locals()

        if self.queryMode == 'group':
            # In 'group' query mode, we only have to search for
            # groups containing given principal as member
            res = self._search({ attr: value },
                               attrs=[auth.groupIdAttribute],
                               queryType='group')
            for dn, entry in res:
                groups.append(self.groupIdPrefix + entry[auth.groupIdAttribute][0])
        else:
            # In 'principal' query mode, we have to search for each
            # group given in principalGroupsAttribute and, for each group,
            # query it's DN and get it's ID attribute
            try:
                for dn in user_entry[self.principalGroupsAttribute]:
                    res = self._search({}, base=dn, attrs=[auth.groupIdAttribute], queryType='group')
                    for _dn, entry in res:
                        groups.append(self.groupIdPrefix + entry[auth.groupIdAttribute][0])
            except:
                pass

        return groups

    def getPrincipalsForGroup(self, group_id):
        """Get group principals"""

        auth = self.authenticator
        if auth is None:
            return None
        principals = []
        internal_id = group_id[len(self.groupIdPrefix):]

        if self.queryMode == 'group':
            # In 'group' query mode, we have to:
            # - search for the group
            # - search for each principal in group's members attribute
            res = self._search({ auth.groupIdAttribute: internal_id },
                               attrs=[self.groupPrincipalsAttribute],
                               queryType='group')
            try:
                _dn, entry = res[0]
                for dn in entry[self.groupPrincipalsAttribute]:
                    res = self._search({ 'objectClass': '*' },
                                       base=dn,
                                       attrs=[auth.idAttribute],
                                       queryType='principal')
                    for _dn, entry in res:
                        principals.append(auth.principalIdPrefix + entry[auth.idAttribute][0])
            except:
                pass
        else:
            # In 'principal' mode, we only have to search for
            # principals based on their own 'memberOf' attribute
            res = self._search({ self.principalGroupsAttribute: internal_id },
                               attrs=[auth.idAttribute],
                               queryType='principal')
            for dn, entry in res:
                principals.append(auth.principalIdPrefix + entry[auth.idAttribute][0])

        return principals


    # private methods

    def _search(self, query={}, base=None, scope=None, attrs=None, queryType='group'):
        """Execute search through LDAP authenticator"""

        auth = self.authenticator
        if auth is None:
            return None

        # connect
        da = auth.getLDAPAdapter()
        if da is None:
            return []
        try:
            conn = da.connect()
        except ServerDown:
            return []

        # build query filter
        if not base:
            base = (queryType == 'group') and auth.groupsSearchBase or auth.searchBase
        if not scope:
            scope = (queryType == 'group') and auth.groupsSearchScope or auth.searchScope
        filter_elems = []
        for key, value in query.items():
            if not value:
                continue
            filter_elems.append('(%s=%s)' % (key, value))
        if (queryType == 'group'):
            if self.groupRequiredClass:
                filter_elems.append('(objectClass=%s)' % self.groupRequiredClass)
        elif (queryType == 'principal'):
            if self.principalRequiredClass:
                filter_elems.append('(objectClass=%s)' % self.principalRequiredClass)
        filter = ''.join(filter_elems)
        if len(filter_elems) > 1:
            filter = '(&%s)' % filter
        if not filter:
            filter = '(objectClass=*)'

        # execute search
        try:
            res = conn.search(base, scope, filter=filter, attrs=attrs)
        except (NoSuchObject, LDAPError):
            return []
        else:
            return res

    def _getGroupInfoFromEntry(self, id, entry):
        return LDAPGroupInformation(self, id, entry[self.titleAttribute][0],
                                    self.descriptionAttribute and entry.get(self.descriptionAttribute, [''])[0] or '')


LDAP_CACHE_NAMESPACE = 'ztfy.ldap.groups'
LDAP_CACHE_MARKER = object()

@adapter(IAuthenticatedPrincipalCreated)
def setGroupsForPrincipal(event):
    """Set principal groups when it is created"""

    principal = event.principal
    if not IGroupAwarePrincipal.providedBy(principal):
        return

    auth = event.authentication
    cache = None
    groups = []
    principal_id = principal.id

    for name, plugin in auth.getAuthenticatorPlugins():
        if not ILDAPGroupsFolder.providedBy(plugin):
            continue

        prefix = auth.prefix + plugin.groupIdPrefix
        if principal_id.startswith(prefix) or not principal_id.startswith(plugin.authenticator.principalIdPrefix):
            continue

        if plugin.cacheProxyName:
            cache_proxy = queryUtility(ICacheProxyHandlerBase, plugin.cacheProxyName)
            if cache_proxy is not None:
                cache = cache_proxy.getCache()
                if cache is not None:
                    cached_groups = cache.query('%s::%s' % (LDAP_CACHE_NAMESPACE, name),
                                                principal_id, LDAP_CACHE_MARKER)
                    if cached_groups is not LDAP_CACHE_MARKER:
                        principal.groups.extend(cached_groups)
                        continue

        cached_groups = [ auth.prefix + p_id
                          for p_id in plugin.getGroupsForPrincipal(principal.id)]
        if cache is not None:
            cache.set('%s::%s' % (LDAP_CACHE_NAMESPACE, name), principal_id, cached_groups)
        groups.extend(cached_groups)

    principal.groups.extend(groups)
