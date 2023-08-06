.. contents::

Introduction
--------------

``collective.scriptedredirect`` allows you to write HTTP 302 Moved Temporary and HTTP 301 Moved Permanently
logic for your `Plone CMS <http://plone.org>`_ site with Python scripting.

Benefits
---------

* The redirect logic is front-end web server independent (no need to learn Apache, Varnish or Nginx)

* Python allows to write more complex logic for redirects easier (no regular expressions!)

* Python scripts in Plone have access to more complete state information
  (user logged in status, permissions, etc.)

Usage
-----

Add add-on in *buildout.cfg*::

    eggs =
        ...
        collective.scriptedredirect

Run buildout.

Install *Scripted redirects in Python* in Site Setup > Add-ons.

Edit *redirect_handler* in Zope Management Interface.

.. image :: http://cloud.github.com/downloads/collective/collective.scriptedredirect/Screen%20Shot%202012-09-25%20at%201.28.18%20AM.png

In the case of accident use ``?no_redirect`` HTTP query parameter to override
the redirecter and fix your site.

Scripting
--------------

The redirect script takes input parameters

* *url*: full URL of the request

* *host*: www.yoursite.com

* *port*: 80, 443 or custom Zope port

* *path*: the path part of URL



Internals
-----------

``collective.scriptedredirect`` hooks itself to Zope's pre-traversal hook and is
triggered before the request traverses into your Plone site in Zope application server.

Author
------

`Mikko Ohtamaa <http://opensourcehacker.com>`_