from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import vs.bootstrap.tinymce


VS_BOOTSTRAP_TINYMCE = PloneWithPackageLayer(
    zcml_package=vs.bootstrap.tinymce,
    zcml_filename='testing.zcml',
    gs_profile_id='vs.bootstrap.tinymce:testing',
    name="VS_BOOTSTRAP_TINYMCE")

VS_BOOTSTRAP_TINYMCE_INTEGRATION = IntegrationTesting(
    bases=(VS_BOOTSTRAP_TINYMCE, ),
    name="VS_BOOTSTRAP_TINYMCE_INTEGRATION")

VS_BOOTSTRAP_TINYMCE_FUNCTIONAL = FunctionalTesting(
    bases=(VS_BOOTSTRAP_TINYMCE, ),
    name="VS_BOOTSTRAP_TINYMCE_FUNCTIONAL")
