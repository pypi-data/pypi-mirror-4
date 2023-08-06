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
    
    def _filterDevice(self, device):
        """
        only return those with LDAP monitoring
        """
        return CollectorConfigService._filterDevice(self, device) and \
            'LDAPServer' in device.getProperty('zDeviceTemplates', [])

    def _createDeviceProxy(self, device):
        proxy = CollectorConfigService._createDeviceProxy(self, device)

        proxy.configCycleInterval = self._prefs.perfldapCycleInterval
        proxy.datapoints = []
        proxy.thresholds = []

        log.debug('device: %s', device)

        try: 
            perfServer = device.getPerformanceServer()
        except: 
            return None

        compName = device.id
        basepath = device.rrdPath()

        for templ in device.getRRDTemplates():
            dpnames = []
            for ds in filter(lambda ds: isinstance(ds, LDAPDataSource), templ.getRRDDataSources()):

                try:
                    proxy.ldapuri = ds.ldapURI(device)
                    proxy.credentials = device.getProperty('zLDAPDN'), device.getProperty('zLDAPPW')
                    proxy.searchFilter = ds.searchFilter
                except:
                    log.error('Device not LDAP: %s' % device)
                    continue

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
                if not (thr.enabled and dpn & set(thr.dsnames)): 
                    continue
                proxy.thresholds.append(thr.createThresholdInstance(device))

        return proxy
