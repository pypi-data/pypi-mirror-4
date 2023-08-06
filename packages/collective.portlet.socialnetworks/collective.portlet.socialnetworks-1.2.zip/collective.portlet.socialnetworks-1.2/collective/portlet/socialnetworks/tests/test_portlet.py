import unittest2 as unittest

from pyquery import PyQuery
from zope.component import getUtility, getMultiAdapter

from plone.portlets import interfaces
from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.socialnetworks import socialnetworks
from collective.portlet.socialnetworks.tests.base import IntegrationTestCase


class IntegrationTestPortlet(IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestPortlet, self).setUp()
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            interfaces.IPortletType,
            name='collective.portlet.socialnetworks.SocialNetworks')
        self.assertEquals(portlet.addview,
                          'collective.portlet.socialnetworks.SocialNetworks')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = socialnetworks.Assignment()
        self.assertTrue(interfaces.IPortletAssignment.providedBy(portlet))
        data = portlet.data
        self.assertTrue(interfaces.IPortletDataProvider.providedBy(data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            interfaces.IPortletType,
            name='collective.portlet.socialnetworks.SocialNetworks')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'header': u'Follow us'})

        self.assertEquals(len(mapping), 1)
        self.assertIsInstance(mapping.values()[0], socialnetworks.Assignment)

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = socialnetworks.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertIsInstance(editview, socialnetworks.EditForm)

    def test_obtain_renderer(self):
        context = self.folder
        request = self.request
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(interfaces.IPortletManager,
                             name='plone.rightcolumn',
                             context=self.portal)

        assignment = socialnetworks.Assignment(header="Follow us")

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment),
            interfaces.IPortletRenderer)
        self.assertIsInstance(renderer, socialnetworks.Renderer)


class IntegrationTestRenderer(IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestRenderer, self).setUp()
        self.setRoles(('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            interfaces.IPortletManager,
            name='plone.rightcolumn',
            context=self.portal)

        assignment = assignment or \
            socialnetworks.Assignment(header="Follow us")
        return getMultiAdapter((context, request, view, manager, assignment),
                               interfaces.IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal,
                          assignment=socialnetworks.Assignment())
        r = r.__of__(self.folder)
        r.update()
        pq = PyQuery(r.render())
        links = pq('a')
        self.assertEqual(len(links), 4)
        facebook, twitter, linkedin, youtube = links
        self.assertEqual(facebook.attrib['href'],
                         'https://www.facebook.com/cirbcibg')
        self.assertEqual(twitter.attrib['href'],
                         'https://twitter.com/cirb_cibg')
        self.assertEqual(linkedin.attrib['href'],
                         'http://www.linkedin.com/company/cirb_cibg')
        self.assertEqual(youtube.attrib['href'],
                         'http://www.youtube.com/user/CIRBCIBG')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
