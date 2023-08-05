.. contents::

Description
===========

    A simple portlet with a lot of bling.  Includes two portlets: the
    "Bling Portlet" will retrieve a single image object per page load and
    "Bling Slideshow Portlet" will reference all image objects in the
    bling source and display them in a slideshow.  Multiple Bling and
    Bling Slideshow portlets are supported on a single page.


Installation
============

1.  Add the following to buildout.cfg

::

    [buildout]
    eggs =
    . . .(other eggs). . .
        Products.BlingPortlet

2.  Re-run buildout (typically 'bin/buildout').

3.  Start Zope (typically 'bin/instance start').

4.  Install BlingPortlet via the Plone Add/Remove Products or Add-ons
    configlet under Site Setup.


Support
=======

* Documentation for using this product is at http://weblion.psu.edu/documentation/blingportlet

* Report bugs to support@weblion.psu.edu

* Contact us::

    Penn State WebLion
    304 The 300 Building
    University Park, PA 16802
    support@weblion.psu.edu


License
=======

Copyright (c) 2011 The Pennsylvania State University. WebLion is developed
and maintained by the WebLion Project Team and its partners.

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA.
