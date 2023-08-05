from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import plomino.patternslib


PLOMINO_PATTERNSLIB = PloneWithPackageLayer(
    zcml_package=plomino.patternslib,
    zcml_filename='testing.zcml',
    gs_profile_id='plomino.patternslib:testing',
    name="PLOMINO_PATTERNSLIB")

PLOMINO_PATTERNSLIB_INTEGRATION = IntegrationTesting(
    bases=(PLOMINO_PATTERNSLIB, ),
    name="PLOMINO_PATTERNSLIB_INTEGRATION")

PLOMINO_PATTERNSLIB_FUNCTIONAL = FunctionalTesting(
    bases=(PLOMINO_PATTERNSLIB, ),
    name="PLOMINO_PATTERNSLIB_FUNCTIONAL")
