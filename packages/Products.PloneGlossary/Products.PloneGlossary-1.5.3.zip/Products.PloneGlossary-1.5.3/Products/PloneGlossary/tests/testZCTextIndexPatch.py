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
Testing patch to ZCTextIndex
"""

from Products.PloneGlossary.tests import PloneGlossaryTestCase


class TestZCTextIndexPatch(PloneGlossaryTestCase.PloneGlossaryTestCase):

    def testDefaultConfig(self):

        #This test is here to prevent changing default behaviour by accident:
        # we don't want to release or commit with patching enabled.
        # That's defensive
        from Products.PloneGlossary.config import PATCH_ZCTextIndex
        from Products.PloneGlossary.config import INDEX_SEARCH_GLOSSARY

        self.assertEquals(PATCH_ZCTextIndex, False)
        self.assertEquals(INDEX_SEARCH_GLOSSARY, ('SearchableText',))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCTextIndexPatch))
    return suite
