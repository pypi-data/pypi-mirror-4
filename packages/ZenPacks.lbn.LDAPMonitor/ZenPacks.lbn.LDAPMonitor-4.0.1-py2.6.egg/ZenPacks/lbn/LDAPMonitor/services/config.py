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
import logging
from Products.ZenCollector.services.config import CollectorConfigService
from ZenPacks.lbn.LDAPMonitor.datasources.LDAPDataSource import LDAPDataSource

log = logging.getLogger('zen.ldapserviceconf')

class LDAPConfigService(CollectorConfigService):
    """
    place LDAP connection information into proxy
    """

    def _createDeviceProxy(self, device):
        proxy = CollectorConfigService._createDeviceProxy(self, device)

        # for now, every device gets a single configCycleInterval based upon
        # the collector's winCycleInterval configuration which is typically
        # located at dmd.Monitors.Performance._getOb('localhost').
        # TODO: create a zProperty that allows for individual device schedules
        proxy.configCycleInterval = self._prefs.perfsnmpCycleInterval
        proxy.datapoints = []
        proxy.thresholds = []

        log.debug('device: %s', device)

        try: 
            perfServer = device.getPerformanceServer()
        except: 
            return None

        for comp in [device] + device.getMonitoredComponents():
            compName = comp.id
            try: 
                basepath = comp.rrdPath()
            except: 
                continue

            for templ in comp.getRRDTemplates():
                dpnames = []
                for ds in filter(lambda ds: isinstance(ds, LDAPDataSource), templ.getRRDDataSources()):

                    proxy.ldapuri = ds.ldapURI()
                    proxy.credentials = ds.ldapCredentials()
                    proxy.searchFilter = ds.searchFilter

                    for dp in ds.getRRDDataPoints():
                        dpname = dp.name()
                        dpnames.append(dpname)
                        proxy.datapoints.append((dp.id,
                                                 compName,
                                                 "/".join((basepath, dpname)),
                                                 dp.rrdtype,
                                                 dp.getRRDCreateCommand(perfServer),
                                                 dp.rrdmin, 
                                                 dp.rrdmax))

                dpn = set(dpnames)
                for thr in templ.thresholds():
                    if not (thr.enabled and dpn & set(thr.dsnames)): continue
                    proxy.thresholds.append(thr.createThresholdInstance(comp))


        return proxy
