# -*- coding: utf-8 -*-
##
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
"""
This module contains permissions used in PloneGlossary product
"""

__docformat__ = 'restructuredtext'

try:
    from plone.app.upgrade import v40
    v40  # pyflakes
    HAS_PLONE4 = True
except ImportError:
    HAS_PLONE4 = False
# CMF imports
from Products.CMFCore import permissions

# Add permission
AddGlossary = 'PloneGlossary: Add Glossary'

if HAS_PLONE4:
    ADDROLES = ('Manager', 'Owner', 'Contributor')
else:
    ADDROLES = ('Manager', 'Owner')

permissions.setDefaultRoles(AddGlossary, ADDROLES)

AddDefinition = 'PloneGlossary: Add Definition'
permissions.setDefaultRoles(AddDefinition, ADDROLES)

add_permissions = {
    'PloneGlossary': AddGlossary,
    'PloneGlossaryDefinition': AddDefinition,
    # Useful for unit tests only
    'ExampleGlossary': AddGlossary,
    'ExampleGlossaryDefinition': AddDefinition
    }
