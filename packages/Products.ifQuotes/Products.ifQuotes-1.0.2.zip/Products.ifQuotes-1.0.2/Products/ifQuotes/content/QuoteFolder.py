# -*- coding: utf-8 -*-
#
# File: QuoteFolder.py
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

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

QuoteFolder_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class QuoteFolder(BaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IQuoteFolder)

    meta_type = 'QuoteFolder'
    _at_rename_after_creation = True
    content_icon = 'folder_icon.gif'

    schema = QuoteFolder_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

registerType(QuoteFolder, PROJECTNAME)
# end of class QuoteFolder

##code-section module-footer #fill in your manual code here
##/code-section module-footer



