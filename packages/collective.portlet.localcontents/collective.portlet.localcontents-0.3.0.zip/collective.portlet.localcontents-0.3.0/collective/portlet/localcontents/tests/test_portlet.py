from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.localcontents import localcontents

from collective.portlet.localcontents.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.localcontents.LocalContents')
        self.assertEquals(portlet.addview,
                          'collective.portlet.localcontents.LocalContents')

    def test_interfaces(self):
        portlet = localcontents.Assignment(**{'name':'In this section...', 'display_when_not_default_page': False})
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.localcontents.LocalContents')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'name':'In this section...', 'display_when_not_default_page': False})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   localcontents.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = localcontents.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, localcontents.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = localcontents.Assignment(**{'name':'In this section...', 'display_when_not_default_page': False})

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, localcontents.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def createFolder(self, id, title):
        self.portal.invokeFactory(id=id, type_name="Folder")
        self.portal[id].edit(title=title)
        return self.portal[id]

    def createDocument(self, context, id, title):
        context.invokeFactory(id=id, type_name="Document")
        context[id].edit(title=title)
        return context[id]

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or localcontents.Assignment(**{'name':'In this section...',
                                                               'display_when_not_default_page': False})
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def updatePortlet(self, context=None):
        if not context:
            context=self.portal
        r = self.renderer(context=context,
                          assignment=localcontents.Assignment(**{'name':'In this section...',
                                                                 'display_when_not_default_page': False}))
        r = r.__of__(context)
        r.update()
        return r

    def test_render_basic(self):
        r = self.updatePortlet()
        output = r.render()
        self.assertTrue('In this section...' in output)

    def test_render_defaultpage(self):
        r = self.updatePortlet()
        output = r.render()
        self.assertFalse('front-page' in output)
        self.portal.setLayout('folder_listing')
        r = self.updatePortlet()
        output = r.render()
        self.assertTrue('front-page' in output)

    def test_render_skip_excludefromnav(self):
        r = self.updatePortlet()
        output = r.render()
        self.assertTrue('Site News' in output)
        self.portal.news.edit(excludeFromNav=True)
        r = self.updatePortlet()
        output = r.render()
        self.assertFalse('Site News' in output)

    def test_render_test_icons(self):
        site_properties = self.portal.portal_properties.site_properties
        # Logged in user see enabled icons
        r = self.updatePortlet()
        output = r.render()
        self.assertTrue('src="http://nohost/plone/folder_icon.gif"' in output)
        # Logged in user see authenticated icons
        site_properties.manage_changeProperties(icon_visibility='authenticated')
        r = self.updatePortlet()
        output = r.render()
        self.assertTrue('src="http://nohost/plone/folder_icon.gif"' in output)
        # Anon user doesn't see authenticated icons
        self.logout()
        r = self.updatePortlet()
        output = r.render()
        self.assertFalse('src="http://nohost/plone/folder_icon.gif"' in output)
        # Anon user see enabled icons
        site_properties.manage_changeProperties(icon_visibility='enabled')
        r = self.updatePortlet()
        output = r.render()
        self.assertTrue('src="http://nohost/plone/folder_icon.gif"' in output)
        # Anon user doesn't see disabled icons
        site_properties.manage_changeProperties(icon_visibility='disabled')
        r = self.updatePortlet()
        output = r.render()
        self.assertFalse('src="http://nohost/plone/folder_icon.gif"' in output)
        # Logged in user doesn't see disabled icons
        self.loginAsPortalOwner()
        site_properties.manage_changeProperties(icon_visibility='disabled')
        r = self.updatePortlet()
        output = r.render()
        self.assertFalse('src="http://nohost/plone/folder_icon.gif"' in output)

    def test_render_notshow_defaultpage(self):
        """Test for a bug in the 0.1 version: must not show the portlet is the current folder has only
        one child that is the default page
        """
        folder = self.createFolder('foo1', 'Foo 1')
        document = self.createDocument(folder, 'main-page', 'Welcome to my section')
        r = self.updatePortlet(folder)
        output = r.render()
        self.assertTrue('In this section...' in output)
        self.assertTrue('Welcome to my section' in output)
        self.assertFalse(r.render.available)
        #TO-BE finished
        # this test is not working
        #folder.setDefaultPage('main-page')
        #r = self.updatePortlet(document)
        #output = r.render()
        #self.assertTrue('In this section...' in output)
        #self.assertFalse('Welcome to my section' in output)
        #self.assertFalse(r.render.available)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
