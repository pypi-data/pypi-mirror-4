==========
Change log
==========

1.5.3 (2012-10-14)
==================

* Add Plone 4.3 compatibility by avoiding hard dependency on zope.app
  packages.
  [maurits]

* Moved to https://github.com/collective/Products.PloneGlossary
  [maurits]

* do catalog dispatching right
  [tom_gross]

* added uninstall profile
  [micecchi]


1.5.2.3 (2012-04-03)
====================

* removed pointless blather logging messages
  [ajung]


1.5.2.1 (2012-03-13)
====================

* updated german translations
  [ajung]


1.5.2 (2012-01-22)
==================

* ensure that terms are sorted in descending term length in order to match
  terms with the same prefix properly (longest matches first) 
  [ajung]


1.5.1 (2011-12-08)
==================

* italian translation added
  [giacomos]


1.5.0 (2011-11-24)
==================

* Added support for switching highlighting on or off per object.  You
  need to write an adapter if you want to use this.  See for example
  https://github.com/zestsoftware/zest.ploneglossaryhighlight
  [maurits]

* PeP8, Pyflakes and i18n cleanup.
  [maurits]

* fixed: Removing special chars from descriptions  [ristow]

1.5.0-b3 (2011-07-15)
=====================

* fix imports for Plone 4.1
  [zworkb]  

* fixed problem in PloneGlossaryTool with uid_catalog and simplified code.
  [jensens]

* consider ``Contributor`` role 
  [jensens]

1.5.0-b2 (2011-04-19)
======================

* Plone 4 CSS fixes

1.5.0-b1 (2011-04-13)
======================

* Plone 4 compatibility

1.4.2 - 2010-08-16
==================

* Fixed the tool ZMI access (properties tab)
  [glenfant]

* Fixed conflicts with Kupu stuffs http://plone.org/products/ploneglossary/issues/5
  [glenfant]

* GS schema version 2 and upgrade steps
  [glenfant]

1.4.1 - 2010-06-14
==================

* Return empty string when reading search_letter from request as default to
  avoid .lower() crash in GlossaryMainPage.__init__.
  [rnix]

* IE8 compatibility fix - thanks to Francesco Manna
  [glenfant]

* Condition to add CSS class "selected" to the Abcedaire didn't match.
  http://plone.org/products/ploneglossary/issues/2
  Thanks to Martin Stadler
  [glenfant]

* Call portal_catalog.n_indexObject instead of BaseObject.n_indexObject. Latter
  one causes collective.indexing crash due to recursion error.
  [rnix]

1.4.0 - 2009-12-04
==================

* Fix upgrade step version.
  [kdeldycke] 2009-04-29

* Refactor to avoid errors in tests tearDown
  [tdesvenain]

* Fix portlet's <span> HTML tags to please IE6
  (see http://dev.plone.org/plone/ticket/9027 for details).
  [kdeldycke] 2009-05-06


1.4.0 RC2 - 2008-09-22
======================

* Upgrades moved to the GenericSetup way, and removed (useless)
  "Migration" tab.
  [glenfant]

* i18n of schemas using message factory.
  [glenfant]

* Fixed test fixtures and associated GS profile.
  [glenfant]

* Added metadata.xml to profiles, provision for future upgrades.
  [glenfant]

* Fixed sorting of terms in glosary view using unicode normalization.
  [glenfant]

* Eggification.
  [glenfant]

* Added "add permissions" for content types instead of generic "Add portal
  content"
  [bmathieu]

* Using unicode normalization to get first letter of the term. This allows
  to find terms starting with non-ascii characters.
  [naro]

* use the standard PropertyManager API to handle properties on the tool
  [wichert]

* clean up imports and remove some unneeded bbb code to make pyflakes happy
  [wichert]

* improve the English wording in a few places
  [wichert]

1.4.0 RC1
=========

* Using Zope 3 "page" technology to speed up complex templates
  [glenfant]

* Using KSS style views for fast edit.
  [glenfant]

* Full GenericSetup installation
  [glenfant]

* Changed portlet into Plone 3 style
  [glenfant]

* Fixed unit tests (new worflow doesn't allow anon to grab into
  glossary)
  [glenfant]

* Adding a /browser for new style views
  [glenfant]

* Fix bug causing html entities in definition title/description to
  appear as entity code instead of char ( ie. &amp; instead of & )

* Install: check for scripts/CSS before registering them

* Added support for Generic setup for the main tool

* Refactored as it can be overloaded

* Manages many types of glossaries

* Added interfaces

* Added test environment

* Don't set to debug in config.py by default. [roeder]
  Otherwise there would be a bogus content type cluttering up portal_types.

* Batch navigation in glossary view added [roeder]

* Fixed highlighting : all glossaries are used if no glossary
  explicitly selected

* Added czech translation (Lukas Zdych)

* Added a patch for ZCTextIndex _apply_index method: search terms with
  synonymous found in global glossaries are replaced by an equivalent
  "OR". By default this is done only for 'SearchableText' . This patch
  is disabled by default (see config.py). [bmathieu]

* Fill portlet by template construct instead of javascript [bmathieu]

* Dropped plone 2.0 compatibility: use css and javascript
  registries. Portlet structure complies with plone 2.1/2.5 standard
  structures.  Improved: highlight definitions whether portlet is
  displayed or not. [bmathieu]

* Configure Glossary and Definitions to be managed by portal_factory
  [bmathieu]

* Added support for rename after creation for glossary and definition
  contents [bmathieu]

* Added german translation thanks to Richard M. Kues

* Added spanish translation thanks to Hector Velarde

* Added share tabs [zegor]

1.3.3 - 2006-03-01
==================

* Added a screenshot in the docs folder

* Added polish translation thanks to Piotr Furman

* Fixed a problem in htm2text. Carriage returns were not interpreted
  as white space. This resulted in combined words to be merged.  For
  example: "<div>plone\r\nglossary</div>" -> "ploneglossary" instead
  of "plone glossary".

1.3.2 - 2006-01-06
==================

* Added 'alpha_sort' parameter on tool.getObjectRelated*, for getting
  terms sorted by title [b_mathieu] 2006-02-06

* In encode ascii function, normalize char by char, to make sure
  unicode string has the same length as ascii string

* Added functionality to allow true local glossaries. It includes a
  config setting in the configlet. [ender] 2006-01-30

* Changed the definition view so that it also shows the variants.
  [ender] 2006-01-30

1.3.1 2006-01-30
================

* Fix bug in encode ascii method

* For AT content, analyse only string and text fields

1.3 2006-01-24
==============

* Variants of a word can now be defined.

1.3 RC2 - 2006-01-06
====================

* Fix highlight script. The position of word to highlight was
  erroneous.

1.3 RC1 - 2006-01-05
====================

* Object words with accents are highlighted even if the glossary term
  is a little bit different

* Improve find_word function

* Changed Title and Description indexes to be ZCTextIndex based.

* Added a special latin lexicon class. The lexicon is initialized when
  adding the GlossaryCatalog and used by the ZCTextIndex indexes.

* Use the same normalizer of lexicon to parse SearchableText

* Add method rebuildCatalog on PloneGlossary to rebuild all glossary
  catalog

* Update javascript highlighting words to work on Firefox and IE

* Fixed access problem to glossary's catalogs for anonymous users -
  [zegor]

* Use AddPortalContent permission to add Glossary and definitions

1.1 - 2005-09-05
================

* Remove highlight for input or textarea tags

* Check permissions in plone glossary portlet
