from plone.app.upgrade.utils import loadMigrationProfile


def upgrade_to_v11(context):
    loadMigrationProfile(context, 'profile-simplelayout.ui.base:to_v11')
