import logging

from App.config import getConfiguration

from z3c.taskqueue.startup import getRootFolder
from z3c.taskqueue.startup import getStartSpecifications
from z3c.taskqueue.startup import startOneService, storeDBReference

log = logging.getLogger('five.taskqueue')


def startServices(root_folder):
    configuration = getTaskqueueConfiguration()
    startSpecifications = getStartSpecifications(configuration)

    for siteName, serviceName in startSpecifications:
        log.debug('Starting service %s from site %s' % (serviceName, siteName))
        site = getSite(siteName, root_folder)
        if site is None:
            continue
        started = startOneService(site, serviceName)
        if not started:
            msg = 'service %s from site %s was not started.'
            log.warn(msg % (serviceName, siteName))
        else:
            log.debug('Service %s from site %s started.' % (serviceName, siteName))


def databaseOpened(event):
    """Start the queue processing services based on the
       settings in zope.conf"""
    log.info('handling event IDatabaseOpenedEvent')
    storeDBReference(event.database)
    root_folder = getRootFolder(event)
    startServices(root_folder)


def getSite(siteName, root_folder):
    try:
        site = root_folder._getOb(siteName)
    except AttributeError:
        log.error('site %s not found' % siteName)
        site = None
    return site


def getTaskqueueConfiguration():
    config = getConfiguration()
    if not hasattr(config, 'product_config'):
        return
    product_config = config.product_config
    if config is None:
        return
    return product_config.get('five.taskqueue', None)
