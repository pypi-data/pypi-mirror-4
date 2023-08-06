#
# Copyright 2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
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
from os import path

PROJECTNAME = "ZenPacks.lbn.LDAPMonitor"
# ZenUtils expects full skin path in it's registration lookup
SKINS_DIR = path.join(path.dirname(__file__), 'skins')
SKINNAME = PROJECTNAME
GLOBALS = globals()

MONITORABLE = ('addentryops', 'anonymousbinds', 'bindsecurityerrors', 
               'bytesrecv', 'bytessent', 'cacheentries', 'cachehits', 
               'chainings', 'compareops', 'connections', 'connectionseq', 
               'copyentries', 'entriesreturned', 'errors', 'inops', 
               'listops', 'masterentries', 'modifyentryops', 
               'modifyrdnops', 'onelevelsearchops', 'readops', 'referrals', 
               'referralsreturned', 'removeentryops', 'searchops', 
               'securityerrors', 'simpleauthbinds', 'slavehits', 
               'strongauthbinds', 'unauthbinds', 'wholetreesearchops')

ERRORDP = (('bindsecurityerrors', 'Bind Security'),
           ('securityerrors', 'Security'),
           ('errors', 'Total Errors'))

BINDDP = (('anonymousbinds', 'Anonymous'),
          ('simpleauthbinds', 'Simple Auth'),
          ('strongauthbinds', 'Strong Auth'),
          ('unauthbinds', 'Unauth'))

# wtf - no failures!!
FAILDP = (('failures', 'Failures'),)

OPSDP = (('addentryops', 'Add Entry'),
         ('modifyentryops', 'Mod Entry'),
         ('removeentryops', 'Del Entry'),
         ('searchops', 'Search'),
         ('referrals', 'Referrals'),
         ('chainings', 'Chainings'))

CACHEDP = (('cacheentries', 'Cache Entries'),
           ('cachehits', 'Cache Hits'),
           ('slavehits', 'Slave Hits'),
           ('masterentries', 'Master Entries'))

MONITORED = ERRORDP + BINDDP + OPSDP + CACHEDP
