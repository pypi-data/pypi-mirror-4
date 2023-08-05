from plone.app.portlets.storage import PortletAssignmentMapping
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from zope.component import getUtility, getMultiAdapter
from Products.BlingPortlet import bling
from Products.BlingPortlet.tests.base import TestCase

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='Products.BlingPortlet.blingslideshow')
        self.assertEquals(portlet.addview, 'Products.BlingPortlet.blingslideshow')

    def testInterfaces(self):
        portlet = bling.SlideshowAssignment(u'Blingy', u'/news', u'thumb', True, 5000, u'Random', True, 80, u'default')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='Products.BlingPortlet.blingslideshow')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'name' : u'test title',
                                   'source' : u'/news',
                                   'links': True, 
                                   'scale': u'thumb',
                                   'interval':5000,
                                   'ordering':u'Random',
                                   'repeat':True,
                                   'desc_limit':80,
                                   'view':u'default',
                                   })

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], bling.SlideshowAssignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = bling.SlideshowAssignment(u'Blingy', u'/news', u'thumb', True, 5000, u'Random', True, 80, u'default')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, bling.SlideshowEditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = bling.SlideshowAssignment(u'Blingy', u'/news', u'thumb', True, 5000, u'Random', True, 80, u'default')

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, bling.SlideshowRenderer))

class TestRenderer(TestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or bling.SlideshowAssignment(u'Blingy', u'/news', u'thumb', True, 5000, u'Random', True, 80, u'default')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=bling.SlideshowAssignment(u'Blingy', u'/news', u'thumb', True, 5000, u'Random', True, 80, u'default'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        #self.failUnless('Bling' in output)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
