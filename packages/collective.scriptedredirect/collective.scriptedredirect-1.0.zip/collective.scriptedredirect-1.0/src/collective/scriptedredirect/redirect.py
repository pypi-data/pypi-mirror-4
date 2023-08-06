"""

    Call a custom TTW script and allow it to handle redirects.


    Use Zope Management Interface to add a ``Script (Python)`` item named ``redirect_handler``
    to your site root - you can edit this script in fly to change the redirects.

    * Redirect script must contain ``url`` in its parameter list

"""


import logging
from urlparse import urlparse

# Now we import things through the last decade...

# Really old old stuff
from zExceptions import Redirect

logger = logging.getLogger("redirect")


def check_redirect(site, event):
    """
    Check if we have a custom redirect script in Zope application server root.

    If we do then call it and see if we get a redirect.

    The script itself is TTW Python script which may return
    string in the case of redirect or None if no redirect is needed.

    For more examples, check

    http://svn.zope.org/Zope/trunk/src/Zope2/App/tests/testExceptionHook.py?rev=115555&view=markup
    """
    request = event.request

    url = request["ACTUAL_URL"]

    parts = urlparse(url)
    netloc = parts.netloc.split(":")
    host = netloc[0]

    path = parts.path

    if len(netloc) > 1:
        port = int(netloc[1])
    else:
        if parts.scheme == "https":
            port = 443
        else:
            port = 80

    if "no_redirect" in request.form:
        # Use no_redirect query parameter to disable this behavior in the case
        # you mess up with the redirect script
        return

    # Check if we have a redirect handler script in the site root
    if "redirect_handler" in site:

        try:
            # Call the script and get its output
            value = site.redirect_handler(url=url, host=host, port=port, path=path)
        except Exception, e:
            # No silent exceptions plz
            logger.error("Redirect exception for URL:" + url)
            logger.exception(e)
            return

        if value is not None and value.startswith("http"):
            # Trigger redirect, but only if the output value looks sane
            raise Redirect(value)
