from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.app.portlets.storage import PortletAssignmentMapping
from zope.component import getUtility, getMultiAdapter

from fourdigits.portlet.twitter import fourdigitsportlettwitter as fpt
from fourdigits.portlet.twitter.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPermission(self):
        permissions = [p['name'] for p in self.app.permission_settings()]
        self.failUnless('fourdigits.portlet.twitter: Add FourdigitsPortletTwitter' in permissions)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='fourdigits.portlet.twitter.FourdigitsPortletTwitter')
        self.assertEquals(portlet.addview, 'fourdigits.portlet.twitter.FourdigitsPortletTwitter')

    def testInterfaces(self):
        portlet = fpt.Assignment(name=u"title", username="plone")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='fourdigits.portlet.twitter.FourdigitsPortletTwitter')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'name' : u"test title", 'username' : u"plone"})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], fpt.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = fpt.Assignment(name=u"title", username="plone")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, fpt.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = fpt.Assignment(name=u"title", username="plone")

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, fpt.Renderer))

        self.failUnless(renderer.available,
                        "Renderer should be available by default.")


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or fpt.Assignment(name=u"title", username="plone")

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=fpt.Assignment(name=u"title", username="plone"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('title' in output)
        self.failUnless('<a href="http://twitter.com/plone">plone</a>' in output)

    def test_hide(self):
        self.assertRaises(TypeError, fpt.Assignment, hide=True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
