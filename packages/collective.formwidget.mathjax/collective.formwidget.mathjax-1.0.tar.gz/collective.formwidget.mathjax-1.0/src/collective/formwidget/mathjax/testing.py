from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.mathjaxwidget


COLLECTIVE_MATHJAXWIDGET = PloneWithPackageLayer(
    zcml_package=collective.mathjaxwidget,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.mathjaxwidget:testing',
    name="COLLECTIVE_MATHJAXWIDGET")

COLLECTIVE_MATHJAXWIDGET_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_MATHJAXWIDGET, ),
    name="COLLECTIVE_MATHJAXWIDGET_INTEGRATION")

COLLECTIVE_MATHJAXWIDGET_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_MATHJAXWIDGET, ),
    name="COLLECTIVE_MATHJAXWIDGET_FUNCTIONAL")
