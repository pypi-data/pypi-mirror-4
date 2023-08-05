## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id$
"""
GenericSetup adapter for PloneGlosaryTool
"""

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.utils import getToolByName

from Products.PloneGlossary.utils import LOG
from Products.PloneGlossary.config import PROJECTNAME, PLONEGLOSSARY_TOOL
from Products.PloneGlossary.interfaces import IGlossaryTool


class ToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """
    XML import/export for IGlossaryTool
    """

    __used_for__ = IGlossaryTool

    _LOGGER_ID = PROJECTNAME

    name = 'glossary'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())

        self._logger.info('Glossary tool exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)

        self._logger.info('Glossary tool imported.')


def importGlossaryTool(context):
    """Import glossary tool settings from an XML file.
    """
    if context.readDataFile('ploneglossary.txt') is None:
        # GS sometimes sucks. Without this, GS will always try to run this
        # whatever product is imported
        return

    site = context.getSite()
    tool = getToolByName(site, PLONEGLOSSARY_TOOL)

    importObjects(tool, '', context)


def exportGlossaryTool(context):
    """Export glossary tool settings as an XML file.
    """
    site = context.getSite()
    tool = getToolByName(site, PLONEGLOSSARY_TOOL, None)
    if tool is None:
        LOG.info('Nothing to export.')
        return

    exportObjects(tool, '', context)
