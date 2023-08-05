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


from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from Products.CMFCore.interfaces import ISkinsTool

def importFinalSteps(context):
    site = context.getSite()

    if context.readDataFile('enpraxis_leftskin_setup.txt') is None:
        return

    # Setup left navigation
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=site)
    left = getMultiAdapter((site, leftColumn), IPortletAssignmentMapping, context=site)
    if u'navigation' in left:
        left[u'navigation'].topLevel = 0

    # Setup custom properties for skin
    stool = site.portal_skins
    if not stool.getSkinPath('custom/baseProperties'):
        stool.leftskin.base_properties.manage_doCustomize(folder_path='custom')
