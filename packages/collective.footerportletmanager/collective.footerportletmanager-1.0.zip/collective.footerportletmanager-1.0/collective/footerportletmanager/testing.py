from plone.testing import z2

from plone.app.testing import *
import collective.footerportletmanager

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.footerportletmanager,
                                additional_z2_products=[],
                                gs_profile_id='collective.footerportletmanager:default',
                                name="collective.footerportletmanager:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.footerportletmanager:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.footerportletmanager:Functional")

