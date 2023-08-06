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

from zope.interface import Interface
from zope.component import adapts
from zope.formlib import form
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import DropdownChoiceWidget

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

ICON_VISIBILITY_CHOICES = {
    _(u"Only for users who are logged in"): 'authenticated',
    _(u"Never show icons"): 'disabled',
    _(u"Always show icons"): 'enabled',
}

ICON_VISIBILITY_VOCABULARY = SimpleVocabulary(
    [SimpleTerm(v, v, k) for k, v in ICON_VISIBILITY_CHOICES.items()]
    )


class ISkinsSchema(Interface):

    theme = Choice(title=_(u'Default theme'),
                  description=_(u'''Select the default theme for the site.'''),
                  required=True,
                  missing_value=tuple(),
                  vocabulary="plone.app.vocabularies.Skins")

    mark_special_links = Bool(title=_(u'Mark external links'),
                              description=_(u"If enabled all external links "
                                             "will be marked with link type "
                                             "specific icons. If disabled "
                                             "the 'external links open in new "
                                             "window' setting has no effect."),
                              default=True)

    ext_links_open_new_window = Bool(title=_(u"External links open in new "
                                              "window"),
                                     description=_(u"If enabled all external "
                                                    "links in the content "
                                                    "region open in a new "
                                                    "window."),
                                     default=False)

    icon_visibility = Choice(title=_(u'Show content type icons'),
                             description=_(u"If disabled the content icons "
                                            "in folder listings and portlets "
                                            "won't be visible."),
                             vocabulary=ICON_VISIBILITY_VOCABULARY)


class SkinsControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(ISkinsSchema)

    def __init__(self, context):
        super(SkinsControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_skins')
        self.jstool = getToolByName(context, 'portal_javascripts')
        ptool = getToolByName(context, 'portal_properties')
        self.props = ptool.site_properties

    def get_theme(self):
        return self.context.getDefaultSkin()

    def set_theme(self, value):
        self.context.default_skin = value

    theme = property(get_theme, set_theme)

    def get_mark_special_links(self):
        return self.jstool.getResource('mark_special_links.js').getEnabled()

    def set_mark_special_links(self, value):
        if value:
            self.jstool.getResource('mark_special_links.js').setEnabled(True)
        else:
            self.jstool.getResource('mark_special_links.js').setEnabled(False)
        self.jstool.cookResources()

    mark_special_links = property(get_mark_special_links,
                                  set_mark_special_links)

    def get_ext_links_open_new_window(self):
        elonw = self.props.external_links_open_new_window
        if elonw == 'true':
            return True
        return False

    def set_ext_links_open_new_window(self, value):
        if value:
            self.props.manage_changeProperties(external_links_open_new_window='true')
        else:
            self.props.manage_changeProperties(external_links_open_new_window='false')
        self.jstool.cookResources()

    ext_links_open_new_window = property(get_ext_links_open_new_window,
                                         set_ext_links_open_new_window)

    def get_icon_visibility(self):
        return self.props.icon_visibility

    def set_icon_visibility(self, value):
        self.props.manage_changeProperties(icon_visibility=value)

    icon_visibility = property(get_icon_visibility,set_icon_visibility)


class SkinsControlPanel(ControlPanelForm):

    form_fields = FormFields(ISkinsSchema)
    form_fields['theme'].custom_widget = DropdownChoiceWidget

    label = _("Theme setting")
    description = _("Settings that affect the site's look and feel.")
    form_name = _("Theme settings")

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        #Define custom folder and base props
        self.custom = self.context.portal_skins.custom.aq_inner.aq_explicit

        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _(u"Changes saved.")

            if hasattr(self.custom, 'base_properties'):
                self.backup_base_properties(data)

            self.restore_base_properties(self.custom, data)    

        else:
            self.status = _(u"No changes made.")

    def backup_base_properties(self, data):
        #backup base_properties on theme change
        self.base_props = self.custom.base_properties
        cur_theme_title = self.base_props.plone_skin

        #If base_props plone_skin value != new theme name, back up base_props
        if data['theme'] != cur_theme_title:
            #backup self.base_props
            self.custom.manage_renameObjects([self.base_props.id], [self.base_props.id + '.' + cur_theme_title.lower().replace(' ', '')])
        
    def restore_base_properties(self, custom, data):
        #on theme change, restore backed up base_properties, if it exists
        for id, obj in custom.items():
            if 'base_properties' in id:
                if obj.plone_skin == data['theme']:
                    custom.manage_renameObjects([id], ['base_properties'])
                    self.context.changeSkin(data['theme'], self.context.REQUEST)
        
