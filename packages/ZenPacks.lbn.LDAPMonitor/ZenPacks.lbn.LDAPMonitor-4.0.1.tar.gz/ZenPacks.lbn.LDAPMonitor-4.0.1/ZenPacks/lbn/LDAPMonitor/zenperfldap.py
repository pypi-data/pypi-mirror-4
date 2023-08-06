#
# Copyright 2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#

import logging, ldap, time
import pysamba.twisted.reactor
from zope.component import queryUtility
from zope.interface import implements
from twisted.internet import defer, reactor
from twisted.python.failure import Failure

from Products.ZenCollector.daemon import CollectorDaemon
from Products.ZenCollector.interfaces import ICollectorPreferences, \
    IDataService, IEventService, IScheduledTask, IScheduledTaskFactory
from Products.ZenCollector.tasks import SimpleTaskFactory,\
    SimpleTaskSplitter, TaskStates
from Products.ZenEvents.ZenEventClasses import Error, Clear, Critical
from Products.ZenUtils.observable import ObservableMixin

# We retrieve our configuration data remotely via a Twisted PerspectiveBroker
# connection. To do so, we need to import the class that will be used by the
# configuration service to send the data over, i.e. DeviceProxy.
from Products.ZenUtils.Utils import unused
from Products.ZenCollector.services.config import DeviceProxy
unused(DeviceProxy)

import config
from monparsers import parse

#
# creating a logging context for this module to use
#
log = logging.getLogger("zen.zenperfldap")

# hmmm - don't worry about PEER TLS - there are so many borked installations out there...
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)



# Create an implementation of the ICollectorPreferences interface so that the
# ZenCollector framework can configure itself from our preferences.
class ZenPerfLDAPPreferences(object):

    implements(ICollectorPreferences)

    def __init__(self):
        """
        Construct a new ZenPerfSqlPreferences instance and provide default
        values for needed attributes.
        """
        self.collectorName = "zenperfldap"
        self.defaultRRDCreateCommand = None
        self.cycleInterval = 5 * 60 # seconds
        self.configCycleInterval = 20 # minutes
        self.options = None
        self.maxTasks = 1

        # the configurationService attribute is the fully qualified class-name
        # of our configuration service that runs within ZenHub
        self.configurationService = 'ZenPacks.lbn.LDAPMonitor.services.LDAPConfigService'

    def buildOptions(self, parser):
        parser.add_option('--debug', dest='debug', default=False,
                          action='store_true',
                          help='Increase logging verbosity.')
        parser.add_option('--sync', dest='sync', default=False,
                               action="store_true",
                               help="Force Synchronous query execution.")

    def postStartup(self):
        # turn on debug logging if requested
        logseverity = self.options.logseverity


class ZenPerfLDAPTask(ObservableMixin):
    """
    gather ldap monitoring info and push it into rrd
    """
    implements(IScheduledTask)

    def __init__(self, taskName, deviceId, scheduleIntervalSeconds, taskConfig):
        """
        Construct a new task instance to get SQL data.

        @param deviceId: the Zenoss deviceId to watch
        @type deviceId: string
        @param taskName: the unique identifier for this task
        @type taskName: string
        @param scheduleIntervalSeconds: the interval at which this task will be
               collected
        @type scheduleIntervalSeconds: int
        @param taskConfig: the configuration for this task
        """
        super(ZenPerfLDAPTask, self).__init__()

        self.name = taskName
        self.configId = deviceId
        self.interval = scheduleIntervalSeconds
        self.state = TaskStates.STATE_IDLE

        self._taskConfig = taskConfig
        self._devId = deviceId
        self._manageIp = self._taskConfig.manageIp
        self._datapoints = self._taskConfig.datapoints
        self._thresholds = self._taskConfig.thresholds

        self._dataService = queryUtility(IDataService)
        self._eventService = queryUtility(IEventService)
        self._preferences = queryUtility(ICollectorPreferences, "zenperfldap")

    def _failure(self, result, summary='Could not fetch statistics', severity=Error, comp=None):
        """
        Errback for an unsuccessful asynchronous connection or collection request.
        """
        err = result.getErrorMessage()
        log.error("Device %s: %s", self._devId, err)
        collectorName = self._preferences.collectorName

        self._eventService.sendEvent(dict(
            summary=summary,
            message=err,
            component=comp or collectorName,
            eventClass='/Status/LDAP',
            device=self._devId,
            severity=severity,
            agent=collectorName,
            ))

         # give the result to the rest of the errback chain
        return result

    def _sendEvents(self, components):
        """
        Send Error and Clear events 
        """
        events = []
        errors = []
        for comp, severity in components.iteritems():
            event = dict(
                summary = "Could not fetch statistics",
                message = "Could not fetch statistics",
                eventClass = '/Status/LDAP',
                device = self._devId,
                severity = severity,
                agent = self._preferences.collectorName,
                )
            if comp: 
                event['component'] = comp
            if isinstance(severity, Failure):
                event['message'] = severity.getErrorMessage()
                event['severity'] = Error
                errors.append(event)
            else:
                events.append(event)

        if len(errors) == len(components) > 0:
            event = errors[0]
            del event['component']
            events.append(event)
        else:
            events.extend(errors)

        for event in events:
            self._eventService.sendEvent(event)

    def _collectSuccessful(self, results={}):
        """
        Callback for a successful fetch of monitor stats from the remote device.
        """
        log.debug("Successful collection from %s [%s], results=%s",
                  self._devId, self._manageIp, results)

        compstatus = {}
        for dpname, comp, rrdP, rrdT, rrdC, tmin, tmax in self._datapoints:
            value = results.get(dpname, 0)
            compstatus[comp] = Clear
            try: 
                self._dataService.writeRRD(rrdP, float(value), rrdT, rrdC, min=tmin, max=tmax)
            except Exception, e:
                compstatus[comp] = Failure(e)
        self._sendEvents(compstatus)
        return results

    def doTask(self):
        log.debug("Polling for stats from %s [%s]", self._devId, self._manageIp)

        ldapuri = self._taskConfig.ldapuri
        ldapcreds = self._taskConfig.credentials
        ldapfilter = self._taskConfig.searchFilter

        log.debug("%s %s %s" % (ldapuri, ldapcreds[0], ldapfilter))

        start_time = time.time()

        slapd = ldap.initialize(ldapuri)
            
        try:
            slapd.simple_bind_s(*ldapcreds)
        except ldap.INVALID_CREDENTIALS:
            msg = 'authentication failure: %s/%s: check credentials!' % (ldapuri, ldapcreds[0])
            return self._failure(Failure(ldap.LDAPError(msg)))
	except ldap.SERVER_DOWN:
	    return self._failure(Failure(ldap.LDAPError('server uncontactable')), 
                                 summary='LDAP server uncontactable', 
                                 severity=Critical)
        except ldap.LDAPError, e:
	    return self._failure(Failure(e))
        
        # seems some ldap implementations require a + attr list to retrieve operational
        # attributes, but others don't :(
        try:
	    # no timeout - we're using this call to set response time ...
            resultseq = slapd.search_s(ldapfilter, ldap.SCOPE_SUBTREE, attrlist=['*', '+'])
        except Exception, e:
            msg = 'search failure(%s): %s?%s: is cn=monitor activated?' % (str(e), ldapuri, ldapfilter)
            return self._failure(Failure(ldap.LDAPError(msg)))

        slapd.unbind()

        resp_time = time.time() - start_time

        # get monparsers to sort out what was returned ...
        results = parse(resultseq, {'responsetime':resp_time})


        #d = defer.maybeDeferred(self._ldapconn.query, queries,
        #                        sync=self._preferences.options.sync)

        #d.addCallback(self._collectSuccessful)
        #d.addErrback(self._failure)

        # returning a Deferred will keep the framework from assuming the task
        # is done until the Deferred actually completes
        #return d
        
        self._collectSuccessful(results)

    def cleanup(self):
        pass

#
# Collector Daemon Main entry point
#
if __name__ == '__main__':
    myPreferences = ZenPerfLDAPPreferences()
    myTaskFactory = SimpleTaskFactory(ZenPerfLDAPTask)
    myTaskSplitter = SimpleTaskSplitter(myTaskFactory)
    daemon = CollectorDaemon(myPreferences, myTaskSplitter)
    daemon.run()
