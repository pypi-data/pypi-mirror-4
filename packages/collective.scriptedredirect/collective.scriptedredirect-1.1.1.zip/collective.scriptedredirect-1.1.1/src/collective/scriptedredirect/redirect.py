"""

    Call a custom TTW script and allow it to handle redirects.


    Use Zope Management Interface to add a ``Script (Python)`` item named ``redirect_handler``
    to your site root - you can edit this script in fly to change the redirects.

    * Redirect script must contain ``url`` in its parameter list

"""


import logging
from urlparse import urlparse

# Really old old stuff
from zExceptions import Redirect
from ZODB.POSException import ConflictError

from zope.component import queryMultiAdapter

logger = logging.getLogger("redirect")


def get_redirect_handler_for_site(site, request):
    """ Get view or script handling the redirect.

    :return: callable or None
    """

    view = queryMultiAdapter((site, request), name="redirect_handler")
    if view:
        return view

    # Check if we have a redirect handler script in the site root
    if "redirect_handler" in site:
        return site["redirect_handler"]

    return None


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
    handler = get_redirect_handler_for_site(site, request)
    if handler:

        try:
            # Call the script and get its output
            value = handler(url=url, host=host, port=port, path=path)

            if value is not None and value.startswith("http"):
                # Trigger redirect, but only if the output value looks sane
                raise Redirect(value)
        except ConflictError:
            # Zope 2 retry exception
            raise
        except Redirect:
            # Redirect exceptions are the only legal ones
            # from above logic
            raise
        except Exception as e:
            # No silent exceptions plz
            logger.error("Redirect exception for URL:" + url)
            logger.exception(e)
            return
