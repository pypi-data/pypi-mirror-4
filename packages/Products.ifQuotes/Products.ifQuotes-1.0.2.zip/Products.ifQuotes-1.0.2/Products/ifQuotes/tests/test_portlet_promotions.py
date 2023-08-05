from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from Products.ifQuotes.portlets import quotes

from Products.ifQuotes.tests.base import ifQuotesTestCase

class TestPortlet(ifQuotesTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner() 
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='RandomQuote')
        self.assertEquals(portlet.addview, 'RandomQuote')

    def testInterfaces(self):
        portlet = quotes.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='RandomQuote')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.rightcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], quotes.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = quotes.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, quotes.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = quotes.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, quotes.Renderer))

class TestRenderer(ifQuotesTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('QuoteFolder', 'cf1')
        self.portal.invokeFactory('QuoteFolder', 'cf2')
        self.portal.cf1.invokeFactory('Quote', 'p1')
        self.portal.cf1.invokeFactory('Quote', 'p2')
        self.portal.cf1.invokeFactory('Quote', 'p3')
        self.portal.cf1.invokeFactory('Quote', 'p4')
        self.portal.cf1.invokeFactory('Quote', 'p5')
        self.portal.cf2.invokeFactory('Quote', 'p6')
        self.portal.cf2.invokeFactory('Quote', 'p7')

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or quotes.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_header(self):
        r = self.renderer(context=self.portal.cf1, assignment=quotes.Assignment(header=u"this is the header"))
        self.assertEquals(u"this is the header",r.header())

    def test_footer(self):
        r = self.renderer(context=self.portal.cf1, assignment=quotes.Assignment(footer=u"this is the footer"))
        self.assertEquals(u"this is the footer",r.footer())

    def test_more_url(self):
        r = self.renderer(context=self.portal.cf1, assignment=quotes.Assignment(more_url="http://foo.com/foo"))
        self.assertEquals("http://foo.com/foo",r.more_url())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
