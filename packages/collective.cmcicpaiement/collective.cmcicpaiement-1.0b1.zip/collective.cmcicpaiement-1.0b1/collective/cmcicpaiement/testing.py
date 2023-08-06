from plone.app.testing import *
import collective.cmcicpaiement

FIXTURE = PloneWithPackageLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.cmcicpaiement,
    additional_z2_products=[],
    gs_profile_id='collective.cmcicpaiement:default',
    name="collective.cmcicpaiement:FIXTURE"
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="collective.cmcicpaiement:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="collective.cmcicpaiement:Functional"
)
