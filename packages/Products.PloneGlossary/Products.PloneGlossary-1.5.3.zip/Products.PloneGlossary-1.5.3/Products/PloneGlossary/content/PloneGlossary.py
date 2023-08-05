# -*- coding: utf-8 -*-
##
## Copyright (C) 2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id$
"""
The Glossary content type
"""
__author__ = 'Cyrille Lebeaupin <clebeaupin@ingeniweb.com>'
__docformat__ = 'restructuredtext'


# Python imports

# Zope imports
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from zope.component import getMultiAdapter

# CMF imports
from Products.CMFCore import permissions

# Archetypes imports
try:
    from Products.LinguaPlone.public import registerType
    registerType  # pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import registerType

from Products.ATContentTypes.content.base import ATCTFolder

# Products imports
from Products.PloneGlossary.config import PROJECTNAME, PLONEGLOSSARY_CATALOG
from Products.PloneGlossary.PloneGlossaryCatalog import \
    manage_addPloneGlossaryCatalog
from Products.PloneGlossary.content.schemata import \
    PloneGlossarySchema as schema
from Products.PloneGlossary.interfaces import IPloneGlossary


class PloneGlossary(ATCTFolder):
    """PloneGlossary container"""

    implements(IPloneGlossary)

    definition_types = ('PloneGlossaryDefinition',)
    schema = schema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'getGlossaryDefinitions')
    def getGlossaryDefinitions(self, terms):
        """Returns glossary definitions.
        Returns tuple of dictionnary title, text.
        Definition is based on catalog getText metadata."""

        # Get glossary catalog
        title_request = ' OR '.join(['"%s"' % x for x in terms if len(x) > 0])
        if not title_request:
            return []

        # Get # Get glossary related term brains
        cat = self.getCatalog()
        brains = cat(Title=title_request)
        if not brains:
            return []

        # Build definitions
        definitions = []
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        mtool = plone_tools.membership()
        # mtool = getToolByName(self, 'portal_membership')
        check_perm = mtool.checkPermission
        for brain in brains:
            # Check view permission
            # FIXME: Maybe add allowed roles and user index in glossary catalog
            obj = brain.getObject()
            has_view_permission = (
                check_perm(permissions.View, obj) and
                check_perm(permissions.AccessContentsInformation, obj))
            if not has_view_permission:
                continue

            # Make sure the title of glossary term is not empty
            title = brain.Title
            if not title:
                continue

            # Build definition
            item = {
                'id': brain.id,
                'title': brain.Title,
                'variants': brain.getVariants,
                'description': brain.Description,
                'url': brain.getURL()}
            definitions.append(item)

        return tuple(definitions)

    security.declareProtected(permissions.View, 'getGlossaryTerms')
    def getGlossaryTerms(self):
        """Returns glossary terms title."""

        # Get glossary term titles
        return [x['title'] for x in self.getGlossaryTermItems()]

    # Make it private because this method doesn't check term security
    def _getGlossaryTermItems(self):
        """Returns glossary terms in a specific structure

        Item:
        - path -> term path
        - id -> term id
        - title -> term title
        - description -> term description
        - url -> term url
        """

        # Returns all glossary term brains
        cat = self.getCatalog()
        brains = cat(REQUEST={})

        # Build items
        items = []
        for brain in brains:
            items.append({'path': brain.getPath(),
                          'id': brain.id,
                          'title': brain.Title,
                          'variants': brain.getVariants,
                          'description': brain.Description,
                          'url': brain.getURL()})
        return items

    security.declarePublic('getGlossaryTermItems')
    def getGlossaryTermItems(self):
        """Returns the same list as _getGlossaryTermItems but check security.
        """

        # Get glossaries term items
        not_secured_term_items = self._getGlossaryTermItems()

        # Walk into each catalog of glossaries and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
        # utool = getToolByName(self, 'portal_url')
        portal_object = utool.getPortalObject()
        term_items = []
        for item in not_secured_term_items:
            path = item['path']
            try:
                portal_object.restrictedTraverse(path)
            except:
                continue
            term_items.append(item)
        return term_items

    security.declarePublic('getCatalog')
    def getCatalog(self):
        """Returns catalog of glossary"""

        if not hasattr(self, PLONEGLOSSARY_CATALOG):
            # Build catalog if it doesn't exist
            catalog = self._initCatalog()
        else:
            catalog = getattr(self, PLONEGLOSSARY_CATALOG)

        return catalog

    def _initCatalog(self):
        """Add Glossary catalog"""

        if not hasattr(self, PLONEGLOSSARY_CATALOG):
            add_catalog = manage_addPloneGlossaryCatalog
            add_catalog(self)

        catalog = getattr(self, PLONEGLOSSARY_CATALOG)
        catalog.manage_reindexIndex()
        return catalog

    security.declareProtected(permissions.ManagePortal, 'rebuildCatalog')
    def rebuildCatalog(self):
        """don't Delete old catalog of glossary and build a new one
        but only clear it, for tests to pass
        """

        if not hasattr(self, PLONEGLOSSARY_CATALOG):
            # Add a new catalog if not exists
            cat = self._initCatalog()
        else:
            cat = self.getCatalog()

        # clear catalog
        cat.manage_catalogClear()

        # Reindex glossary definitions
        for obj in self.objectValues():
            if obj.portal_type in self.definition_types:
                cat.catalog_object(obj)

registerType(PloneGlossary, PROJECTNAME)


###
## Events handlers
###

def glossaryAdded(glossary, event):
    """A glossary has been added"""

    container = event.newParent
    # FIXME: Fix this when AT don't need manage_afterAdd any more
    super(glossary.__class__, glossary).manage_afterAdd(glossary, container)
    glossary._initCatalog()
    return


def glossaryMoved(glossary, event):
    """A glossary has been moved or renamed"""

    glossary.rebuildCatalog()
    return
