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
Specific catalog for PloneGlossary
"""

__author__ = 'Cyrille Lebeaupin <clebeaupin@ingeniweb.com'
__docformat__ = 'restructuredtext'

# Python imports
import re

# Zope imports
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.ZCatalog import ZCatalog

# Products imports
from Products.ZCTextIndex.PipelineFactory import element_factory
from Products.PloneGlossary.config import PLONEGLOSSARY_CATALOG, SITE_CHARSET
from Products.PloneGlossary.utils import encode_ascii


class args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


# We currently only support Latin normalizer and splitter
class LatinNormalizerAndSplitter:
    rx = re.compile(r"(?L)\w+")
    rxGlob = re.compile(r"(?L)\w+[\w*?]*")  # See globToWordIds() ab

    def _normalize(self, text):
        """Normalize text : returns an ascii text

        @param text: Text to normalize"""

        utext = text
        if type(text) != type(u''):  # Not unicode string
            utext = text.decode(SITE_CHARSET, "replace")
        return encode_ascii(utext)

    def process(self, lst):
        result = []
        for word in lst:
            norm_word = self._normalize(word)
            result.extend(self.rx.findall(norm_word))
        return result

    def processGlob(self, lst):
        result = []
        for word in lst:
            norm_word = self._normalize(word)
            result.extend(self.rxGlob.findall(norm_word))
        return result


try:
    element_factory.registerFactory(
        "Glossary Latin normalizer and splitter",
        "Glossary Latin normalizer and splitter",
        LatinNormalizerAndSplitter)
except ValueError:
    # in case the normalizer is already registered, ValueError is raised
    pass


class PloneGlossaryCatalog(ZCatalog):
    """Catalog for PloneGlossary"""

    id = PLONEGLOSSARY_CATALOG
    title = "Glossary Catalog"

    security = ClassSecurityInfo()

    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    security.declarePublic('enumerateIndexes')
    def enumerateIndexes(self):
        """Returns indexes used by catalog"""
        return (
                ('UID', 'FieldIndex'),
                ('id', 'FieldIndex'),
                ('Title', 'ZCTextIndex'),
                ('getVariants', 'KeywordIndex'),
                ('Description', 'ZCTextIndex'),
                )

    def __url(self, object):
        """Returns url of object"""
        return '/'.join(object.getPhysicalPath())

    security.declarePrivate('indexObject')
    def indexObject(self, object):
        '''Add to catalog.
        '''
        url = self.__url(object)
        self.catalog_object(object, url)

    security.declarePrivate('unindexObject')
    def unindexObject(self, object):
        '''Remove from catalog.
        '''
        url = self.__url(object)
        self.uncatalog_object(url)

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=[]):
        """Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        """

        url = self.__url(object)
        if idxs != []:
            # Filter out invalid indexes.
            valid_indexes = self._catalog.indexes.keys()
            idxs = [i for i in idxs if i in valid_indexes]
        self.catalog_object(object, url, idxs=idxs)

InitializeClass(PloneGlossaryCatalog)


def manage_addPloneGlossaryCatalog(self, REQUEST=None):
    """Add the glossary catalog
    """

    c = PloneGlossaryCatalog()
    self._setObject(c.getId(), c)

    cat = getattr(self, c.getId())

    # Add Lexicon
    cat.manage_addProduct['ZCTextIndex'].manage_addLexicon(
        'glossary_lexicon',
        elements=[
            args(group="Glossary Latin normalizer and splitter",
                 name="Glossary Latin normalizer and splitter"),
                 ]
                 )

    # Add indexes and metadatas
    for index_name, index_type in cat.enumerateIndexes():
        try:  # ugly try catch XXX FIXME
            if index_name not in cat.indexes():
                if index_type == 'ZCTextIndex':
                    extra = args(doc_attr=index_name,
                                 lexicon_id='glossary_lexicon',
                                 index_type='Okapi BM25 Rank')
                    cat.addIndex(index_name, index_type, extra=extra)
                else:
                    cat.addIndex(index_name, index_type)

            if not index_name in cat.schema():
                cat.addColumn(index_name)
        except:
            pass

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
