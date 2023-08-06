.. contents::

Introduction
====================

``collective.scriptedredirect`` allows you to write HTTP 302 Moved Temporary and HTTP 301 Moved Permanently
redirects for your `Plone CMS <http://plone.org>`_ site in Python code.

.. image:: https://travis-ci.org/collective/collective.scriptedredirect.png

Benefits
====================

* The redirect logic is front-end web server independent: no need to touch variouos configuration files of Apache, Varnish or Nginx)

* Python allows to write more complex logic for redirects easier - no regular expressions!

* Python scripts in Plone have access to more complete state information:
  user logged in status, permissions, etc.

Usage
====================

Installation
----------------

Add add-on in *buildout.cfg*::

    eggs =
        ...
        collective.scriptedredirect

Run buildout.

Install *Scripted redirects in Python* in Site Setup > Add-ons.

Doing redirects through the web
--------------------------------

Edit *redirect_handler* in Zope Management Interface in your site root.

.. image :: http://cloud.github.com/downloads/collective/collective.scriptedredirect/Screen%20Shot%202012-09-25%20at%201.28.18%20AM.png

In the case of accident use ``?no_redirect`` HTTP query parameter to override
the redirecter and fix your site.


Doing redirects through the web
--------------------------------

You can also register a browser view called ``redirect_handler``.
In this case, you write the redirect code in addon Python code
and not through the web.

``redirect_handler`` view is always preferred over ``redirect_handler`` script.

Example Python code in ``redirector.py``::

    class TestingRedirectHandler(object):
        """ Redirect handler registered as a ``redirect_handler`` Zope 3 <browser:page>
        """

        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self, url, host, port, path):
            """
            :return: None if no redirect needed, otherwise a string full HTTP URL to the redirect target

            :raise: zExceptions.Redirect or other custom redirect exception if needed
            """

            # Simple example: always access site over www. domain prefix
            if not url.startswith("http://www."):
                return url.replace("http://", "http://www.")

            # Don't redirect if we are already using www. prefix
            return None

Example ZCML::

    <browser:page
        name="redirect_handler"
        for="Products.CMFCore.interfaces.ISiteRoot"
        layer="YOUR_ADDON_LAYER"
        class=".redirector.TestRedirectHandler"
        />

Internals
====================

``collective.scriptedredirect`` hooks itself to Zope's pre-traversal hook and is
triggered before the request traverses into your Plone site in Zope application server.

Author
====================

Mikko Ohtamaa (`blog <https://opensourcehacker.com>`_, `Facebook <https://www.facebook.com/?q=#/pages/Open-Source-Hacker/181710458567630>`_, `Twitter <https://twitter.com/moo9000>`_, `Google+ <https://plus.google.com/u/0/103323677227728078543/>`_)



