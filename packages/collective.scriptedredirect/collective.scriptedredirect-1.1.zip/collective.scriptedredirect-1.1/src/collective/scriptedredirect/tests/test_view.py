import unittest2 as unittest

from zExceptions import Redirect

import zope.component
import zope.publisher.interfaces.browser

from collective.scriptedredirect.testing import\
    COLLECTIVE_SCRIPTEDREDIRECT_FUNCTIONAL

from plone.testing.z2 import Browser


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


class TestRedirectView(unittest.TestCase):
    """
    Test redirect view.
    """
    layer = COLLECTIVE_SCRIPTEDREDIRECT_FUNCTIONAL

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        # Register view directly by pushing it to zope.component multi-adapter registry

        zope.component.provideAdapter(
            # Our class
            factory=TestingRedirectHandler,
            # (context, request) layers for multiadapter lookup
            # We provide None as layers are not used
            adapts=(None, None),
            # All views are registered as IBrowserView interface
            provides=zope.publisher.interfaces.browser.IBrowserView,
            # View name
            name='redirect_handler')

        browser = Browser(self.portal)
        browser.handleErrors = False
        browser.raiseHttpErrors = False
        self.browser = browser

    def tearDown(self):
        """
        """
        # Dynamically unregister a view
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterAdapter(factory=TestingRedirectHandler,
                              required=(None, None),
                              provided=zope.publisher.interfaces.browser.IBrowserView,
                              name="redirect_handler")

    def test_redirect_view(self):
        """ Test www redirect.

        View is registered through testing.zcml.
        """

        try:
            self.browser.open(self.portal.absolute_url())
            raise AssertionError("Should not be reached")
        except Redirect as e:
            # Plone test browser handlers directs always as exceptions
            self.assertEqual(e.message, "http://www.nohost/plone")
