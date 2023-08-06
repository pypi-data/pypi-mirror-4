import unittest2 as unittest

import transaction

from zExceptions import Redirect

from collective.scriptedredirect.testing import\
    COLLECTIVE_SCRIPTEDREDIRECT_FUNCTIONAL

from plone.testing.z2 import Browser


WWW_REDIRECT_SNIPPET="""

context.plone_log(url)

if not url.startswith("http://www."):
    return url.replace("http://", "http://www.")
"""

# Invalid Python code
BAD_SNIPPET="""
foobarbar
"""


class TestRedirectScript(unittest.TestCase):
    """
    Test redirect script.
    """
    layer = COLLECTIVE_SCRIPTEDREDIRECT_FUNCTIONAL

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        browser = Browser(self.portal)
        browser.handleErrors = False
        browser.raiseHttpErrors = False
        self.browser = browser

    def set_redirect_script(self, payload):

        # Define the script parameters
        parameters = "url, host, port, path"

        script = self.portal.redirect_handler
        script.ZPythonScript_edit(parameters, payload)
        transaction.commit()

    def test_redirect_default_no_redirect(self):
        """ Test that the default installation doesn't produce redirects.
        """

        # Assert no error is risen
        self.browser.open(self.portal.absolute_url())
        self.assertEqual(self.browser.headers["status"], "200 Ok")

    def test_redirect_www(self):
        """ Set www redirect
        """
        self.set_redirect_script(WWW_REDIRECT_SNIPPET)

        try:
            self.browser.open(self.portal.absolute_url())
            raise AssertionError("Should not be reached")
        except Redirect as e:
            # Plone test browser handlers directs always as exceptions
            self.assertEqual(e.message, "http://www.nohost/plone")

    def test_bad_snippet(self):
        """ See that syntax error in the script does not cause problems.
        """
        self.set_redirect_script(BAD_SNIPPET)
        self.browser.open(self.portal.absolute_url())
        self.assertEqual(self.browser.headers["status"], "200 Ok")
