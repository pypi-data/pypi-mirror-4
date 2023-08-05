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

from Products.CMFPlone.browser.admin import AddPloneSite
from Products.CMFPlone.browser.admin import Overview as OriginalOverview
from Products.Five.browser import BrowserView
import os, os.path
from zope.component import getUtilitiesFor
from ploomcake.core.install_util import IPloomCakeCake

class AddPloomcakeSite(AddPloneSite):

    def __call__(self):
        #
        # Monkey patching - content profile (in this way it add our content instead "welcome to plone")
        #
        from Products.CMFPlone import factory
        factory._CONTENT_PROFILE = "ploomcake.installer:ploomcake-content"

        return AddPloneSite.__call__(self)

    def getCakes(self):
        return [util for utilname, util in getUtilitiesFor(IPloomCakeCake)]
    
class Overview(OriginalOverview):
    pass

class AddDemo(BrowserView):
    def __call__(self):
        exportdir = os.path.join(os.path.dirname(__file__),'demo')
        for filename in os.listdir(exportdir):
            name, ext = os.path.splitext(filename)
 
            if ext == '.zexp':
                if hasattr(self.context, name):
                    self.context.manage_delObjects(name)
                self.context._importObjectFromFile(os.path.join(exportdir, filename))

        self.request.RESPONSE.redirect(self.context.absolute_url())

