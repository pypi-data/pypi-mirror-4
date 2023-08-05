#from Products.CMFCore.utils import getToolByName
from Products.cron4plone.browser.configlets.cron_configuration import ICronConfiguration
from Products.cron4plone.tools.configlet_util import ConfigletUtil


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('Products.cron4plone_various.txt') is None:
        return

    # Add additional setup code here
    portal = context.getSite()
    sm = portal.getSiteManager()

    if not sm.queryUtility(ICronConfiguration, name='cron4plone_config'):
        sm.registerUtility(ConfigletUtil(),
                           ICronConfiguration,
                           'cron4plone_config')
