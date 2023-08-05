Introduction
============

A portlet for Plone someway similar the navigation ones, but only show contents inside the current folder visited
by the current user (so the position where you add the portlet to the portal is important only to know where the
portlet is show or not).

If the current context is not a folder but a content inside the folder itself, the portlet is still shown; this mean that
the folder sublevel is always shown, but if you move to another subfolder, the portlet will begin showing this second
folder contents.  

The portlet is only shown when the current folder is of *IATFolder* type (or subtypes) like every standard Plone Folder
content types (not in the portal root, for example).

Normally, the portlet is not displayed when the current context is also the folder itself, so if the folder is not using
a content as default view.
You can change this behaviour selecting the "*Show when not using default content view*" flag.

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

