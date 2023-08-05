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
Subclasses for unit tests or demo.
"""

from zope.interface import implements

# Archetypes imports
try:
    from Products.LinguaPlone.public import registerType
    registerType  # pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import registerType


from Products.PloneGlossary.content.PloneGlossary import PloneGlossary
from Products.PloneGlossary.content.PloneGlossaryDefinition import \
    PloneGlossaryDefinition
from Products.PloneGlossary.interfaces import (IPloneGlossary,
                                               IPloneGlossaryDefinition)

from Products.PloneGlossary.config import PROJECTNAME

ExampleGlossarySchema = PloneGlossary.schema.copy()


class ExampleGlossary(PloneGlossary):
    """ExampleGlossary"""

    implements(IPloneGlossary)

    definition_types = ('ExampleGlossaryDefinition',)

    meta_type = 'ExampleGlossary'
    schema = ExampleGlossarySchema


ExampleGlossaryDefinitionSchema = PloneGlossaryDefinition.schema.copy()


class ExampleGlossaryDefinition(PloneGlossaryDefinition):
    """ExamplePloneGlossaryDefinition"""

    implements(IPloneGlossaryDefinition)

    meta_type = 'ExampleGlossaryDefinition'
    schema = ExampleGlossaryDefinitionSchema

registerType(ExampleGlossary, PROJECTNAME)
registerType(ExampleGlossaryDefinition, PROJECTNAME)
