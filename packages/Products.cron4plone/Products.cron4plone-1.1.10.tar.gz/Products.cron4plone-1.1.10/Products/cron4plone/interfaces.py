from zope.interface import Interface
#from zope.interface import Attribute
#from Products.cron4plone.browser.configlets.cron_configuration import ICronConfiguration


class ICronTickView(Interface):
    """Marker interface to display google search results"""


class ICronTool(Interface):
    """Marker interface for the CronTool"""
