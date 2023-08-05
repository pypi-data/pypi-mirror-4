#!/usr/bin/env python
# Authors: Maurizio Lupo <maurizio.lupo@redomino.com> and contributors (see docs/CONTRIBUTORS.txt)
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
"""
ploomcake setup handlers.
"""

from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from Products.CMFPlone.interfaces import INonInstallable as INonInstallableProfile
from zope.interface import implements


class HiddenProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return ['ploomcake.installer']

class HiddenProfiles(object):
    implements(INonInstallableProfile)

    def getNonInstallableProfiles(self):
        return ['ploomcake.installer:ploomcake-content']


from Products.CMFPlone.setuphandlers import setupPortalContent as setupPlonePortalContent
from zope.i18n.locales import locales
from zope.component import queryUtility
from zope.i18n.interfaces import ITranslationDomain

import front_page

# just a hack to mislead i18ndude to put these strings in the .po
_ = lambda x: x
hack_title = _(u'front-title')
hack_desc = _(u'front-description')
hack_text = _(u'front-text')


def setupPortalContent(p):
    """
    Import default plone content
    """
    setupPlonePortalContent(p)

    language = p.Language()
    parts = (language.split('-') + [None, None])[:3]
    locale = locales.getLocale(*parts)
    target_language = base_language = locale.id.language

    util = queryUtility(ITranslationDomain, 'ploomcake.installer')
    if util is not None:
        front_title = util.translate(u'front-title',
                                   target_language=target_language,
                                   default=front_page.title)
        front_desc = util.translate(u'front-description',
                           target_language=target_language,
                           default=front_page.desc)
        front_text= util.translate(u'front-text',
                           target_language=target_language,
                           default=front_page.text)


    existing = p.keys()
    fp = p['front-page']

    fp.setTitle(front_title)
    fp.setDescription(front_desc)

    fp.setText(front_text, mimetype='text/html')

    fp.reindexObject()

def importContent(context):
    """
    Final Plone content import step.
    """
    # Only run step if a flag file is present
    if context.readDataFile('ploomcake-content.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)


