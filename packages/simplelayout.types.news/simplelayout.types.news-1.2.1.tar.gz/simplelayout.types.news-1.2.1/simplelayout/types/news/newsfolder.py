from Products.ATContentTypes.content import folder
from AccessControl import ClassSecurityInfo
from simplelayout.types.news.config import PROJECTNAME
from simplelayout.base.interfaces import ISimpleLayoutCapable
from zope.interface import implements
from DateTime import DateTime
from Products.Archetypes.atapi import registerType
from simplelayout.types.news.interfaces import INewsFolder

class NewsFolder(folder.ATFolder):

    implements(INewsFolder, ISimpleLayoutCapable)
    security = ClassSecurityInfo()

    def getDefaultEffectiveDate(self):
        return DateTime().Date()


registerType(NewsFolder, PROJECTNAME)