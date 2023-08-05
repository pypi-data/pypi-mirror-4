# -*- coding: utf-8 -*-
#
# File: Quote.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ifQuotes.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    TextField(
        name='quote',
        allowable_content_types=('text/plain',),
        widget=TextAreaWidget(
            label='Quote',
            label_msgid='ifQuotes_label_quote',
            i18n_domain='ifQuotes',
        ),
    ),
    StringField(
        name='author',
        widget=StringField._properties['widget'](
            label='Author',
            label_msgid='ifQuotes_label_author',
            i18n_domain='ifQuotes',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Quote_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Quote(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IQuote)

    meta_type = 'Quote'
    portal_type = 'Quote'
    content_icon = 'document_icon.gif'
    _at_rename_after_creation = True

    schema = Quote_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

registerType(Quote, PROJECTNAME)
# end of class Quote

##code-section module-footer #fill in your manual code here
##/code-section module-footer



