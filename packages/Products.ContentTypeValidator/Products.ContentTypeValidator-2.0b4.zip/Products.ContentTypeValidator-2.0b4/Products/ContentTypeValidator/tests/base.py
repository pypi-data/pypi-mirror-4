from plone.app.testing import PloneSandboxLayer
from plone.app.testing import FunctionalTesting

CONTENTTYPEVALIDATOR = PloneSandboxLayer(name='CONTENTTYPEVALIDATOR')

CONTENTTYPEVALIDATOR_FUNCTIONAL = FunctionalTesting(bases=(CONTENTTYPEVALIDATOR,), name='CONTENTTYPEVALIDATOR_FUNCTIONAL')
