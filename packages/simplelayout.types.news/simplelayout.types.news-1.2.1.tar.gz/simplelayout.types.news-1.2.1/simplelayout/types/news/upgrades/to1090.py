from ftw.upgrade import UpgradeStep
from simplelayout.types.news.newsfolder import NewsFolder
from zope.interface import alsoProvides
from simplelayout.base.interfaces import ISimpleLayoutCapable


class UpgradeTypes(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-simplelayout.types.news.upgrades:1090')

class RemoveEditActions(UpgradeStep):

    def __call__(self):
        self.actions_remove_type_action('News', 'edit')
        self.actions_remove_type_action('NewsFolder', 'edit')


class MigrateNewsFolders(UpgradeStep):

    def __call__(self):
        cat = self.getToolByName('portal_catalog')
        results = cat.searchResults(portal_type='NewsFolder')
        for brain in results:
            obj = brain.getObject()
            self.migrate_class(obj, NewsFolder)
            alsoProvides(obj, ISimpleLayoutCapable)
