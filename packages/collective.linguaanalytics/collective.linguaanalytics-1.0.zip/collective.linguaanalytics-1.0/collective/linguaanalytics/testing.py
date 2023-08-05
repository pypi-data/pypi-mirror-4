
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
import collective.linguaanalytics

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                            zcml_package=collective.linguaanalytics,
                            additional_z2_products=[],
                            gs_profile_id='collective.linguaanalytics:default',
                            name="collective.linguaanalytics:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.linguaanalytics:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.linguaanalytics:Functional")
