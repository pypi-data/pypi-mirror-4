from plone.testing import z2

from plone.app.testing import *
import collective.diggdigg

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.diggdigg,
                                additional_z2_products=[],
                                gs_profile_id='collective.diggdigg:default',
                                name="collective.diggdigg:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.diggdigg:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.diggdigg:Functional")

