#!/bin/bash
# Run this script to update the translations.

# Rebuild the pot file for the ploneglossary domain.
i18ndude rebuild-pot --pot i18n/glossary.pot --create ploneglossary .
# Merge with the manual file
i18ndude rebuild-pot --pot i18n/glossary.pot --merge i18n/manual.pot --create ploneglossary .
# Sync with the ploneglossary po files.
i18ndude sync --pot i18n/glossary.pot $(find i18n -iregex '.*\.po$'|grep -v plone)

# Rebuild the pot file for the plone domain.  We only look in the GS
# profiles.  Actually, this does not work; I think it wants to find at
# least one translation in a page template or python file.  So skip this.
#i18ndude rebuild-pot --pot i18n/glossary-plone.pot --create plone profiles/

# Sync with the plone po files.
#i18ndude sync --pot i18n/glossary-plone.pot i18n/glossary-plone-*.po
