from Products.CMFCore.utils import getToolByName

default_profile = 'profile-Products.cron4plone:default'


def upgrade(upgrade_product, version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            p = getToolByName(context, 'portal_quickinstaller').get(
                    upgrade_product)
            setattr(p, 'installedversion', version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func


@upgrade('cron4plone', '1.1.10')
def upgrade_to_1_1_10(context):
    """ well.. do nothing really """
    print "Upgrading to 1.1.10"
