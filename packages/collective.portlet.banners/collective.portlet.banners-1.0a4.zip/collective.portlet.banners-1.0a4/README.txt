Introduction
============

collective.portlet.banners provides a portlet to display rotating images,
such as sponsor logos, which may be hyperlinked. The images and corresponding
URLs are stored in a custom content type called a Portlet Banner. Since banner
images are stored as blobs, collective.portlet.banners requires that the site
be using plone.app.blob and plone.app.imaging.

Installation
============

To install collective.portlet.banners, first ensure that your site is using
plone.app.blob and plone.app.imaging. Then add collective.portlet.banners
to the eggs section of your buildout. If you are using Plone 3.2 or earlier, 
you also need to add a ZCML slug. Then re-run buildout and restart Zope. 
You can now install the product in your Plone site using the Add/Remove
Products control panel.

Basic Use
=========

After installing the product, you should see the Portlet Banner type in the
Add New menu. You can add portlet banners anywhere on your Plone site, but
all the banners that you want to display on a particular portlet need to be
in the same folder. As with all Plone content, portlet banners are only visible
to anonymous users when they are published. If you save a portlet banner and 
the image is not displayed, you need to install plone.app.blob and 
plone.app.imaging from the Add/Remove Products control panel.

After creating the banners that you want to display, you can use the banners
portlet. Add the portlet by clicking on Manage Portlets and selecting Banners
Portlet from the drop-down menu. Then fill in the form, selecting for the
banner folder the folder where you created the banners. Be sure to also set
the title of the portlet, the delay (in seconds) between images, the fade
speed, the portlet width, and the order of the banners. Note that the width
setting **does not** resample the images, so it still important to resize and
optimize the images before uploading them.

Credits
=======

Development
-----------

* `Matt Yoder <mattyoder@groundwire.org>`_
