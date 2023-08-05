# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

from logging import getLogger
logger = getLogger('collective.taxonomysupport')


def upgrade(upgrade_product, version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            p = getToolByName(context, 'portal_quickinstaller').get(upgrade_product)
            setattr(p, 'installedversion', version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func


@upgrade('collective.taxonomysupport', '1.2.1')
def upgrade1_2_0_to_1_2_1(context):
    logger.info("Updating actions info")
    context.runImportStepFromProfile(profile_id='profile-collective.taxonomysupport:default',
                                     step_id='actions')

    context.runImportStepFromProfile(profile_id='profile-collective.taxonomysupport:default',
                                     step_id='action-icons')
