LeftSkin Product
================

The LeftSkin product is a Plone Add-on designed to simplify the process of skinning a Plone site.

Installing Leftskin
===================

To install Leftskin you must first setup up easy_install_. After installing easy_install, you can install the Leftskin product by running:
  
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall

  easy_install enpraxis.leftskin
  
To add the *Leftskin* product to your Plone site, start your Plone site and enter the control panel. Then click on the *Add-on products* link in your Plone control panel. Select the *Leftskin* checkbox and click the *install* button. The product will appear in the list of installed products.

.. image:: images/install_leftskin.png
   :alt: Install Leftskin checkbox

Using the Leftskin Product
==========================

To skin your site using the Leftskin product, navigate to the Site Setup page and click the *Left Skin CSS Settings* in the *Add-on Product Configuration* section.

.. image:: images/leftskincss_settings.png
   :alt: The Leftskin CSS Links

The customizations that you can make in Leftskin are broken down into five categories:

.. image:: images/leftskincss_categories.png
   :alt: The Leftskin headers

Using the Color Picker
----------------------

When you click on a color field, the color picker appears.

.. image:: images/leftskin_colorpicker.png
   :alt: The Leftskin color picker

To use the color picker user your mouse to select the color. Once you have selected the color you must click on the color wheel (in the lower right hand corner) to set the color.

.. image:: images/leftskin_colorwheel.png
   :alt: The Leftskin color wheel

Clicking outside of the color picker frame will close the color picker.

Reshreshing the Site
--------------------

Changes to your skin may not be immediately visible if you have pages that are still available through your browser's cache. To refresh the page without pulling from the cache hold down the shift button while you refresh the page.

Advanced Settings
-----------------

The Leftskin Product also provides the CSS Helper.

.. image:: images/leftskin_helper.png
   :alt: The Leftskin helper

This form is for advanced users of Plone who want to make fine-tuned changes to the appearance of the site. In addition, the form also allows the user to place the site in development mode, preventing css from aggregating css pages (especially useful for debugging css issues).







	