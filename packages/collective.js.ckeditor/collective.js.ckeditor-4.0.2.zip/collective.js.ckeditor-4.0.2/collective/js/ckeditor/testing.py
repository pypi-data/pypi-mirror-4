from plone.testing import z2

from plone.app.testing import *
import collective.js.ckeditor

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.js.ckeditor,
                                additional_z2_products=[],
                                gs_profile_id='collective.js.ckeditor:default',
                                name="collective.js.ckeditor:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.js.ckeditor:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.js.ckeditor:Functional")

