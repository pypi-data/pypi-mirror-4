from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
import random
from Acquisition import aq_inner
from plone.memoize.instance import memoize

class IRandomQuote(IPortletDataProvider):
    """ Interface for random quote portlet """
    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)

    footer = schema.TextLine(title=_(u"Portlet footer"),
                             description=_(u"Text to be shown in the footer"),
                             required=False)

    more_url = schema.ASCIILine(title=_(u"Details link"),
                                  description=_(u"If given, the header and footer "
                                                  "will link to this URL."),
                                  required=False)

class Assignment(base.Assignment):
    implements(IRandomQuote)
    header = u''
    footer = u''
    more_url = ''

    def __init__(self, header=u"", footer=u"", more_url=''):
        self.header = header
        self.footer = footer
        self.more_url = more_url

    @property
    def title(self):
        return self.header

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/randomquote.pt')

    def has_link(self):
        return bool(self.data.more_url)
        
    def has_footer(self):
        return bool(self.data.footer)

#    @memoize
    def random_quote(self):
        """ Return one of the quotes published in the site """

#        context = aq_inner(self.context)#utils.context(self)
        catalog = getToolByName(self.context, "portal_catalog")

        results = catalog(meta_type='Quote',
                          review_state='published')

        if results:
            return random.choice(results).getObject()
        else:
            return None


class AddForm(base.AddForm):
    form_fields = form.Fields(IRandomQuote)
    label = _(u"Add New Random Quote")
    description = _(u"This portlet displays a random Quote.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IRandomQuote)
    label = _(u"Edit Random Quote")
    description = _(u"This portlet displays a random Quote.")

