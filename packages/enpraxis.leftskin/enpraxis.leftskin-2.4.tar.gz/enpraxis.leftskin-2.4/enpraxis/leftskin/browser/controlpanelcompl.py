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


from zope.interface import Interface, implements
from zope.component import adapts, getUtility, getMultiAdapter
from zope.schema import TextLine, Choice, Bool
from zope.schema.vocabulary import SimpleVocabulary
from schema import ImageLine
from widgets import ImageWidget
from zope.formlib import form
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.CMFCore.interfaces import ISkinsTool
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.validators import null_validator
from plone.fieldsets.fieldsets import FormFieldsets
from enpraxis.leftskin import leftskinMessageFactory as _
from Products.CMFPlone import PloneMessageFactory


def uploadImage(context, filename, file):
    """ Upload an image object. """
    if filename in context.objectIds():
        context.manage_delObjects([filename])
    context.manage_addImage(id=filename, file=file.read())
    
class ILeftSkinComplDevSchema(Interface):

    development_mode = Bool(title=_(u'Development Mode'),
                            description=_(u'In development mode, stylesheets are not merged to composites, '
                                          'and caching and compression of css is disabled. The registry also sends '
                                          'http-headers to prevent browsers from caching the stylesheets. '
                                          'Remember to turn it off as the developmentmode affects performance.'),
                            required=True)



class ILeftSkinComplGeneralSchema(Interface):

    portal_logo = ImageLine(title=_(u'Portal Logo'),
                            description=_(u'The clickable logo in the top banner. Select '
                                          'the file to be added by clicking the \'Browse\' '
                                          'button. This image should be 360px wide by 63px '
                                          'high to fit within the default layout. The logo will '
                                          'be rendered \'on top of\' the Portal Banner.'),
                            required=False)

    portal_banner = ImageLine(title=_(u'Portal Banner'),
                              description=_(u'The top banner of your eduCommons instance. '
                                            'Select the file to be added by clicking the '
                                            '\'Browse\' button. This image should be 2000px '
                                            'wide by 65px high to fit within the default layout.'),
                              required=False)

    fluid_fixed_width = Bool(title=_(u'Fluid Fixed Width'),
                          description=_(u'If checked, the site will have a fixed width center column '
                                              'of 960 pixels. Please set the Body Background Color and/or Body Backgound Image'
                                              'as well.'),
                          required=True)

    fluid_fixed_repeat_y = Bool(title=_(u'Repeat Y-axis'),
                              description=_(u'If checked, the Body Background Image will repeat on the x- and y- axis. If unchecked '
                                              'the image will repeat only on the x-axis.'),
                              required=True)

    body_bkg_color = TextLine(title=_(u'Body Background Color'),
                                 description=_(u'The background color of the left and right columns, when the site is set to a floating fixed width.'),
                                 required=False)

    body_bkg_img = ImageLine(title=_(u'Body Background Image'),
                                 description=_(u'The background image of the left and right columns, when the site is set to a floating fixed width.'),                             
                                 required=False)


    topnav_background = ImageLine(title=_(u'Top Navigation Background Image'),
                                  description=_(u'You may customize the background of the top navigation '
                                                'elements (home, courses, help, about OCW) by uploading a '
                                                'background image. For non-tiling images, the size should '
                                                'be 2000px wide by 28px high.'),
                                  required=False)

    leftnav_background = ImageLine(title=_(u'Left Navigation Background Image'),
                                   description=_(u'The background image for the Left Hand Column. '
                                                 'Select the file to be added by clicking the '
                                                 '\'Browse\' button. This image should be 150px wide '
                                                 'by 10px high to fit within the default layout.'),
                                   required=False)
                                         
    portal_favicon = ImageLine(title=_(u'Portal Favicon'),
                               description=_(u'The favicon for your portal. Save your image as favicon.ico.'),
                               required=False)

    main_font = Choice(title=_(u'Main font'),
                       description=_(u"The preferred font, and the fall-backs if the preferred font is not available in the user's browser"),
                       required=True,
                       vocabulary='leftskin.fontfamilies_vocab')

    default_text_size  = TextLine(title=_('Default text size'),
                                 description=_('You can specify this as a % value, or in em, or (not recommended) in pixels'),
                                 required=False)

    default_font_color = TextLine(title=_(u'Default text Color'),
                                  description=_(u'The color for text in the content well of the page.  Colors can be specified as words of hex values'),
                                  required=False)

    small_text_size = TextLine(title=_('Small text size'),
                               description=_('If you specify this as a % value, it is a % of the default text size (defined above)'),
                               required=False)

    page_bkg_color = TextLine(title=_(u'Page background color'),
                                 description=_(u'Note: it is often hard to read text on a strong color'),
                                 required=False)


    unvisited_link_color = TextLine(title=_(u'Unvisited link color'),
                                  description=_(u'Make sure this looks different from visited links, even to colorblind people'),
                                  required=False)

    active_link_color = TextLine(title=_(u'Active link color'),
                                    description=_(u'When you click on a link in text, it will change color to whatever you specify here'),
                                    required=False)

    visited_link_color = TextLine(title=_(u'Visited link color'),
                                  description=_('Make sure this looks different from unvisited links, even to colorblind people '),
                                  required=False)

    default_border_width = TextLine(title = _(u'Default border width'),
                 description = _('You can specify this in pixels (e.g., 2px) or em (e.g., 0.25em) '),
                 required = False)

    default_border_style = Choice(title = _(u'Default border style'),
                                  description = _("Choose a style, or choose 'none' to have no borders at all "),
                 required = True,
                 vocabulary='leftskin.borderstyles_vocab')

    annotation_border_style = Choice(title = _(u'Annotation border style'),
                 description = _('For example, the border around comments made in response to a page '),
                 required = True,
                 vocabulary='leftskin.borderstyles_vocab')

    default_border_color = TextLine(title = _(u'Default border color'),
                 description = _(''),
                 required = False)

    secondary_bkg_color = TextLine(title = _(u'Secondary background color'),
                 description = _('The background color for the footer, portlet headers and global navigation bar '),
                 required = False)

    secondary_text_color = TextLine(title = _(u'Secondary text color'),
                 description = _('The color of the text in the footer, portlet headers and global navigation tabs '),
                 required = False)

    heading_font = Choice(title = _(u'Heading font'),
                 description = _("The preferred font, and the fall-backs if the preferred font is not available in the user's browser "),
                 required = True,
                 vocabulary='leftskin.fontfamilies_vocab')

    loggedin_tabs_border_color = TextLine(title = _(u'Logged-in tabs border color'),
                 description = _('Applies to the tabs (view, edit, etc) that you may see when logged in '),
                 required = False)

    loggedin_tabs_bkg_color = TextLine(title = _(u'Logged-in tabs background color'),
                 description = _('Applies to the tabs (view, edit, etc) that you may see when logged in '),
                 required = False)

    loggedin_tabs_text_color = TextLine(title = _(u'Logged-in tabs text color'),
                 description = _('Applies to the tabs (view, edit, etc) that you may see when logged in '),
                 required = False)

    form_inputtext_color = TextLine(title = _(u'Color of input text on forms'),
                 description = _('When someone types something into a form, the color of the text they enter '),
                 required = False)

    text_transform = Choice(title = _(u'Text transform'),
                 description = _('Regardless of how text is entered, it can be transformed to all lower case, all capitals, etc. Applies to text in global navigation tabs among other things. '),
                 required = True,
                 vocabulary='leftskin.transforms_vocab')                 

    evenrow_bkg_color = TextLine(title = _(u'Even row background color'),
                 description = _('Even-numbered rows in certain kinds of tables or lists have this background color '),
                 required = False)

    oddrow_bkg_color = TextLine(title = _(u'Odd row background color'),
                 description = _('Odd-numbered rows in certain kinds of tables or lists have this background color '),
                 required = False)

    notification_border_color = TextLine(title = _(u'Notification border color'),
                 description = _('Applies to notification elements like the status message, the calendar focus '),
                 required = False)

    notification_bkg_color = TextLine(title = _(u'Notification background color'),
                 description = _('Applies to notification elements like the status message, the calendar focus '),
                 required = False)

    discreet_text_color = TextLine(title = _(u'Discreet text color'),
                 description = _("Applies to explanatory information in forms and other items given class 'discreet' "),
                 required = False)

    info_popup_bkg_color = TextLine(title = _(u'Information pop-up background color'),
                 description = _('Warning: this is not currently used by Plone, although it is available for you to use if you wish '),
                 required = False)

    site_min_width = TextLine(title = _(u'Site minimum width'),
                 description = _('When you resize your browser window, how small can it get before a horizontal scroll bar appears? (Note: does not apply in Internet Explorer) '),
                 required = False)

    col_one_width = TextLine(title = _(u'Column One width'),
                 description = _('How wide should the left column be? '),
                 required = False)

    col_two_width = TextLine(title = _(u'Column Two width'),
                 description = _('How wide should the right column be? '),
                 required = False)



class ILeftSkinComplSchema(ILeftSkinComplDevSchema, ILeftSkinComplGeneralSchema):
    """ Combine schemas in tab form. """


class LeftSkinComplControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ILeftSkinComplSchema)

    def __init__(self, context):
        super(LeftSkinComplControlPanelAdapter, self).__init__(context)
        # look up the tool properly at some point, getUtility(ISkinsTool)
        # fails for some reason, until then just access it directly
        self.customizeBaseProperties()
        self.skins = context.portal_skins.custom
        self.props = context.portal_skins.custom.base_properties
        self.ls_props = context.portal_properties.left_skin_properties        
        self.css = context.portal_css

    # Header settings

    def get_portal_banner(self):
        return self.props.getProperty('portalHeaderBackgroundImage')

    def set_portal_banner(self, file):
        if file:
            uploadImage(self.skins, 'headerBackground.png', file)

    portal_banner = property(get_portal_banner, set_portal_banner)

    def get_fluid_fixed_width(self):
        return self.ls_props.getProperty('fluid_fixed_width')

    def set_fluid_fixed_width(self, fixed):
        self.ls_props.manage_changeProperties(fluid_fixed_width=fixed)

    fluid_fixed_width = property(get_fluid_fixed_width, set_fluid_fixed_width)

    def get_fluid_fixed_repeat_y(self):
        return self.ls_props.getProperty('fluid_fixed_repeat_y')

    def set_fluid_fixed_repeat_y(self, repeat):
        self.ls_props.manage_changeProperties(fluid_fixed_repeat_y=repeat)

    fluid_fixed_repeat_y = property(get_fluid_fixed_repeat_y, set_fluid_fixed_repeat_y)

    def get_body_bkg_color(self):
        return self.props.getProperty('bodyBackgroundColor')

    def set_body_bkg_color(self, color):
        self.props.manage_changeProperties(bodyBackgroundColor=color.encode('ascii'))

    body_bkg_color = property(get_body_bkg_color, set_body_bkg_color)

    def get_body_bkg_img(self):
        return self.props.getProperty('bodyBackgroundImage')

    def set_body_bkg_img(self, file):
        if file:
            uploadImage(self.skins, 'bodyBackground.gif', file)

    body_bkg_img = property(get_body_bkg_img, set_body_bkg_img)



    # Top Navigation Bar settings

    def get_topnav_background(self):
        return self.props.getProperty('portalTopNavBackgroundImage')

    def set_topnav_background(self, file):
        if file:
            uploadImage(self.skins, 'topNavBackground.png', file)

    topnav_background = property(get_topnav_background, set_topnav_background)

    # Left Navigation settings

    def get_leftnav_background(self):
        return self.props.getProperty('portalColumnOneBackgroundImage')

    def set_leftnav_background(self, file):
        if file:
            uploadImage(self.skins, 'columnOneBackground.png', file)

    leftnav_background = property(get_leftnav_background, set_leftnav_background)

    # General settings

    def get_development_mode(self):
        return self.css.getDebugMode()

    def set_development_mode(self, mode):
        self.css.setDebugMode(mode)

    development_mode = property(get_development_mode, set_development_mode)

    def get_portal_logo(self):
        return self.props.getProperty('logoName')

    def set_portal_logo(self, file):
        if file:
            uploadImage(self.skins, 'logo.png', file)

    portal_logo = property(get_portal_logo, set_portal_logo)

    def get_portal_favicon(self):
        return self.props.getProperty('faviconName')

    def set_portal_favicon(self, file):
        if file:
            uploadImage(self.skins, 'favicon.ico', file)
        
        if hasattr(self.props, 'faviconName'):
            self.props.manage_changeProperties(faviconName='favicon.ico')
        else:
            self.props.manage_addProperty('faviconName', 'favicon.ico', 'string')

    portal_favicon = property(get_portal_favicon, set_portal_favicon)


    def get_main_font(self):
        return self.props.getProperty('fontFamily')

    def set_main_font(self, family):
        self.props.manage_changeProperties(fontFamily=family.encode('ascii'))

    main_font = property(get_main_font, set_main_font)

    def get_default_text_size(self):
        return self.props.getProperty('fontBaseSize')

    def set_default_text_size(self, size):
        self.props.manage_changeProperties(fontBaseSize=size.encode('ascii'))

    default_text_size = property(get_default_text_size, set_default_text_size)

    def get_default_font_color(self):
        return self.props.getProperty('fontColor')

    def set_default_font_color(self, color):
        self.props.manage_changeProperties(fontColor=color.encode('ascii'))

    default_font_color = property(get_default_font_color, set_default_font_color)

    def get_small_text_size(self):
        return self.props.getProperty('fontSmallSize')

    def set_small_text_size(self, size):
        self.props.manage_changeProperties(fontSmallSize=size.encode('ascii'))

    small_text_size = property(get_small_text_size, set_small_text_size)

    def get_page_bkg_color(self):
        return self.props.getProperty('backgroundColor')

    def set_page_bkg_color(self, color):
        self.props.manage_changeProperties(backgroundColor=color.encode('ascii'))

    page_bkg_color = property(get_page_bkg_color, set_page_bkg_color)


    def get_unvisited_link_color(self):
        return self.props.getProperty('linkColor')

    def set_unvisited_link_color(self, color):
        self.props.manage_changeProperties(linkColor=color.encode('ascii'))

    unvisited_link_color = property(get_unvisited_link_color, set_unvisited_link_color)

    def get_active_link_color(self):
        return self.props.getProperty('linkActiveColor')

    def set_active_link_color(self, color):
        self.props.manage_changeProperties(linkActiveColor=color.encode('ascii'))

    active_link_color = property(get_active_link_color, set_active_link_color)

    def get_visited_link_color(self):
        return self.props.getProperty('linkVisitedColor')

    def set_visited_link_color(self, color):
        self.props.manage_changeProperties(linkVisitedColor=color.encode('ascii'))

    visited_link_color = property(get_visited_link_color, set_visited_link_color)

    def get_default_border_width(self):
        return self.props.getProperty('borderWidth')

    def set_default_border_width(self, width):
        self.props.manage_changeProperties(borderWidth=width.encode('ascii'))

    default_border_width = property(get_default_border_width, set_default_border_width)

    def get_default_border_style(self):
        return self.props.getProperty('borderStyle')

    def set_default_border_style(self, style):
        self.props.manage_changeProperties(borderStyle=style.encode('ascii'))

    default_border_style = property(get_default_border_style, set_default_border_style)

    def get_annotation_border_style(self):
        return self.props.getProperty('borderStyleAnnotations')

    def set_annotation_border_style(self, style):
        self.props.manage_changeProperties(borderStyleAnnotations=style.encode('ascii'))

    annotation_border_style = property(get_annotation_border_style, set_annotation_border_style)

    def get_default_border_color(self):
        return self.props.getProperty('globalBorderColor')

    def set_default_border_color(self, color):
        self.props.manage_changeProperties(globalBorderColor=color.encode('ascii'))

    default_border_color = property(get_default_border_color, set_default_border_color)

    def get_secondary_bkg_color(self):
        return self.props.getProperty('globalBackgroundColor')

    def set_secondary_bkg_color(self, color):
        self.props.manage_changeProperties(globalBackgroundColor=color.encode('ascii'))

    secondary_bkg_color = property(get_secondary_bkg_color, set_secondary_bkg_color)

    def get_secondary_text_color(self):
        return self.props.getProperty('globalFontColor')

    def set_secondary_text_color(self, color):
        self.props.manage_changeProperties(globalFontColor=color.encode('ascii'))

    secondary_text_color = property(get_secondary_text_color, set_secondary_text_color)

    def get_heading_font(self):
        return self.props.getProperty('headingFontFamily')

    def set_heading_font(self, family):
        self.props.manage_changeProperties(headingFontFamily=family.encode('ascii'))

    heading_font = property(get_heading_font, set_heading_font)

    def get_loggedin_tabs_border_color(self):
        return self.props.getProperty('contentViewBorderColor')

    def set_loggedin_tabs_border_color(self, color):
        self.props.manage_changeProperties(contentViewBorderColor=color.encode('ascii'))        

    loggedin_tabs_border_color = property(get_loggedin_tabs_border_color, set_loggedin_tabs_border_color)

    def get_loggedin_tabs_bkg_color(self):
        return self.props.getProperty('contentViewBackgroundColor')

    def set_loggedin_tabs_bkg_color(self, color):
        self.props.manage_changeProperties(contentViewBackgroundColor=color.encode('ascii'))        

    loggedin_tabs_bkg_color = property(get_loggedin_tabs_bkg_color, set_loggedin_tabs_bkg_color)

    def get_loggedin_tabs_text_color(self):
        return self.props.getProperty('contentViewFontColor')

    def set_loggedin_tabs_text_color(self, color):
        self.props.manage_changeProperties(contentViewFontColor=color.encode('ascii'))        

    loggedin_tabs_text_color = property(get_loggedin_tabs_text_color, set_loggedin_tabs_text_color)

    def get_form_inputtext_color(self):
        return self.props.getProperty('inputFontColor')

    def set_form_inputtext_color(self, color):
        self.props.manage_changeProperties(inputFontColor=color.encode('ascii'))        

    form_inputtext_color = property(get_form_inputtext_color, set_form_inputtext_color)

    def get_text_transform(self):
        return self.props.getProperty('textTransform')

    def set_text_transform(self, xform):
        self.props.manage_changeProperties(textTransform=xform.encode('ascii'))

    text_transform = property(get_text_transform, set_text_transform)

    def get_evenrow_bkg_color(self):
        return self.props.getProperty('evenRowBackgroundColor')

    def set_evenrow_bkg_color(self, color):
        self.props.manage_changeProperties(evenRowBackgroundColor=color.encode('ascii'))

    evenrow_bkg_color = property(get_evenrow_bkg_color, set_evenrow_bkg_color)                                     

    def get_oddrow_bkg_color(self):
        return self.props.getProperty('oddRowBackgroundColor')

    def set_oddrow_bkg_color(self, color):
        self.props.manage_changeProperties(oddRowBackgroundColor=color.encode('ascii'))

    oddrow_bkg_color = property(get_oddrow_bkg_color, set_oddrow_bkg_color)                                     

    def get_notification_border_color(self):
        return self.props.getProperty('notifyBorderColor')

    def set_notification_border_color(self, color):
        self.props.manage_changeProperties(notifyBorder=color.encode('ascii'))

    notification_border_color = property(get_notification_border_color, set_notification_border_color)                                     

    def get_notification_bkg_color(self):
        return self.props.getProperty('notifyBackgroundColor')

    def set_notification_bkg_color(self, color):
        self.props.manage_changeProperties(notifyBackgroundColor=color.encode('ascii'))

    notification_bkg_color = property(get_notification_bkg_color, set_notification_bkg_color)                                     

    def get_discreet_text_color(self):
        return self.props.getProperty('discreetColor')

    def set_discreet_text_color(self, color):
        self.props.manage_changeProperties(discreetColor=color.encode('ascii'))

    discreet_text_color = property(get_discreet_text_color, set_discreet_text_color)

    def get_info_popup_bkg_color(self):
        return self.props.getProperty('helpBackgroundColor')

    def set_info_popup_bkg_color(self, color):
        self.props.manage_changeProperties(helpBackgroundColor=color.encode('ascii'))

    info_popup_bkg_color = property(get_info_popup_bkg_color, set_info_popup_bkg_color)                                     

    def get_site_min_width(self):
        return self.props.getProperty('portalMinWidth')

    def set_site_min_width(self, width):
        self.props.manage_changeProperties(portalMinWidth=width.encode('ascii'))

    site_min_width = property(get_site_min_width, set_site_min_width)

    def get_col_one_width(self):
        return self.props.getProperty('columnOneWidth')

    def set_col_one_width(self, width):
        self.props.manage_changeProperties(columnOneWidth=width.encode('ascii'))

    col_one_width = property(get_col_one_width, set_col_one_width)

    def get_col_two_width(self):
        return self.props.getProperty('columnTwoWidth')

    def set_col_two_width(self, width):
        self.props.manage_changeProperties(columnTwoWidth=width.encode('ascii'))

    col_two_width = property(get_col_two_width, set_col_two_width)

    def clearAllSettings(self):
        """ Remove all customizations. """
        objs = self.skins.objectIds()
        custom = ['logo.png',
                  'favicon.ico',
                  'headerBackground.png', 
                  'topNavBackground.png',
                  'columnOneBackground.png',
                  'bodyBackground.gif',
                  'base_properties']
        
        self.skins.manage_delObjects(filter(lambda x:x in objs, custom))
        self.ls_props.manage_changeProperties(fluid_fixed_width=False)
        self.ls_props.manage_changeProperties(fluid_fixed_repeat_y=False)        
        stool = self.context.portal_skins
        stool.leftskin.base_properties.manage_doCustomize(folder_path='custom')

    def customizeBaseProperties(self):
        """ Ensure a copy of the current theme's base_properties exists in the custom folder  """
        self.custom = self.context.portal_skins.custom.aq_inner.aq_explicit

        if not hasattr(self.custom, 'base_properties'):
            base_props = self.context.base_properties
            base_props.manage_doCustomize(folder_path='custom')


devset = FormFieldsets(ILeftSkinComplDevSchema)
devset.id = 'basePropertiesDevSchema'
devset.description = _(u"Development Mode Setting for the Theme.")
devset.label = _(u"Development Mode")

generalset = FormFieldsets(ILeftSkinComplGeneralSchema)
generalset['portal_logo'].custom_widget = ImageWidget
generalset['portal_favicon'].custom_widget = ImageWidget
generalset['portal_banner'].custom_widget = ImageWidget
generalset['body_bkg_img'].custom_widget = ImageWidget
generalset['topnav_background'].custom_widget = ImageWidget
generalset['leftnav_background'].custom_widget = ImageWidget
generalset.id = 'basepropertiesGeneralSchema'
generalset.description = _(u'Base Properties settings for the Theme.')
generalset.label = _(u'Base Properties')


class LeftSkinComplControlPanel(ControlPanelForm):
    
    form_fields = FormFieldsets(devset, generalset)

    label = _(u'Base Properties Settings')
    description = _(u'Settings that affect the current theme. '
                    'Remember to clear you browser\'s cache in order '
                    'to see the changes made in this control panel.')
    form_name = _(u'Base Properties Settings')

    @form.action(PloneMessageFactory(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = PloneMessageFactory(u"Changes saved.")
        else:
            self.status = PloneMessageFactory(u"No changes made.")

    @form.action(_(u'Reset to Default'),
                 validator=null_validator,
                 name=u'Reset to Default')

    def handle_reset(self, action, data):

        if self.adapters.has_key('ILeftSkinComplGeneralSchema'):
            self.adapters['ILeftSkinComplGeneralSchema'].clearAllSettings()
            self.status = PloneMessageFactory(u'Changes saved.')
        else:
            self.status = PloneMessageFactory(u'No changes made.')


    @form.action(PloneMessageFactory(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')

    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(PloneMessageFactory(u"Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''
        



