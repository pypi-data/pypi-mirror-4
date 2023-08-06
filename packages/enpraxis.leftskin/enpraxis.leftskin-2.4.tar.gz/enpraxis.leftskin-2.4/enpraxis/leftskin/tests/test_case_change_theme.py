##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from base import leftskinTestCase
from Products.CMFCore.utils import getToolByName

class testInstall(leftskinTestCase):

    def test_leftskinInstall(self):
        self.failUnless('enpraxis.leftskin' in [product['product'] for product in self.portal.portal_setup.listProfileInfo()])

    def test_installControlPanel(self):
        control_panel = getToolByName(self.portal, 'portal_controlpanel', None)
        las = ['LeftSkin_basic', 'LeftSkin_adv']
        for la in las:
            self.failUnless(la in [listAction.id for listAction in control_panel.listActions()])
               
    def test_installJavascriptObjects(self):
        pjs = getToolByName(self.portal, 'portal_javascripts',None)
        js_files = ['js/colorpicker.js', 'js/eye.js', 'js/utils.js', 'js/layout.js']
        for js in js_files:
            self.assertEqual(pjs.getResource(js).getEnabled(), True)

    def test_installSiteCSS(self):
        cssreg = getToolByName(self.portal,'portal_css')
        css_files = ['leftskin.css', 'leftskinRTL.css', 'css/colorpicker.css', 'css/layout.css']

        for css in css_files:
            css_file = cssreg.getResource('leftskin.css')
            self.assertEqual(css_file.getCookable(),True)

    def test_installCustomBaseProperties(self):
        skins_tool = getToolByName(self.portal, 'portal_skins')
        self.failUnless('base_properties' in skins_tool.custom.aq_explicit)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testInstall))
    return suite


