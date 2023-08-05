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
The PloneGlossary package
"""
__author__ = ''
__docformat__ = 'restructuredtext'

# Python imports
import os
import sys

# CMF imports
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory

# Archetypes imports
from Products.Archetypes.public import process_types, listTypes

# Products imports
from Products.PloneGlossary.config import SKINS_DIR, GLOBALS, PROJECTNAME
from Products.PloneGlossary.PloneGlossaryTool import PloneGlossaryTool
from Products.PloneGlossary import content as content_module

# BBB: Make migrations easier.
sys.modules['Products.PloneGlossary.types'] = content_module

registerDirectory(SKINS_DIR, GLOBALS)


def initialize(context):

    # import at initialize: this let a chance to 3rd party products to change
    # config before deciding to patch
    from Products.PloneGlossary import patches
    patches  # pyflakes
    from Products.PloneGlossary.permissions import add_permissions

    # used by test framework
    if 'ZOPETESTCASE' in os.environ:
        import examples
        examples  # pyflakes

    # Import types
    listOfTypes = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(listOfTypes,
                                                      PROJECTNAME)

    for content_type, constructor in zip(content_types, constructors):
        kind = "%s: %s" % (PROJECTNAME, content_type.__name__)
        ContentInit(
            kind,
            content_types=(content_type, ),
            permission=add_permissions[content_type.__name__],
            extra_constructors=(constructor, ),
            fti=ftis,
        ).initialize(context)

    # Import tool
    ToolInit(
        '%s Tool' % PROJECTNAME,
        tools=(PloneGlossaryTool,),
        icon='tool.gif').initialize(context)
