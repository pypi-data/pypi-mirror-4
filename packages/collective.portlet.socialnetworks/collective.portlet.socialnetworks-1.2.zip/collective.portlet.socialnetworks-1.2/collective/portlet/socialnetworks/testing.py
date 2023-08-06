from plone.app.testing import *
import collective.portlet.socialnetworks


FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                    zcml_package=collective.portlet.socialnetworks,
                    additional_z2_products=[],
                    gs_profile_id='collective.portlet.socialnetworks:default',
                    name="collective.portlet.socialnetworks:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.portlet.socialnetworks:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.portlet.socialnetworks:Functional")
