import transaction
import unittest2 as unittest
from collective.portlet.socialnetworks import testing
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

        self.registry = self.portal.portal_registry
        key = 'collective.portlet.socialnetworks'
        self.registry[key] = (
            u"facebook|https://www.facebook.com/cirbcibg",
            u"twitter|https://twitter.com/cirb_cibg",
            u"linkedin|http://www.linkedin.com/company/cirb_cibg",
            u"youtube|http://www.youtube.com/user/CIRBCIBG",
            )

    def setRoles(self, roles):
        testing.setRoles(self.portal, testing.TEST_USER_ID, roles)


class FunctionalTestCase(IntegrationTestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        #we must commit the transaction
        transaction.commit()
