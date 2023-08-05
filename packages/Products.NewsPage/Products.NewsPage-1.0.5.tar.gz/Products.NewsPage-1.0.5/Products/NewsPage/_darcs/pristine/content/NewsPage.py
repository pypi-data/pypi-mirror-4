# -*- coding: utf-8 -*-
#
# File: NewsPage.py
#
# Copyright (c) 2008 by 
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

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.ATContentTypes import ATCTMessageFactory as _


from Products.NewsPage.config import *
from Products.CMFCore.utils import getToolByName

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((
    ReferenceField('primary_news_item',
                   relationship = 'relatesTo',
                   multiValued = False,
                   widget = ReferenceBrowserWidget(
         allow_search = True,
         allow_browse = True,
         show_indexes = False,
         force_close_on_insert = True,
         label = _(u'primary_news_item', default=u'1. Nyhetssak'),
         description = '',
         )),
    ReferenceField('secondary_news_item',
                   relationship = 'relatesTo2',
                   multiValued = False,
                   widget = ReferenceBrowserWidget(
         allow_search = True,
         allow_browse = True,
         show_indexes = False,
         force_close_on_insert = True,
         label = _(u'primary_news_item', default=u'2. Nyhetssak'),
         description = '',
         )),    
    ReferenceField('tertiary_news_item',
                   relationship = 'relatesTo3',
                   multiValued = False,
                   widget = ReferenceBrowserWidget(
         allow_search = True,
         allow_browse = True,
         show_indexes = False,
         force_close_on_insert = True,
         label = _(u'primary_news_item', default=u'3. Nyhetssak'),
         description = '',
         )),
    StringField('show_review_state', default="internally_published"),
    LinesField('include_paths',),
    LinesField('exclude_paths',),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

NewsPage_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

def filter_exclude_paths(objects, paths):
    """Removes objects with paths."""
    objects_ = []
    for object in objects:
        for path in paths:
            if '/'.join(object.getPhysicalPath()).startswith(path):
                break
        else:
            objects_.append(object)
    return objects_

class NewsPage(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.INewsPage)

    meta_type = 'NewsPage'
    _at_rename_after_creation = True

    schema = NewsPage_schema

    ##code-section class-header #fill in your manual code here
    exclude_from_nav = True    
    ##/code-section class-header

    # Methods

    def check_b_start(self, b_start):
        if b_start == 0:
            return 1

    def get_news_items(self):
        """Returns a list with news item newsitems."""
        query = {}
        query["review_state"] = self.getShow_review_state()
        query["sort_on"] = "effective"
        query["sort_order"] = "reverse"
        query["Type"] = "News Item"
        if self.getInclude_paths():
            query['path'] = self.getInclude_paths()
        portal_catalog = getToolByName(self, 'portal_catalog')
        newsitems = map(lambda x: x.getObject(), portal_catalog.searchResults(**query))
        selected = [self.getPrimary_news_item(), self.getSecondary_news_item(), self.getTertiary_news_item()]
        selected = filter(None, selected)
        for item in selected:
            try:
                newsitems.remove(item)
            except ValueError:
                print 'not removing %s from news listing' % item
        objects = selected + newsitems
        if self.getExclude_paths():
            objects = filter_exclude_paths(objects, self.getExclude_paths())
        return objects

    def primary_news(self):
        """Returns the top 3 news item objects."""
        objects = []
        brains = self.get_news_items()
        for brain in brains[:3]:
            objects.append(brain)
        return objects

    def secondary_news(self):
        """Returns rest of the news."""
        objects = []
        brains = self.get_news_items()
        for brain in brains[3:]:
            objects.append(brain)
        return objects

registerType(NewsPage, PROJECTNAME)
# end of class NewsPage

##code-section module-footer #fill in your manual code here
##/code-section module-footer



