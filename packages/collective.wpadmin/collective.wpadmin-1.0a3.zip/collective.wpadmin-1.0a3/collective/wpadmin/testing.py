from plone.testing import z2

from plone.app.testing import *
import collective.wpadmin


FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.wpadmin,
                                additional_z2_products=[],
                                name="collective.wpadmin:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.wpadmin:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.wpadmin:Functional")
