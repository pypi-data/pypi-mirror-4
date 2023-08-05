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
PloneGlossary public interfaces (Zope 3 style)
"""

from zope.interface import Interface, Attribute


class IGlossaryTool(Interface):
    """Marker interface for tool
    """
    pass


class IPloneGlossary(Interface):
    """
    PloneGlossary container
    """
    definition_types = Attribute("""tuple of definitions content metatypes""")

    def getGlossaryDefinitions(self, terms):
        """Returns glossary definitions.
        Returns tuple of dictionnary title, text.
        Definition is based on catalog getText metadata."""

    def getGlossaryTerms():
        """Returns glossary terms title."""

    def getGlossaryTermItems():
        """Returns glossary terms in a specific structure

        Item:
        - path -> term path
        - id -> term id
        - title -> term title
        - description -> term description
        - url -> term url

         check security."""

    def getCatalog():
        """Returns catalog of glossary"""

    def rebuildCatalog():
        """Delete old catalog of glossary and build a new one"""


class IPloneGlossaryDefinition(Interface):
    """
    Plone Glossary definition
    """

    def indexObject():
        """Index object in portal catalog and glossary catalog"""

    def unindexObject():
        """Unindex object in portal catalog and glossary catalog"""

    def reindexObject(idxs=[]):
        """Reindex object in portal catalog and glossary catalog"""


class IOptionalHighLight(Interface):
    """Do we want to highlight terms in this object?
    """

    def do_highlight(default):
        """Highlight this object?

        When no preference can be found, return the default value.
        This should be optional
        """
