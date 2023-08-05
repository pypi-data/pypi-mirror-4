from Products.CMFPlone import utils
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

class IQuoteView(Interface):
    """Interface for Quote View"""

class QuoteView(BrowserView):    
    implements(IQuoteView)

    __call__ = ViewPageTemplateFile('templates/quote_view.pt')


