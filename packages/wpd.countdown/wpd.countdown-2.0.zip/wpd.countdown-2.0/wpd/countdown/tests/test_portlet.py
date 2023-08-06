from zope.component import getUtility, getMultiAdapter

from datetime import datetime
from datetime import timedelta

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from wpd.countdown.browser import wpdcountdown

from wpd.countdown.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='wpd.countdown.WPDcountdown')
        self.assertEquals(portlet.addview,
                          'wpd.countdown.WPDcountdown')

    def test_interfaces(self):
        portlet = wpdcountdown.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = wpdcountdown.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, wpdcountdown.Renderer))

    def test_validate_dates(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = wpdcountdown.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        
        now = datetime.now()
        today = datetime(now.year,now.month,now.day)
        
        # Fake the WPD day to 1 day in the future
        renderer.day = today + timedelta(days=1)
        self.failUnless(renderer.isFuture)

        # Fake the WPD day to 1 day in the past
        renderer.day = today + timedelta(days=-1)
        self.failUnless(renderer.isPast)
        
        # Fake the WPD day to today
        renderer.day = today
        self.failUnless(renderer.isToday)        
        
class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or wpdcountdown.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal,
                          assignment=wpdcountdown.Assignment())
        r = r.__of__(self.folder)
        r.update()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
