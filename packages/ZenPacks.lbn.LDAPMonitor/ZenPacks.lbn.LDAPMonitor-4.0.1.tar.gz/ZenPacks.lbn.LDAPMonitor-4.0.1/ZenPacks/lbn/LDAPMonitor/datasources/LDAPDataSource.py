#
# Copyright 2012-2013 Corporation of Balclutha (http://www.balclutha.org)
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
from Products.ZenModel.BasicDataSource import BasicDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import Permissions
from Products.ZenUtils.Utils import binPath

from ZenPacks.lbn.LDAPMonitor.config import MONITORED

class LDAPDataSource(ZenPackPersistence, BasicDataSource):
    """
    A command-plugin that calls munin-based Zope-agents on remote
    instance via wget

    This base class needs instantiations with munin_plugins, and uri 
    attributes
    """

    LDAP_MONITOR = 'LDAP'
    ZENPACKID = 'ZenPacks.lbn.LDAPMonitor'

    sourcetypes = (LDAP_MONITOR,)
    sourcetype = LDAP_MONITOR

    eventClass = '/Status/LDAP'
        
    hostname = '${dev/ip}'
    ipAddress = '${dev/manageIp}'

    ldapProto = '${dev/zLDAPProto}'
    ldapPort = '${dev/zLDAPPort}'
    ldapDN = '${dev/zLDAPDN}'
    ldapPW = '${dev/zLDAPPW}'
    timeout = 20

    searchFilter = 'cn=monitor'

    _properties = BasicDataSource._properties + (
        {'id':'ldapProto',    'type':'string',    'mode':'w'},
        {'id':'ldapPort',     'type':'int',       'mode':'w'},
        {'id':'ldapDN',       'type':'string',    'mode':'w'},
        {'id':'ldapPW',       'type':'string',    'mode':'w'},
        {'id':'timeout',      'type':'int',       'mode':'w'},
        {'id':'searchFilter', 'type':'string',    'mode':'r'},
        )
        
    _relations = BasicDataSource._relations

    def __init__(self, id, title=None, buildRelations=True):
        BasicDataSource.__init__(self, id, title, buildRelations)
        self.addDataPoints()

    def ldapURI(self, device):
        """
        LDAP server connection string - this is really the getCommand() function here
        """
        return self.getCommand(device, 
                               "%s://%s:%s" % (self.ldapProto, self.ipAddress, self.ldapPort))

    def getDescription(self):
        return '%s://%s:%s (%s)' % (self.ldapProto, self.hostname, self.ldapPort, self.searchFilter)

    def useZenCommand(self):
        return False

    def checkCommandPrefix(self, context, cmd):
        return cmd

    def addDataPoints(self):
        for tag in map(lambda x: x[0], MONITORED):
            if not hasattr(self.datapoints, tag):
                self.manage_addRRDDataPoint(tag)
