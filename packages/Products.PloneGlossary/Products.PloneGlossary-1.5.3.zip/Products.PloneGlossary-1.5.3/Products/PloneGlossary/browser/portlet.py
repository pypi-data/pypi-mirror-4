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
"""The glossary portlet"""

from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.PloneGlossary.config import PLONEGLOSSARY_TOOL
from Products.PloneGlossary.utils import PloneGlossaryMessageFactory as _
from Products.PloneGlossary.utils import LOG


class IGlossaryPortlet(IPortletDataProvider):
    """Our portlet has no configuration (at the moment)"""
    pass


class Assignment(base.Assignment):
    """Minimal assignment"""

    implements(IGlossaryPortlet)

    @property
    def title(self):
        return _(u"Glossary")


class Renderer(base.Renderer):
    """Renders our portlet"""

    render = ViewPageTemplateFile('ploneglossary_portlet.pt')

    def __init__(self, *args):
        super(Renderer, self).__init__(*args)

    @property
    def available(self):
        """Do we show the portlet?"""

        _available = bool(self.definitions())
        LOG.debug("Portlet available: %s", _available)
        return _available

    @memoize
    def definitions(self):
        """List of applicable definitions"""

        pgtool = getToolByName(self.context, PLONEGLOSSARY_TOOL)
        return pgtool.getDefinitionsForUI(self.context, self.request)

    @memoize
    def definition_icon(self):
        """HTML of glossary definition icon"""

        icon = getattr(self.context, 'ploneglossarydefinition_icon.gif')
        return icon.tag()


class AddForm(base.NullAddForm):
    """No add form, directly adds the portlet"""

    form_fields = form.Fields(IGlossaryPortlet)
    label = _(u"Add Glossary Portlet")
    description = _(
        u"This portlet shows the definitions of terms of the current page.")

    def create(self):
        return Assignment()
