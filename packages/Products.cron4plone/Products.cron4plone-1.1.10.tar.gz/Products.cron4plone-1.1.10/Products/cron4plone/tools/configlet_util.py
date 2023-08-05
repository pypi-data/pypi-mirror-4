from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from OFS.SimpleItem import SimpleItem

from Products.cron4plone.browser.configlets.cron_configuration import ICronConfiguration


def form_adapter(context):
    return getUtility(ICronConfiguration, name='cron4plone_config', context=context)


class ConfigletUtil(SimpleItem):
    implements(ICronConfiguration)

    def __call__(self):
        print self.cronjobs

    cronjobs = FieldProperty(ICronConfiguration['cronjobs'])
