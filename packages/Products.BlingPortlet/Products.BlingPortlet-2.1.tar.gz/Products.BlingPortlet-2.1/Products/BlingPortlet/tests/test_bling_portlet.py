from plone.app.portlets.storage import PortletAssignmentMapping
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from zope.component import getUtility, getMultiAdapter
from Products.BlingPortlet import bling
from Products.BlingPortlet.tests.base import TestCase
from mocker import Mocker
from datetime import datetime

from Products.ATContentTypes.tests.test_atimage import loadImage
icon = loadImage('test.gif')

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='Products.BlingPortlet.bling')
        self.assertEquals(portlet.addview, 'Products.BlingPortlet.bling')

    def testInterfaces(self):
        portlet = bling.Assignment(u'Blingy', u'/news', u'thumb', True, u'Random', u'default')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='Products.BlingPortlet.bling')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'name' : u'test title',
                                   'source' : u'/news',
                                   'links': True, 
                                   'scale': u'thumb',
                                   'change': u'Random',
                                   'view': u'default'})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], bling.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = bling.Assignment(u'Blingy', u'/news', u'thumb', True, u'Random', u'default')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, bling.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        folderpath = '/'.join(self.folder.getPhysicalPath())
        self.folder.invokeFactory('Document', id='doc')

        assignment = bling.Assignment(u'Blingy', folderpath, u'thumb', True, u'Random', u'default')

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, bling.Renderer))


class TestRenderer(TestCase):
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or bling.Assignment(u'Blingy', u'/news', u'thumb', True, u'Random', u'default')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        bling_title = u'Blingy'
        self.folder.invokeFactory('Image', id='bling')
        self.folder.bling.setImage(icon)
        bling_link = self.folder.bling.absolute_url()
        self.portal.portal_workflow.doActionFor(self.folder, 'publish')
        fpath = '/'+'/'.join(self.folder.getPhysicalPath()[-2:])
        r = self.renderer(context=self.portal, assignment=bling.Assignment(bling_title, fpath, u'thumb', True, u'Random', u'default'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(bling_title in output)
        self.failUnless(bling_link in output)

class TestRendererTiming(TestCase):

    def afterSetUp(self):
        self.mocker = Mocker()
        tm = self.mocker.replace("time.time")
        tm()

        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        self.renderer = getMultiAdapter((context, request, view, manager, bling.Assignment(u'Blingy', u'/news', u'thumb', True, u'Random', u'default')), IPortletRenderer)

    def beforeTearDown(self):
        self.mocker.restore()

    def _getResultIndex(self, time, arrayLength):
        self.mocker.result(time)
        self.mocker.replay()
        return self.renderer.getResultsIndex(arrayLength)

    def _timingByPeriod(self, changeStr, periodInSeconds):
        self.renderer.data.change = changeStr
        self.assertEquals(self._getResultIndex(0, 2), 0)
        self.assertEquals(self._getResultIndex(periodInSeconds, 2), 1)
        self.assertEquals(self._getResultIndex(2*periodInSeconds-1, 2), 1)
        self.assertEquals(self._getResultIndex(2*periodInSeconds, 2), 0)
        
    def testTimingBySecond(self):
        self._timingByPeriod(u'Each second', 1)

    def testTimingByMinute(self):
        self._timingByPeriod(u'Each minute', 60)
        
    def testTimingByHour(self):
        self._timingByPeriod(u'Each hour', 3600)

    def testTimingByDay(self):
        self._timingByPeriod(u'Each day', 86400)

    def testTimingByWeek(self):
        self._timingByPeriod(u'Each week', 604800)

    def testTimingByMonth(self):
        dt = self.mocker.replace("datetime.datetime")
        dt.now()
        self.renderer.data.change = u'Each month'
        self.assertEquals(self._getResultIndex(datetime(2011,1,1),2), 1)
        self.assertEquals(self._getResultIndex(datetime(2011,1,2),2), 1)
        self.assertEquals(self._getResultIndex(datetime(2011,2,1),2), 0)
        self.assertEquals(self._getResultIndex(datetime(2011,3,1),2), 1)

    def testTimingByYear(self):
        dt = self.mocker.replace("datetime.datetime")
        dt.now()
        self.renderer.data.change = u'Each year'
        self.assertEquals(self._getResultIndex(datetime(2011,1,1),2), 1)
        self.assertEquals(self._getResultIndex(datetime(2011,1,2),2), 1)
        self.assertEquals(self._getResultIndex(datetime(2012,1,1),2), 0)
        self.assertEquals(self._getResultIndex(datetime(2013,3,1),2), 1)

                

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    suite.addTest(makeSuite(TestRendererTiming))
    return suite
