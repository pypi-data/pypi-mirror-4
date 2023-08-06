from DateTime import DateTime
from simplelayout.types.common.content.simplelayout_schemas import imageSchema
from simplelayout.types.common.content import page
from simplelayout.types.common.content.page import Page

from AccessControl import ClassSecurityInfo
from simplelayout.types.news.config import PROJECTNAME
from simplelayout.types.common.content.simplelayout_schemas import finalize_simplelayout_schema
from zope.interface import implements
from simplelayout.types.news.interfaces import INews
from simplelayout.base.interfaces import ISimpleLayoutCapable

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType


news_schema = page.page_schema.copy() + imageSchema.copy()

news_schema['effectiveDate'].required = True
news_schema['effectiveDate'].default_method = 'getDefaultEffectiveDate'
news_schema.changeSchemataForField('effectiveDate', 'default')
news_schema.changeSchemataForField('expirationDate', 'default')
finalize_simplelayout_schema(news_schema, folderish=True)


class News(Page):

    implements(INews, ISimpleLayoutCapable)
    security = ClassSecurityInfo()

    schema = news_schema

    def getDefaultEffectiveDate(self):
        return DateTime().Date()

    security.declarePublic('show_description')
    def show_description(self):
        return False

registerType(News, PROJECTNAME)
