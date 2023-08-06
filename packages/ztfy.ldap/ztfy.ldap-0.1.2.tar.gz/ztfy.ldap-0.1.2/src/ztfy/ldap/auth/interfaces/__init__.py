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
import re

# import Zope3 interfaces
from zope.pluggableauth.interfaces import IPrincipalInfo

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Choice

# import local packages

from ztfy.ldap import _


class ILDAPPrincipalInfo(IPrincipalInfo):
    """LDAP principal marker interface"""


class ILDAPGroupInfo(ILDAPPrincipalInfo):
    """Marker interface for an LDAP group principal"""

    plugin = Attribute(_("LDAP groups folder authentication plug-in"))


class ILDAPGroupSearchSchema(Interface):
    """LDAP schema from groups searching"""

    uid = TextLine(title=u'uid',
                   required=False)

    cn = TextLine(title=u'cn',
                  required=False)


class ILDAPAuthenticationPlugin(Interface):
    """Marker interface for an LDAP authentication plug-in"""

    def principalInfo(self, id):
        """Get principal info"""


class ILDAPGroupsFolder(ILDAPAuthenticationPlugin):
    """LDAP GroupsFolder plug-in interface for Pluggable Authentication"""

    authenticatorName = Choice(title=_("LDAP authenticator name"),
                               description=_("Name of the LDAP authenticator plug-in used to authenticate users"),
                               vocabulary="LDAP authenticator names",
                               required=True)

    groupIdPrefix = TextLine(title=_("Group ID prefix"),
                             description=_("Prefix to add to all groups ids"),
                             required=True)

    titleAttribute = TextLine(title=_("Group title attribute"),
                              description=_("LDAP attribute used to identify group's title"),
                              constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                              required=True,
                              default=u'cn')

    descriptionAttribute = TextLine(title=_("Group description attribute"),
                                    description=_("LDAP attribute used to identify group's description"),
                                    constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                                    required=True,
                                    default=u'description')

    groupRequiredClass = TextLine(title=_("Group required class"),
                             description=_("LDAP class required on groups"),
                             constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                             required=True,
                             default=u'group')

    principalRequiredClass = TextLine(title=_("Principal required class"),
                                      description=_("LDAP class required on pincipals"),
                                      constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                                      required=True,
                                      default=u'person')

    queryMode = Choice(title=_("Group members query mode"),
                       description=_("Query mode used to find members of a group and groups of a principal"),
                       vocabulary="ZTFY LDAP groups query mode",
                       required=True,
                       default=u'group')

    groupPrincipalsAttribute = TextLine(title=_("Group principals attribute"),
                                        description=_("Name of LDAP's group attribute containing it's principals"),
                                        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                                        required=False,
                                        default=u'uniqueMember')

    groupModeQueryFilter = TextLine(title=_("'group' mode query filter"),
                                    description=_("LDAP query used to find principals and groups in 'group' mode"),
                                    required=False,
                                    default=u'uniqueMember=%(dn)s')

    principalGroupsAttribute = TextLine(title=_("Principal groups attribute"),
                                        description=_("Name of LDAP's principal attribute containing it's groups"),
                                        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                                        required=False,
                                        default=u'memberOf')

    principalModeQueryFilter = TextLine(title=_("'principal' mode query filter"),
                                        description=_("LDAP query used to find principals and groups in 'principal' mode"),
                                        required=False,
                                        default=u'memberOf=%(dn)s')

    cacheProxyName = Choice(title=_("Cache proxy name"),
                            description=_("Use given cache to store principals groups"),
                            required=False,
                            vocabulary='ZTFY cache proxy handlers')

    def getGroupsForPrincipal(self, principal_id):
        """Get list of groups for given principal"""

    def getPrincipalsForGroup(self, group_id):
        """Get list of principals for given group"""


class ILDAPGroupsMailInfo(Interface):
    """LDAP GroupsFolder mail info extension"""

    mailMode = Choice(title=_("Group mail mode"),
                      description=_("Mail mode defines how a mail can be send to group members"),
                      vocabulary="ZTFY LDAP groups mail mode",
                      required=True,
                      default='none')

    dnReplaceExpression = TextLine(title=_("DN replace expression"),
                                   description=_("In 'redirect' mode, enter DN source and target value parts, separated by a '|'"),
                                   constraint=re.compile("[a-zA-Z0-9-=,]+|[a-zA-Z0-9-=,]+").match,
                                   default=u'ou=access|ou=lists')

    mailAttribute = TextLine(title=_("Group mail attribute"),
                             description=_("Name of LDAP's group attribute containing mail address"),
                             constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
                             required=True,
                             default=u'mail')
