##############################################################################
#
# Copyright (c) 2006, 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Task Service Implementation

"""
__docformat__ = 'restructuredtext'

from z3c.taskqueue import interfaces
from zope import component
from zope.app.publication.zopepublication import ZopePublication
import logging
import zope.interface
import zope.location
import z3c.taskqueue


log = logging.getLogger('z3c.taskqueue')


def databaseOpened(event, productName='z3c.taskqueue'):
    """Start the queue processing services based on the
       settings in zope.conf"""
    log.info('handling event IDatabaseOpenedEvent')
    storeDBReference(event)
    root_folder = getRootFolder(event)

    from zope.app.appsetup.product import getProductConfiguration
    configuration = getProductConfiguration(productName)
    startSpecifications = getStartSpecifications(configuration)

    for sitesIdentifier, servicesIdentifier in startSpecifications:
        sites = getSites(sitesIdentifier, root_folder)
        for site in sites:
            startOneService(site, servicesIdentifier)


def getRootFolder(event):
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    return root_folder


def getStartSpecifications(configuration):
    """get a list of sites/services to start"""
    if configuration is not None:
        autostart = configuration.get('autostart', '')
        autostartParts = [name.strip()
                        for name in autostart.split(',')]

        specs = [name.split('@') for name in autostartParts if name]
        return specs
    else:
        return []


def getSites(sitesIdentifier, root_folder):
    # we search only for sites at the database root level
    if sitesIdentifier == '':
        return [root_folder]
    elif sitesIdentifier == '*':
        return getAllSites(root_folder)
    else:
        site = getSite(sitesIdentifier, root_folder)
        if site is not None:
            return [site]
        else:
            return []


def getAllSites(root_folder):
    sites = []
    # do not forget to include root folder as it might have registered services
    sites.append(root_folder)
    root_values = root_folder.values()
    for folder in root_values:
        if zope.location.interfaces.ISite.providedBy(folder):
            sites.append(folder)
    return sites


def getSite(siteName, root_folder):
    site = root_folder.get(siteName)
    if site is None:
        log.error('site %s not found' % siteName)
    return site


def getAllServices(site, root_folder):
    sm = site.getSiteManager()
    services = list(
        sm.getUtilitiesFor(interfaces.ITaskService))
    # filter out services registered in root
    root_sm = root_folder.getSiteManager()
    if sm != root_sm:
        rootServices = list(root_sm.getUtilitiesFor(
            interfaces.ITaskService))
        services = [s for s in services
                       if s not in rootServices]
    services = [service for name, service in services]
    return services


def getSiteName(site):
    siteName = getattr(site, '__name__', '')
    if siteName is None:
        siteName = 'root'
    return siteName


def startOneService(site, serviceName):
    service = getService(site, serviceName)
    if service is not None:
        if not service.isProcessing():
            service.startProcessing()
            if service.isProcessing():
                siteName = getSiteName(site)
                msg = 'service %s on site %s started'
                log.info(msg % (serviceName, siteName))
        return service
    else:
        return None


def getService(site, serviceName):
    service = component.queryUtility(interfaces.ITaskService,
        context=site, name=serviceName)
    if service is not None:
        return service
    else:
        siteName = getSiteName(site)
        msg = 'service %s on site %s not found'
        log.error(msg % (serviceName, siteName))
        return None


def storeDBReference(db):
    z3c.taskqueue.GLOBALDB = db


def storeDBReferenceOnDBOpened(event):
    storeDBReference(event.database)
