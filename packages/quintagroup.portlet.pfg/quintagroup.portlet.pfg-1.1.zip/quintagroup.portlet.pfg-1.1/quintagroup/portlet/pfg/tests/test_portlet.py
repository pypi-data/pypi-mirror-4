from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from quintagroup.portlet.pfg import pfg

from quintagroup.portlet.pfg.tests.base import TestCase


class TestPFGPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('FormFolder', 'test_form')

    def testPortletTypeRegistered(self):
        portlet = getUtility(
            IPortletType, name='quintagroup.portlet.pfg.PFGPortlet')
        self.assertEquals(
            portlet.addview, 'quintagroup.portlet.pfg.PFGPortlet')

    def testInterfaces(self):
        portlet = pfg.Assignment(target_form=u"/test_form")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(
            IPortletType, name='quintagroup.portlet.pfg.PFGPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'target_form': u"/test_form"})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], pfg.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = pfg.Assignment(target_form=u"/test_form")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, pfg.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = pfg.Assignment(target_form=u"/test_form")

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, pfg.Renderer))


class TestPFGPortletRenderer(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.setRoles(('Manager',))
        self.portal.invokeFactory('FormFolder', 'test_form')

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or pfg.Assignment(target_form="/test_form")

        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_portletStyle(self):
        assignment = pfg.Assignment(target_form="/test_form")
        renderer = self.renderer(context=self.portal,
                                 request=self.portal.REQUEST,
                                 assignment=assignment)
        renderer = renderer.__of__(self.portal)
        renderer.update()

        self.failUnless('Your E-Mail Address' in renderer.render())
        self.failUnless('Subject' in renderer.render())
        self.failUnless('Comments' in renderer.render())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPFGPortlet))
    suite.addTest(makeSuite(TestPFGPortletRenderer))
    return suite
