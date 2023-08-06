from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.scriptedredirect


COLLECTIVE_SCRIPTEDREDIRECT = PloneWithPackageLayer(
    zcml_package=collective.scriptedredirect,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.scriptedredirect:testing',
    name="COLLECTIVE_SCRIPTEDREDIRECT")

COLLECTIVE_SCRIPTEDREDIRECT_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_SCRIPTEDREDIRECT, ),
    name="COLLECTIVE_SCRIPTEDREDIRECT_INTEGRATION")

COLLECTIVE_SCRIPTEDREDIRECT_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_SCRIPTEDREDIRECT, ),
    name="COLLECTIVE_SCRIPTEDREDIRECT_FUNCTIONAL")
