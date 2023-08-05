##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Setting bases for local sites.

$Id: base.py 97499 2009-03-04 23:39:58Z nadako $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component
import zope.schema
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.formlib import form
from zope.security.proxy import removeSecurityProxy
from zope.site.interfaces import ILocalSiteManager

BASENAME = _('-- Global Base Registry --')
PARENTNAME = _('-- Parent Local Registry --')

class BaseComponentsVocabulary(zope.schema.vocabulary.SimpleVocabulary):
    """A vocabulary for ``IComponents`` utilities."""

    zope.interface.classProvides(zope.schema.interfaces.IVocabularyFactory)

    def __init__(self, context):
        terms = []
        utils = set()
        
        # add available registry utilities
        for name, util in \
            zope.component.getUtilitiesFor(
                zope.component.interfaces.IComponents, context):
            
            terms.append(zope.schema.vocabulary.SimpleTerm(util, name))
            utils.add(util)

        # add location parent registry if any
        lsm = [removeSecurityProxy(sm) for sm in context.__bases__ \
               if sm not in utils and ILocalSiteManager.providedBy(sm)]
        if lsm:
            terms.append(zope.schema.vocabulary.SimpleTerm(lsm[0], PARENTNAME))

        # add the base registry
        terms.append(zope.schema.vocabulary.SimpleTerm(zope.component.globalregistry.base, BASENAME))
        
        super(BaseComponentsVocabulary, self).__init__(terms)

class IComponentsBases(zope.interface.Interface):
    """An interface describing the bases API of the IComponents object."""

    __bases__ = zope.schema.List(
        title=_('Bases'),
        description=_('The base components registires of this registry.'),
        value_type=zope.schema.Choice(vocabulary='Base Components'),
        required=True)


class SetBasesPage(form.EditForm):
    """A page to set the bases of a local site manager"""
    form_fields = form.FormFields(IComponentsBases)

