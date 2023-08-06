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

# import Zope3 interfaces
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ldappas.interfaces import ILDAPAuthentication

# import Zope3 packages
from zope.component import adapter
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.i18n import translate
from zope.interface import classProvides, alsoProvides
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# import local packages
from ztfy.utils.request import queryRequest

from ztfy.ldap import _
from zope.pluggableauth.interfaces import IFoundPrincipalCreated
from ztfy.ldap.auth.interfaces import ILDAPPrincipalInfo, ILDAPGroupInfo



class LDAPAuthenticatorVocabulary(UtilityVocabulary):

    classProvides(IVocabularyFactory)

    interface = ILDAPAuthentication
    nameOnly = True



QUERY_MODES = {
               u'group': _("Use group attribute containing it's members list"),
               u'principal': _("Use principal attribute containing it's groups list")
              }

class QueryModesVocabulary(SimpleVocabulary):
    """Query modes vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, *args, **kw):
        request = queryRequest()
        terms = [SimpleTerm(v, title=translate(t, context=request)) for v, t in QUERY_MODES.iteritems()]
        super(QueryModesVocabulary, self).__init__(terms)


GROUP_MAIL_MODES = {
                    u'none': _("None (only use members own mail address)"),
                    u'internal': _("Use group internal attribute"),
                    u'redirect': _("Use another group internal attribute")
                   }

class GroupMailModesVocabulary(SimpleVocabulary):
    """Groups mail modes vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, *args, **kw):
        request = queryRequest()
        terms = [SimpleTerm(v, title=translate(t, context=request)) for v, t in GROUP_MAIL_MODES.iteritems()]
        terms.sort(key=lambda x: x.title)
        super(GroupMailModesVocabulary, self).__init__(terms)


@adapter(IFoundPrincipalCreated)
def createLDAPPrincipal(event):
    if ILDAPGroupInfo.providedBy(event.info):
        alsoProvides(event.principal, ILDAPGroupInfo)
    elif ILDAPPrincipalInfo.providedBy(event.info):
        alsoProvides(event.principal, ILDAPPrincipalInfo)
