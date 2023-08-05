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
## along with this program; see the file LICENSE.txt. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id$
"""
Migrations from 1.2 to any
"""
__author__ = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from Products.CMFCore.utils import getToolByName
from Products.PloneGlossary.config import PLONEGLOSSARY_TOOL
from Products.PloneGlossary.utils import getSite, IfInstalled

safety_belt = IfInstalled()


@safety_belt
def synonymsSupportHandler(setuptool):
    """Adding support for synonyms"""

    for brain in findGlossaryBrains():
        glossary = brain.getObject()
        if glossary is None:
            continue
        glossary_catalog = glossary.getCatalog()
        if 'getVariants' not in glossary_catalog.indexes():
            glossary_catalog.addIndex('getVariants', 'KeywordIndex')
            glossary_catalog.manage_reindexIndex(ids=["getVariants"])
            glossary_catalog.addColumn("getVariants")
    return


def synonymsSupportChecker(setuptool):
    """Checking we have getVariant index in first glossary catalog found"""

    for brain in findGlossaryBrains():
        glossary = brain.getObject()
        if glossary is None:
            continue
        glossary_catalog = glossary.getCatalog()
        if 'getVariants' in glossary_catalog.indexes():
            return False
    return True


def findGlossaryBrains():
    portal = getSite()
    glossary_tool = getToolByName(portal, 'portal_glossary')
    glossary_metatypes = glossary_tool.getProperty('glossary_metatypes')
    catalog = getToolByName(portal, 'portal_catalog')
    return catalog.searchResults(meta_type=glossary_metatypes)


##
# -> 1.4.2
##

@safety_belt
def changeJSRegistryConditions(setuptool):
    """Change / simplify condition for JS registry.
    """
    runImportStep(setuptool, 'jsregistry')
    return


@safety_belt
def fixKupuSupport(setuptool):
    """Don't decorate Kupu specific areas
    """
    new_tags = set(['div#kupu-editor-text-config-escaped',
                     'div#kupu-editor-text-config'])
    pgtool = getSite()[PLONEGLOSSARY_TOOL]
    not_highlighted_tags = set(pgtool.getProperty('not_highlighted_tags'))
    if not new_tags <= not_highlighted_tags:
        not_highlighted_tags |= new_tags
        not_highlighted_tags = tuple(not_highlighted_tags)
        pgtool.manage_changeProperties(
            not_highlighted_tags=not_highlighted_tags)
    return


###
# Misc
###

def runImportStep(setuptool, step_id):
    setuptool.runImportStepFromProfile(
        'profile-Products.PloneGlossary:default',
        step_id, run_dependencies=False)
    return
