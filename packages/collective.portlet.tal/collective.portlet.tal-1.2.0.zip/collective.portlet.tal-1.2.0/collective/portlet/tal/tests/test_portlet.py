from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.tal import talportlet

from collective.portlet.tal.tests.base import TestCase

from zope.pagetemplate.pagetemplate import PTRuntimeError
from zExceptions import NotFound

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlet.tal.TALPortlet')
        self.assertEquals(portlet.addview, 'collective.portlet.tal.TALPortlet')

    def testInterfaces(self):
        portlet = talportlet.Assignment(title=u"Test", tal=u"<b tal:content='context/Title'/>")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='collective.portlet.tal.TALPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data=dict(title=u"Test", tal=u"<b tal:content='context/Title'/>"))

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], talportlet.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = talportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, talportlet.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        
        assignment = talportlet.Assignment(title=u"Test", tal=u"<b tal:content='context/Title'/>")

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, talportlet.Renderer))

class TestRenderer(TestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        
        assignment = assignment or talportlet.Assignment(title=u"Test", tal=u"<b tal:content='context/Title'/>")
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        self.folder.setTitle('Foo')
        r = self.renderer(context=self.folder, assignment=talportlet.Assignment(title=u"Test", tal=u"<b tal:content='context/Title'/>"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.assertEquals(u'<b>%s</b>' % self.folder.Title(), output.strip())
        
    def test_render_runtime_error(self):
        # we're in restricted land boys and girls
        self.folder.setTitle('Foo')
        r = self.renderer(context=self.folder, assignment=talportlet.Assignment(title=u"Test", 
                                tal=u"<b tal:content='python:context._owner'/>"))
        r = r.__of__(self.folder)
        r.update()
        self.assertRaises(PTRuntimeError, r.render)
        
    def test_render_runtime_notfound(self):
        self.folder.setTitle('Foo')
        r = self.renderer(context=self.folder, assignment=talportlet.Assignment(title=u"Test", 
                                tal=u"<b tal:content='context/_owner'/>"))
        r = r.__of__(self.folder)
        r.update()
        self.assertRaises(NotFound, r.render)
        
    def testSetInvalidZPTSyntax(self):
        self.folder.setTitle('Foo')
        r = self.renderer(context=self.folder, assignment=talportlet.Assignment(title=u"Test", 
                                tal=u"<tal:content='"))
        r = r.__of__(self.folder)
        r.update()
        self.assertRaises(PTRuntimeError, r.render)
                
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
