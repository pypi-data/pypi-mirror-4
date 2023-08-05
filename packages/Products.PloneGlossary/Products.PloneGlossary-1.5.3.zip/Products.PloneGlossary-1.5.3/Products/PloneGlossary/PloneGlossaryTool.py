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
Tool
"""

__author__ = ''
__docformat__ = 'restructuredtext'

import logging

# Zope imports
from zope.interface import implements
from zope.component import getMultiAdapter
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Acquisition import aq_base
from ZODB.POSException import ConflictError

try:
    from zope.component.hooks import getSite
    getSite  # pyflakes
except ImportError:
    # BBB for Plone < 4.0
    from zope.app.component.hooks import getSite

# CMF imports
from Products.CMFCore.utils import UniqueObject, getToolByName

# Plone imports
from plone.memoize.request import memoize_diy_request
from plone.i18n.normalizer.base import baseNormalize

# PloneGlossary imports
from Products.PloneGlossary.config import PLONEGLOSSARY_TOOL, SITE_CHARSET
from Products.PloneGlossary.utils import (
    text2words, find_word, escape_special_chars, encode_ascii)
from interfaces import IGlossaryTool, IOptionalHighLight

logger = logging.getLogger('Products.PloneGlossary')


class PloneGlossaryTool(PropertyManager, UniqueObject, SimpleItem):
    """Tool for PloneGlossary"""
    implements(IGlossaryTool)

    plone_tool = 1
    id = PLONEGLOSSARY_TOOL
    title = 'PloneGlossaryTool'
    meta_type = 'PloneGlossaryTool'

    _properties = (
        {'id': 'title',
         'type': 'string',
         'mode': 'w'},
        {'id': 'highlight_content',
         'type': 'boolean',
         'mode': 'w'},
        {'id': 'use_general_glossaries',
         'type': 'boolean',
         'mode': 'w'},
        {'id': 'general_glossary_uids',
         'type': 'multiple selection',
         'mode': 'w',
         'select_variable': 'getGlossaryUIDs'},
        {'id': 'allowed_portal_types',
         'type': 'multiple selection',
         'mode': 'w',
         'select_variable': 'getAvailablePortalTypes'},
        {'id': 'description_length',
         'type': 'int',
         'mode': 'w'},
        {'id': 'description_ellipsis',
         'type': 'string',
         'mode': 'w'},
        {'id': 'not_highlighted_tags',
         'type': 'lines',
         'mode': 'w'},
        {'id': 'available_glossary_metatypes',
         'type': 'lines',
         'mode': 'w'},
        {'id': 'glossary_metatypes',
         'type': 'multiple selection', 'mode': 'w',
         'select_variable': 'getAvailableGlossaryMetaTypes'},
        )

    highlight_content = True
    use_general_glossaries = True
    general_glossary_uids = []
    allowed_portal_types = ['PloneGlossaryDefinition']
    description_length = 0
    description_ellipsis = '..'
    not_highlighted_tags = [
        'a', 'h1', 'input', 'textarea', 'div#kupu-editor-text-config-escaped',
        'div#kupu-editor-text-config'
        ]
    available_glossary_metatypes = ()
    glossary_metatypes = ['PloneGlossary']

    _actions = ()

    manage_options = PropertyManager.manage_options + SimpleItem.manage_options

    security = ClassSecurityInfo()

    security.declarePublic('getAvailablePortalTypes')
    def getAvailablePortalTypes(self):
        """Returns available portal types"""

        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        portal_types = plone_tools.types()
        return portal_types.listContentTypes()

    security.declarePublic('getAvailableGlossaryMetaTypes')
    def getAvailableGlossaryMetaTypes(self):
        """
        Returns available glossary portal types
        """
        return self.available_glossary_metatypes

    security.declarePublic('getAllowedPortalTypes')
    def getAllowedPortalTypes(self):
        """Returns allowed portal types.
        Allowed portal types can be highlighted."""

        return self.allowed_portal_types

    security.declarePublic('getUseGeneralGlossaries')
    def getUseGeneralGlossaries(self):
        """Returns use_general_glossaries
        """
        return self.use_general_glossaries

    security.declarePublic('showPortlet')
    def showPortlet(self):
        """Returns true if you want to show glosssary portlet"""

        return True
        #return self.show_portlet

    security.declarePublic('highlightContent')
    def highlightContent(self, obj):
        """Returns true if content must be highlighted"""

        portal_type = obj.getTypeInfo().getId()
        allowed_portal_types = self.getAllowedPortalTypes()

        if allowed_portal_types and portal_type not in allowed_portal_types:
            return False

        # Check for an adapter on the object and see if this wants
        # highlighting.
        optional = IOptionalHighLight(obj, None)
        if optional is not None:
            return optional.do_highlight(default=self.highlight_content)

        return self.highlight_content

    security.declarePublic('getUsedGlossaryUIDs')
    def getUsedGlossaryUIDs(self, obj):
        """Helper method for the portlet Page Template. Fetches the general
           or local glossary uids depending on the settings in the glossary
           tool.
        """
        if self.getUseGeneralGlossaries():
            return self.getGeneralGlossaryUIDs()
        else:
            return self.getLocalGlossaryUIDs(obj)

    security.declarePublic('getLocalGlossaryUIDs')
    def getLocalGlossaryUIDs(self, context):
        """Returns glossary UIDs used to highlight content
        in the context of the current object. This method traverses upwards
        in the navigational tree in search for the neares glossary.
        This neares glossary is then returned
        """
        portal_catalog = getToolByName(context, 'portal_catalog')

        context = context.aq_inner
        siteroot = getSite()
        glossaries = []
        glossary_metatypes = self.glossary_metatypes

        while True:
            query = {
                'portal_type': glossary_metatypes,
                'path': "/".join(context.getPhysicalPath()),
            }

            brains = portal_catalog(query)
            if brains:
                glossaries.extend([x.UID for x in brains])
                break

            # quit after siteroot
            if context == siteroot:
                break

            context = context.aq_parent

        return glossaries

    security.declarePublic('getGeneralGlossaryUIDs')
    def getGeneralGlossaryUIDs(self):
        """Returns glossary UIDs used to highlight content"""
        if self.general_glossary_uids:
            return self.general_glossary_uids
        else:
            return self.getGlossaryUIDs()

    security.declarePublic('getGeneralGlossaries')
    def getGeneralGlossaries(self):
        """Returns glossaries used to highlight content"""
        general_glossary_uids = self.getGeneralGlossaryUIDs()
        return self.getGlossaries(general_glossary_uids)

    security.declarePublic('getGlossaryUIDs')
    def getGlossaryUIDs(self):
        """Returns glossary UIDs defined on portal"""

        uid_cat = getToolByName(self, 'uid_catalog')
        brains = uid_cat(portal_type=self.glossary_metatypes)
        return tuple([x.UID for x in brains])

    security.declarePublic('getGlossaries')
    def getGlossaries(self, glossary_uids=None):
        """Returns glossaries defined on portal"""

        cat = getToolByName(self, 'portal_catalog')
        query = {}
        query['portal_type'] = self.glossary_metatypes
        if glossary_uids is not None:
            query['UID'] = glossary_uids
        brains = cat(**query)
        glossaries = [_.getObject() for _ in brains]
        return tuple([_ for _ in glossaries if _])

    # Make it private because this method doesn't check term security
    def _getGlossaryTermItems(self, glossary_uids):
        """Returns glossary terms as a list of dictionaries

        Item:
        - path -> term path
        - id -> term id
        - title -> term title
        - variants -> term variants
        - description -> term description
        - url -> term url

        @param glossary_uids: uids of glossary where we get terms
        """

        # Get glossaries
        glossaries = self.getGlossaries(glossary_uids)
        if not glossaries:
            return []

        # Get items
        items = []
        for glossary in glossaries:
            new_items = glossary._getGlossaryTermItems()
            items.extend(new_items)
        return tuple(items)

    security.declarePublic('getGlossaryTermItems')
    def getGlossaryTermItems(self, glossary_uids):
        """Returns the same list as _getGlossaryTermItems but check security.

        @param glossary_uids: Uids of glossary where we get term items"""

        # Get glossaries term items
        not_secured_term_items = self._getGlossaryTermItems(glossary_uids)

        # Walk into each catalog of glossaries and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
        portal_object = utool.getPortalObject()
        term_items = []
        for item in not_secured_term_items:
            path = item['path']
            try:
                portal_object.restrictedTraverse(path)
            except:
                continue
            term_items.append(item)
        return term_items

    security.declarePublic('getGlossaryTerms')
    def getGlossaryTerms(self, glossary_uids):
        """Returns term titles stored in glossaries.

        @param glossary_uids: Uids of glossary where we get term items"""

        # Get glossaries term items
        term_items = self.getGlossaryTermItems(glossary_uids)

        # Returns titles
        return [x['title'] for x in term_items]

    def _getObjectText(self, obj):
        """Returns all text of an object.

        If object is an AT content, get schema and returns all text fields.
        Otherwise returns SearchableText.

        @param obj: Content to analyse"""

        text = ''
        if hasattr(aq_base(obj), 'Schema'):
            schema = obj.Schema()
            data = []

            # Loop on fields
            for field in schema.fields():
                if field.type in ('string', 'text',):
                    method = field.getAccessor(obj)

                    if method is None:
                        continue

                    # Get text/plain content
                    try:
                        datum = method(mimetype="text/plain")
                    except TypeError:
                        # retry in case typeerror was raised because
                        # accessor doesn't handle the mimetype
                        # argument
                        try:
                            datum = method()
                        except ConflictError:
                            raise
                        except:
                            continue

                    # Make sure value is a string
                    if type(datum) == type(''):
                        data.append(datum)
            text = ' '.join(data)
        elif hasattr(aq_base(obj), 'SearchableText'):
            text = obj.SearchableText()

        return text

    def _getTextRelatedTermItems(self, text, glossary_term_items,
                                 excluded_terms=()):
        """
        @param text: charset encoded text
        @param excluded_terms: charset encoded terms to exclude from search
        """
        if isinstance(text, unicode):
            utext = text
        else:
            utext = text.decode(SITE_CHARSET, "replace")
        usplitted_text_terms = self._split(utext)
        atext = encode_ascii(utext)

        aexcluded_terms = [encode_ascii(t.decode(SITE_CHARSET, "replace"))
                          for t in excluded_terms]

        result = []

        # Search glossary terms in text
        analyzed_terms = []
        for item in glossary_term_items:
            # Take into account the word and its variants
            terms = []
            item_title = item['title']
            item_variants = item['variants']

            if type(item_title) == type(''):
                terms.append(item_title)
            if type(item_variants) in (type([]), type(()), ):
                terms.extend(item_variants)

            # Loop on glossary terms and intersect with object terms
            for term in terms:
                if term in analyzed_terms:
                    continue

                # Analyze term
                analyzed_terms.append(term)
                uterm = term.decode(SITE_CHARSET, "replace")
                aterm = encode_ascii(uterm)
                if aterm in aexcluded_terms:
                    continue

                # Search the word in the text
                found_pos = find_word(aterm, atext)
                if not found_pos:
                    continue

                # Extract terms from obj text
                term_length = len(aterm)
                text_terms = []
                for pos in found_pos:
                    utext_term = utext[pos:(pos + term_length)]

                    # FIX ME: Workaround for composed words. Works in 99%
                    # Check the word is not a subword but a real word
                    # composing the text.
                    if not [x for x in self._split(utext_term)
                            if x in usplitted_text_terms]:
                        continue

                    # Encode the term and make sure there are no doublons
                    text_term = utext_term.encode(SITE_CHARSET, "replace")
                    if text_term in text_terms:
                        continue
                    text_terms.append(text_term)

                if not text_terms:
                    continue

                # Append object term item
                new_item = item.copy()
                new_item['terms'] = text_terms
                result.append(new_item)

        return result

    # Make it private because this method doesn't check term security
    def _getObjectRelatedTermItems(self, obj, glossary_term_items):
        """Returns object terms in a specific structure

        Item:
        - terms -> object terms
        - path -> term path
        - id -> term id
        - title -> term title
        - variants -> term variants
        - description -> term description
        - url -> term url

        @param obj: object to analyse

        @param glossary_term_items: Glossary term items to check in
            the object text

        Variables starting with a are supposed to be in ASCII

        Variables starting with u are supposed to be in Unicode
        """

        # Get obj properties
        ptype = obj.portal_type
        if callable(obj.title_or_id):
            title = obj.title_or_id()
        else:
            title = obj.title_or_id

        text = self._getObjectText(obj)

        # Words to remove from terms to avoid recursion
        # For example, on a glossary definition itself, it makes no sense to
        # underline the defined word.
        removed_words = ()
        if ptype in ('PloneGlossaryDefinition',):
            removed_words = (title,)

        return self._getTextRelatedTermItems(text, glossary_term_items,
                                             removed_words,)

    security.declarePublic('getObjectRelatedTermItems')
    def getObjectRelatedTermItems(self, obj, glossary_term_items,
                                  alpha_sort=False):
        """Returns the same list as _getObjectRelatedTermItems but
        check security.

        @param obj: object to analyse

        @param glossary_term_items: Glossary term items to check in
        the object text

        @param alpha_sort: if True, returned items are sorted by title, asc
        """

        # Get glossaries term items
        not_secured_term_items = self._getObjectRelatedTermItems(
            obj, glossary_term_items)

        # Walk into each catalog of glossaries and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
        portal_object = utool.getPortalObject()
        term_items = []
        for item in not_secured_term_items:
            path = item['path']
            try:
                obj = portal_object.restrictedTraverse(path)
            except:
                continue
            term_items.append(item)

        if alpha_sort:
            def glossary_cmp(o1, o2):
                return cmp(o1.get('title', ''), o2.get('title', ''))
            term_items.sort(glossary_cmp)

        return term_items

    security.declarePublic('getObjectRelatedTerms')
    def getObjectRelatedTerms(self, obj, glossary_uids, alpha_sort=False):
        """Returns glossary term titles found in object

        @param obj: Content to analyse and extract related glossary terms
        @param glossary_uids: if None tool will search all glossaries
        @param alpha_sort: if True, returned items are sorted by title, asc
        """

        # Get term definitions found in obj
        definitions = self.getObjectRelatedDefinitions(obj, glossary_uids,
                                                       alpha_sort=False)

        # Returns titles
        return [x['title'] for x in definitions]

    security.declarePublic('getObjectRelatedDefinitions')
    def getObjectRelatedDefinitions(self, obj, glossary_uids,
                                    alpha_sort=False):
        """Returns object term definitions get from glossaries.

        definition:
        - terms -> exact words in obj text
        - id -> term id
        - path -> term path
        - title -> term title
        - variants -> term variants
        - description -> term definitions
        - url -> term url

        @param obj: Content to analyse and extract related glossary terms
        @param glossary_uids: if None tool will search all glossaries
        @param alpha_sort: if True, returned items are sorted by title, asc
        """

        # Get glossary term items from the glossary
        # All terms are loaded in the memory as a list of dictionaries

        if not glossary_uids:
            return []

        glossary_term_items = self._getGlossaryTermItems(glossary_uids)

        marked_definitions = []
        urls = {}
        # Search related definitions in glossary definitions
        for definition in self.getObjectRelatedTermItems(
                obj, glossary_term_items, alpha_sort):
            if definition['url'] in urls:
                # The glossary item is already going to be shown
                definition['show'] = 0
            else:
                # The glossary item is going to be shown
                urls[definition['url']] = 1
                definition['show'] = 1
            marked_definitions.append(definition)
        return marked_definitions

    security.declarePublic('getDefinitionsForUI')
    @memoize_diy_request(arg=2)
    def getDefinitionsForUI(self, context, request):
        """Provides UI friendly definitions for the context item"""

        # LOG.debug("Running PloneGlossaryTool.getDefinitionsForUi")
        glossary_uids = self.getUsedGlossaryUIDs(context)
        if len(glossary_uids) == 0:
            glossary_uids = None
        # ensure that terms are sorted in descending term length in order to match
        # terms with the same prefix properly (longest matches first) (ajung)
        defs = self.getObjectRelatedDefinitions(context, glossary_uids)
        defs.sort(lambda t1,t2: -cmp(len(t1['terms'][0]), len(t2['terms'][0])))
        return defs

    security.declarePublic('searchResults')
    def searchResults(self, glossary_uids, **search_args):
        """Returns brains from glossaries.
        glossary_uids: UIDs of glossaries where to search.
        search_args: Use index of portal_catalog."""

        # Get path of glossaries
        query = dict(search_args)
        glossaries = self.getGlossaries(glossary_uids)
        query['path'] = ['/'.join(x.getPhysicalPath()) for x in glossaries]
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        ctool = plone_tools.catalog()
        query['portal_type'] = self._getDefinitionsMetaTypes(glossaries)
        logger.debug(query)
        return ctool(**query)

    def _getDefinitionsMetaTypes(self, glossaries):
        """
        get glossary definitions metatypes using glossaries list
        """
        metatypes = []
        for glossary in glossaries:
            glossary_def_mts = [deftype \
                                for deftype in glossary.definition_types\
                                if deftype not in metatypes]
            metatypes.extend(glossary_def_mts)

        return metatypes

    security.declarePublic('getAsciiLetters')
    def getAsciiLetters(self):
        """Returns list of ascii letters in lower case"""

        return tuple([chr(x) for x in range(97, 123)])

    security.declarePublic('getFirstLetter')
    def getFirstLetter(self, term):
        """ returns first letter """
        if isinstance(term, unicode):
            letter = term[0:1]
            return baseNormalize(letter)
        else:
            try:
                uterm = term.decode(SITE_CHARSET)
                letter = baseNormalize(uterm[0:1]).encode(SITE_CHARSET)
                return letter
            except UnicodeDecodeError:
                letter = term[0:1].decode()  # use python default encoding
                return baseNormalize(letter)

    security.declarePublic('getAbcedaire')
    def getAbcedaire(self, glossary_uids):
        """Returns abcedaire.
        glossary_uids: UIDs of glossaries used to build abcedaire"""

        terms = self.getGlossaryTerms(glossary_uids)
        letters = []

        for term in terms:
            letter = self.getFirstLetter(term).lower()
            if letter not in letters:
                letters.append(letter)

        # Sort alphabetically
        letters.sort()

        return tuple(letters)

    security.declarePublic('getAbcedaireBrains')
    def getAbcedaireBrains(self, glossary_uids, letters):
        """Returns brains from portal_catalog.
        glossary_uids: UIDs of glossaries used to build abcedaire.
        letters: beginning letters of terms to search"""

        abcedaire_brains = []
        brains = self.searchResults(glossary_uids)

        for brain in brains:
            letter = self.getFirstLetter(brain.Title).lower()
            if letter in letters:
                abcedaire_brains.append(brain)

        # Sort alphabetically
        def cmp_alpha(a, b):
            return cmp(a.Title, b.Title)

        abcedaire_brains.sort(cmp_alpha)

        return abcedaire_brains

    security.declarePublic('truncateDescription')
    def truncateDescription(self, text):
        """Truncate definition using tool properties"""

        max_length = self.description_length
        text = text.decode(SITE_CHARSET, "replace")
        text = text.strip()

        if max_length > 0 and len(text) > max_length:
            ellipsis = self.description_ellipsis
            text = text[:max_length]
            text = text.strip()
            text = '%s %s' % (text, ellipsis)

        text = text.encode(SITE_CHARSET, "replace")

        return text

    security.declarePublic('escape')
    def escape(self, text):
        """Returns escaped text."""

        return escape_special_chars(text)

    security.declarePublic('includePloneGlossaryJS')
    def includePloneGlossaryJS(self, context, request):
        """Helper for portal_javascripts
        Should we include PloneGlossary javascripts
        """
        context_state = getMultiAdapter((context, request),
                                        name=u'plone_context_state')
        if not context_state.is_view_template():
            return False
        return self.showPortlet() or self.highlightContent(context)

    def _split(self, text, removed_words=()):
        """Split unicode text into tuple of unicode terms

        @param text: unicode text to split
        @param remove_words: words to remove from the split result"""

        return tuple([x for x in text2words(text)
                       if len(x) > 1 and x not in removed_words])

InitializeClass(PloneGlossaryTool)
