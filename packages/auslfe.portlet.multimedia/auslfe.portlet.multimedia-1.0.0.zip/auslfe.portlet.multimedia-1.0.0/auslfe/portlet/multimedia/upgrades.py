from Products.CMFCore.utils import getToolByName
from auslfe.portlet.multimedia import logger

upgrade_profile = 'profile-auslfe.portlet.multimedia:migrate_to_1000'


def upgrade(upgrade_product, version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            p = getToolByName(context, 'portal_quickinstaller').get(upgrade_product)
            setattr(p, 'installedversion', version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func


@upgrade('auslfe.portlet.multimedia', '1.0.0')
def to_1000(context):
    """
    """
    logger.info('Upgrading auslfe.portlet.multimedia to version 1.0.0')
    context.runAllImportStepsFromProfile(upgrade_profile)
    logger.info('Removed javascript')
