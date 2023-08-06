from Products.PythonScripts.PythonScript import manage_addPythonScript

DEFAULT_REDIRECT_PY_CONTENT = """
if port not in (80, 443):
    # Don't kick in HTTP/HTTPS redirects if the site
    # is directly being accessed from a Zope front-end port
    return None

# Some default rules - comment out which ones you want to use.
# Use incoming 'url' and 'port' parameters to do the redirect.
# You return new redirect target as return value or
# directly raise an exception if special handling is needed

# Make sure that search engines and visitors access the site only WITH www. prefix
# if not url.startswith("http://www."):
#    return url.replace("http://", "http://www.")

# Make sure that search engines and visitors access the site only WITHOUT www. prefix
# if url.startswith("http://www."):
#    return url.replace("http://www.", "http://")

"""


def runCustomInstallerCode(site):
    """ Run custom add-on product installation code to modify Plone site object and others

    Python scripts can be created by Products.PythonScripts.PythonScript.manage_addPythonScript

    http://svn.zope.org/Products.PythonScripts/trunk/src/Products/PythonScripts/PythonScript.py?rev=114513&view=auto

    @param site: Plone site
    """

    # Create the script in the site root
    id = "redirect_handler"

    # Don't override the existing installation
    if not id in site.objectIds():
        manage_addPythonScript(site, id)
        script = site[id]

        # Define the script parameters
        parameters = "url, host, port, path"

        script.ZPythonScript_edit(parameters, DEFAULT_REDIRECT_PY_CONTENT)


def setupVarious(context):
    """
    @param context: Products.GenericSetup.context.DirectoryImportContext instance
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other proudct
    if context.readDataFile('collective.scriptedredirect.marker.txt') is None:
        # Not our add-on
        return

    portal = context.getSite()

    runCustomInstallerCode(portal)
