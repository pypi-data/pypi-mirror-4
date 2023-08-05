from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.customizablerecent import customizablerecent

from collective.portlet.customizablerecent.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.customizablerecent.CustomizableRecent')
        self.assertEquals(portlet.addview,
                          'collective.portlet.customizablerecent.CustomizableRecent')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = customizablerecent.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.customizablerecent.CustomizableRecent')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   customizablerecent.Assignment))

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = customizablerecent.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, customizablerecent.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = customizablerecent.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, customizablerecent.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment
        # constructor.
        assignment = assignment or customizablerecent.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)


    def test_recent_items(self):
        self.setRoles(['Manager'])
        if 'news' in self.portal:
            self.portal._delObject('news')
        if 'events' in self.portal:
            self.portal._delObject('events')
        if 'front-page' in self.portal:
            self.portal._delObject('front-page')
        if 'Members' in self.portal:
            self.portal._delObject('Members')
            self.folder = None

        self.portal.invokeFactory('Document', 'doc1')

        self.portal.invokeFactory('Folder', 'folder1', title="My Folder")
        folder_path = '/folder1'
        self.portal.folder1.invokeFactory('Document', 'doc2')

        r = self.renderer(assignment=customizablerecent.Assignment())
        self.assertEquals(3, len(r.recent_items()))

        r = self.renderer(assignment=customizablerecent.Assignment(count=2))
        self.assertEquals(2, len(r.recent_items()))

        r = self.renderer(assignment=customizablerecent.Assignment(content_types=('Document',)))
        self.assertEquals(2, len(r.recent_items()))

        r = self.renderer(assignment=customizablerecent.Assignment(root=folder_path))
        self.assertEquals(2, len(r.recent_items()))

        r = self.renderer(assignment=customizablerecent.Assignment(root=folder_path,
                                                                   content_types=('Document',)))
        self.assertEquals(1, len(r.recent_items()))


    def test_recently_modified_link(self):
        r = self.renderer(assignment=customizablerecent.Assignment())
        self.failUnless(r.recently_modified_link().endswith('/recently_modified'))

        r = self.renderer(assignment=customizablerecent.Assignment(content_types=('Document',)))
        self.failUnless(r.recently_modified_link().endswith('/recently_modified?portal_type:list=Document'))

        r = self.renderer(assignment=customizablerecent.Assignment(content_types=('Document', 'Folder')))
        self.failUnless(r.recently_modified_link().endswith('/recently_modified?portal_type:list=Document&portal_type:list=Folder'))

    def test_title(self):
        r = self.renderer(assignment=customizablerecent.Assignment())
        self.assertEquals(str(r.title), 'box_recent_changes')

        r = self.renderer(assignment=customizablerecent.Assignment(name="The changes"))
        self.assertEquals(str(r.title), "The changes")

        self.portal.invokeFactory('Folder', 'folder1', title="My Folder")

        r = self.renderer(assignment=customizablerecent.Assignment(root='/folder1'))
        self.assertEquals(str(r.title), 'local_recent_label')
        self.assertEquals(r.title.mapping['name'], "My Folder")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
