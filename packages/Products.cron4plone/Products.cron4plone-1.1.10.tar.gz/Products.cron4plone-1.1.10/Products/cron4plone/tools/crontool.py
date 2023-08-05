import transaction
from DateTime import DateTime

from OFS import SimpleItem
from OFS.PropertyManager import PropertyManager
#from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression, getExprContext

from Products.cron4plone.tools.crontab_utils import *
from Products.cron4plone.browser.configlets.cron_configuration import ICronConfiguration
from Products.cron4plone.config import PROJECTNAME
import logging

logger = logging.getLogger(PROJECTNAME)


class CronTool(UniqueObject, PropertyManager,
               SimpleItem.SimpleItem, ActionProviderBase):

    """CronTool"""
    meta_type = 'Cron4Plone Tool'
    id = 'CronTool'
    isPrincipiaFolderish = True

    manage_options = PropertyManager.manage_options + \
                     SimpleItem.SimpleItem.manage_options

    _properties = (
        {'id': 'cron_history',
         'type': 'text',
         'mode': 'r'},
    )

    # Standard security settings
    security = ClassSecurityInfo()

    def __init__(self):
        """
        """
        self.cron_history = {}

    def _getCronData(self):
        """
        return the cron data.
        """
        sm = self.getSiteManager()
        data = sm.queryUtility(ICronConfiguration, name='cron4plone_config')
        jobs = []

        for id, job in enumerate(data.cronjobs):
            splittedDict = splitJob(job)
            splittedDict['id'] = id
            jobs.append(splittedDict)

        return jobs

    def run_tasks(self, context):
        """
        run the scheduled tasks
        """
        now = DateTime()
        logger.info("running tasks. (%s)" % str(now))
        crondata = self._getCronData()
        for line in crondata:
            logger.debug(line)
            id = line['id']

            if id in self.cron_history.keys():
                last_executed = self.cron_history[id]['last_executed']
            else:
                logger.debug("task %s never ran before.." % id)
                last_executed = getNoSecDate(now)
                self.cron_history[id] = {'last_executed': last_executed}
                self._p_changed = 1

            schedule = line['schedule']
            assert len(schedule) == 4, 'number of parameters invalid'
            next = getNextScheduledExecutionTime(schedule, last_executed)

            if not isPending(schedule, last_executed):
                logger.debug("plugin %s will run on: %s" % (id, next))
            else:
                logger.debug("Running task %s" % id)
                expression = line['expression']
                expr = Expression(expression)
                e_context = getExprContext(context)
                result = expr(e_context)
                #logger.debug(result)
                logger.debug("task finished")
                self.cron_history[id]['last_executed'] = getNoSecDate(now)
                self._p_changed = 1

            transaction.commit() # necessary???
