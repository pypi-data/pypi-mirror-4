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
AT schemas for PloneGlossary content types
"""

__author__ = ''
__docformat__ = 'restructuredtext'

# Archetypes import
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RichWidget
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.PloneGlossary.utils import PloneGlossaryMessageFactory as _


# PloneGlossary schema
PloneGlossarySchema = ATContentTypeSchema.copy()
PloneGlossarySchema['description'].schemata = 'default'

finalizeATCTSchema(PloneGlossarySchema, folderish=True)

# PloneGlossaryDefinition schema
PloneGlossaryDefinitionSchema = ATContentTypeSchema.copy() + Schema((
    StringField(
        'title',
        required=True,
        searchable=True,
        default='',
        accessor='Title',
        widget=StringWidget(
            label=_(u'label_glossary_term', default=u"Term"),
            description=_(u'help_glossary_term',
                              default=u"Enter the term to be defined."),
            visible={'view': 'invisible'}),
        ),
    LinesField(
        'variants',
        required=False,
        searchable=True,
        default=(),
        widget=LinesWidget(
            label=_(u'label_glossary_variants', default=u"Variants"),
            description=_(
                u'help_glossary_variants',
                default=u"Enter the variants of the term, one per line."),
            visible={'view': 'invisible'}),
        ),
    TextField(
        'definition',
        required=True,
        searchable=True,
        default_content_type=zconf.ATDocument.default_content_type,
        default_output_type='text/x-html-safe',
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        widget=RichWidget(
            label=_(u'label_glossary_definition_text', default=u"Body text"),
            description=_(u'help_glossary_definition_text',
                          default=u"Enter the body text."),
            rows=25),
        ),

    ))

del PloneGlossaryDefinitionSchema['description']
finalizeATCTSchema(PloneGlossaryDefinitionSchema)

# Hide description. It is generated dynamically
#PloneGlossaryDefinitionSchema['description'].widget.visible = {'view' : '
#visible', 'edit' : 'invisible'}
