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

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('ploomcake.xhtmlstrict_theme_various.txt') is None:
        return
    site = context.getSite()


    # remove invalid attribute from front-page
    pc = site.portal_catalog

    for fp in pc.searchResults(id="front-page"):
        obj = fp.getObject()
        txt = obj.getText().replace('target="_blank"', "")        
        obj.setText(txt)

    # uninstall portlet embed
    pq = site.portal_quickinstaller
    try:
        pq.uninstallProducts(products = ['collective.portlet.embed',])
    except AttributeError:
        pass




