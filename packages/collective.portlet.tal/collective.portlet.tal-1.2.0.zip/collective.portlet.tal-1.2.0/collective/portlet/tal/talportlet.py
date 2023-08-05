from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from collective.portlet.tal import TALPortletMessageFactory as _

from Acquisition import aq_inner, aq_base

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

class ITALPortlet(IPortletDataProvider):
    """A TAL portlet - allows TAL code to be entered in the browser and
    executed.
    """
    
    title = schema.TextLine(title=_(u"Title"),
                             description=_(u"A title to show in the admin UI"),
                             required=True)
                             
    tal = schema.Text(title=_(u"TAL code"),
                      description=_(u"TAL code which will be executed when the portlet is rendered"),
                      required=True, default=u"""\
<dl class="portlet portlet${portlet_type_name}"
    tal:define="portal_state context/@@plone_portal_state;
                context_state context/@@plone_context_state;">

    <dt class="portletHeader">
        <span class="portletTopLeft"></span>
        <span>
           Header
        </span>
        <span class="portletTopRight"></span>
    </dt>

    <dd class="portletItem odd">
        Body text
    </dd>
    
    <dd class="portletFooter">
        <span class="portletBotomLeft"></span>
        <span>
           Footer
        </span>
        <span class="portletBottomRight"></span>
    </dd>

</dl>
""")


class Assignment(base.Assignment):
    implements(ITALPortlet)

    title = u"" # overrides the readonly property method from the base class

    def __init__(self, title=u"", tal=u""):
        self.pt = ZopePageTemplate(id='__tal_portlet__')
        self.title = title
        self.tal = tal
        
    def _get_tal(self):
        return self.pt.read()
    def _set_tal(self, value):
        self.pt.pt_edit(value, 'text/html')
    tal = property(_get_tal, _set_tal)

class Renderer(base.Renderer):
    
    def render(self):
        context = aq_inner(self.context)
        pt = aq_base(self.data.pt).__of__(context)
        return pt()
        
class AddForm(base.AddForm):
    form_fields = form.Fields(ITALPortlet)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(ITALPortlet)