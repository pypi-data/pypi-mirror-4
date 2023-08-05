Schools is a free responsive diazo theme for Plone 4.2.2.

Features
--------

**Responsive Web Design**

 Schools is a fully responsive theme that allows for easy viewing on mobile devices and tablets. The website will start to automatically resize and reposition the content to accommodate the different device screen sizes. 

**Customizable logo**

 Schools diazo theme comes with default Plone logo.  You can replace it with your own as you would do it in default Plone: in ZMI customize  *portal_skins -> sunburst_images -> logo.png*.

**Configurable left/right column width** 

 Go to *Site Setup -> Theming*, open *Advanced settings* tab.  In *Parameter expressions* textarea change the *columnonewidth* or/and *columntwowidth* parameters values respectively.

**Improved thumbnail display view**

 To see the changes go to Display dropdown menu and click on Thumbnail view. 

**Top image**

 The theme allows you to replace header image for the whole site or site sections. To have new top image, add image with ``topimage`` shortname into desirable location on site. Default image size is 993*107px. 

 In case you upload higher image, it will not be completely displayed. To change it go to *Site Setup -> Theming*, open *Advanced settings* tab. In *Parameter expressions* textarea set the *logo_min_height* parameter value from 107  with a new header height.

**Top portlet**

 Right top area is reserved for a portlet. The first portlet from right column is displayed there.

**Theme Colors**

 You can change links colors: ``links_color``, ``hover_links_color``, and ``visited_links_color``. For this, go to *Site Setup -> Theming -> Advanced settings* tab.  In *Parameter expressions* textarea change the 'links_color' or/and 'hover_links_color' or/and 'visited_links_color' parameters values respectively.

**Carousel Banner**

 Rotating banners can be added in case you install ``Products.Carousel`` add-on. Custom Carousel display style applies automatically to carousel banner.
 
 To create a banner on the front page, go to the *Carousel* tab in the task bar. Set carousel options and select *Carousel Banner* from *Add new...* drop-down menu. Upload image that will be used as one rotating banner, type its title and text (will be displayed under the image), and provide web address, image title will be linked to. Add as many carousel banners as you need. 
  
 Recommended image dimensions are  397*288px. There are 4 demo images that might be used as demo banners - see *src* folder within theme package (*quintagroup -> theme -> schools*).

**Editable Slogan**

 Schools Theme uses customizable slogan. To change it, go to *Site Setup -> Theming -> Advanced Settings* tab. In *Parameter expressions* textarea change ``Free Theme for Plone`` slogan in *slogan* line.

 If you need your slogan to be displayed in non-ASCII characters, go to *Site Setup -> Theming*, open *Advanced settings* tab.  In *Parameter expressions* change the following field  
 
 ``slogan = string:Free Theme for Plone`` 

 to 

 ``slogan = python:path('context/slogan|string:').decode('utf-8', 'ignore')``
 
 and in *Site Setup -> Zope Management Interface settings -> Properties* tab add a new property *slogan*, type ``string``, value ``your slogan`` and save.

**Editable footer** 

  Customize: *portal_view_customizations -> plone.footer*.

**Supported Add-Ons**

  Additional features can be activated:

* ``Products.Carousel``
   Adds rotating Carousel banner feature. Adjusted stylings to Carousel

* ``Products.ContentWellPortlets``
   Allows adding portlets in the header, footer and content area.

* ``Products.PloneFormGen``
   Adds TTW Form Generator feature.

* ``quintagroup.dropdownmenu``
   Adds adjusted styling to drop-down menu.

* ``Products.LinguaPlone``
   Adds multilingual functionality with adjusted styling for language selectors.

Dependencies
============

* plone.app.theming

Recommended
===========

Theme was tested with:

* Plone 4.2.2
* plone.app.theming 1.1b1
* Products.Carousel 2.2
* Products.ContentWellPortlets 4.1.0
* Products.PloneFormGen 1.7.6
* quintagroup.dropdownmenu 1.2.11
* Products.LinguaPlone 4.1.2

Home Directory
==============

http://themes.quintagroup.com/product/schools

Authors
=======

* Yuriy Hvozdovych
* Taras Peretiatko 
* Volodymyr Rudnytskyy
* Serhiy Valchuk  

Quintagroup: http://quintagroup.com, 2013