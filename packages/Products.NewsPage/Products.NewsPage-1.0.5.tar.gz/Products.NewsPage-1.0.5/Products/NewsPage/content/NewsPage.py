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
from Products.NewsPage import NewsPageMessageFactory as _

from Products.NewsPage.config import *
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

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
         label = _(u'primary_news_item', default=u'Primary news item'),
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
         label = _(u'secondary_news_item', default=u'Secondary news item'),
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
         label = _(u'tertiary_news_item', default=u'Tertiary news item'),
         description = '',
         )),
    StringField('show_review_state', default="internally_published",
                         widget=StringWidget(label = _(u'show_review_state', default=u'Review states to show, for example published'),),),
    LinesField('include_paths',
         widget=LinesWidget(label = _(u'include_paths', default=u'Paths to include (complete Zope path)')),),
    LinesField('exclude_paths',
               widget=LinesWidget(label = _(u'exclude_paths', default=u'Paths to exclude (complete Zope path)')),),
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

from plone.portlets.interfaces import ILocalPortletAssignable

class NewsPage(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.INewsPage, ILocalPortletAssignable)

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
        query["review_state"] = self.getShow_review_state().split(',')
        query["sort_on"] = "effective"
        query["sort_order"] = "reverse"
        query["Type"] = "News Item"
        query["effectiveRange"] = DateTime()
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



