from plone.app.upgrade.utils import loadMigrationProfile


def upgrade_newsfolder(context):
    loadMigrationProfile(context, 'profile-simplelayout.types.news:newsfolder')

