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

# $Id: portlet.py 54227 2007-11-20 17:44:37Z glenfant $
"""
Page views for PloneGlossary
"""
import string
import unicodedata
from zExceptions import Redirect
from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

try:
    from Products.CMFPlone import Batch
    Batch  # pyflakes
except ImportError:
    # Plone4.1 has moved Batch
    from Products.CMFPlone.PloneBatch import Batch

from Products.PloneGlossary.config import (
    PLONEGLOSSARY_TOOL,
    BATCH_SIZE,
    SITE_CHARSET
)


class GlossaryMainPage(BrowserView):

    def __init__(self, context, request):
        super(GlossaryMainPage, self).__init__(context, request)
        self.search_letter = request.get('search_letter', '')
        self.search_text = request.get('search_text')
        self.batch_start = request.get('b_start', 0)
        self.uid = context.UID()
        self.gtool = getToolByName(context, PLONEGLOSSARY_TOOL)

    def title(self):
        """Title of our glossary"""

        return self.context.title_or_id()

    def first_letters(self):
        """Users with non latin chars (cyrillic, arabic, ...) should override
        this with a better suited dataset."""

        out = []
        existing = self.gtool.getAbcedaire([self.uid])
        glossary_url = self.context.absolute_url()
        for letter in tuple(string.ascii_uppercase):
            letter_map = {
                'glyph': letter,
                'has_no_term': letter.lower() not in existing,
                'zoom_link': glossary_url + '?search_letter=' + letter.lower(),
                'css_class': letter.lower() == self.search_letter.lower() \
                             and 'selected' or None
                }
            out.append(letter_map)
        return out

    def has_results(self):
        """Something to show ?"""

        return len(self._list_results()) > 0

    def batch_results(self):
        """Wrap all results in a batch"""

        results = self._list_results()
        batch = Batch(results, BATCH_SIZE, int(self.batch_start), orphan=1)
        return batch

    @memoize
    def _list_results(self):
        """Terms list (brains) depending on the request"""

        gtool = self.gtool
        if self.search_letter:
            # User clicked a letter
            results = gtool.getAbcedaireBrains([self.uid],
                                               letters=[self.search_letter])
        elif self.search_text:
            # User searches for text
            results = gtool.searchResults([self.uid],
                                          SearchableText=self.search_text)
            # We redirect to the result if unique
            if len(results) == 1:
                target = results[0].getURL()
                raise Redirect(target)
        else:
            # Viewing all terms
            results = gtool.searchResults([self.uid])
        results = list(results)
        results.sort(lambda x, y: cmp(toLowerAscii(x.Title),
                                      toLowerAscii(y.Title)))
        return tuple(results)

    def result_features(self, result):
        """TAL friendly properties of each feature"""

        description = self.gtool.truncateDescription(result.Description)
        return {
            'url': result.getURL(),
            'title': result.Title or result.getId,
            'description': description.replace('\n', '<br />')
            }


def toLowerAscii(text):
    utext = text.decode(SITE_CHARSET, 'replace')
    ntext = unicodedata.normalize('NFKD', utext)
    atext = ntext.encode('ascii', 'ignore')
    atext = atext.lower()
    return atext
