"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from plone.app.workflow.tests.base import WorkflowFunctionalTestCase

# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#   ztc.installProduct('SimpleAttachment')
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
# All of Plone's products are already set up by PloneTestCase.


@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    fiveconfigure.debug_mode = True
    import collective.bulksharing
    zcml.load_config('configure.zcml', collective.bulksharing)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage()
    # instead of installProduct().
    # This is *only* necessary for packages outside the Products.*
    # namespace which are also declared as Zope 2 products, using
    # <five:registerPackage /> in ZCML.

    # We may also need to load dependencies, e.g.:
    #   ztc.installPackage('borg.localrole')

    ztc.installPackage('collective.bulksharing')

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['collective.bulksharing'])


class BulkSharingFunctionalTestCase(WorkflowFunctionalTestCase):
    """Base class for functional integration tests for collective.bulksharing.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.

    """

    def afterSetUp(self):

        super(BulkSharingFunctionalTestCase, self).afterSetUp()
        self.portal.acl_users._doAddUser('testuser', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('nonasciiuser',
                                         'secret', ['Member'], [])
        self.portal.acl_users._doAddGroup('testgroup',
                                           [], title='Some meaningful title')
        nonasciiuser = \
            self.portal.portal_membership.getMemberById('nonasciiuser')
        nonasciiuser.setMemberProperties(\
            dict(fullname=u'\xc4\xdc\xdf'.encode('utf-8')))

    def update_security(self):
        pw = self.portal.portal_workflow
        pw.updateRoleMappings()
