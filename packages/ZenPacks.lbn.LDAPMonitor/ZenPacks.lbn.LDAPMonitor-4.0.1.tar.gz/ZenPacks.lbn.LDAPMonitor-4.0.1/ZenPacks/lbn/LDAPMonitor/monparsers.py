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
from config import MONITORED
import logging

KEYS = map(lambda x:x[0], MONITORED)

def _dn(dn, results):
    """ fetch the attribute hash corresponding to the dn """
    r = filter(lambda x: x[0].lower() == dn, results)
    if r:
        return r[0][1]
    raise KeyError, '%s: %s' % (dn, map(lambda x: x[0], results))

def _isFDS(base):
    """ is this a Fedora Directory Server... """
    return base.get('version',[''])[0].startswith('389')
    
def _FDS(ldapresults, results={}):
    """
    Fedora Directory Server (389-ds)
    """
    snmp = _dn('cn=snmp,cn=monitor', ldapresults)
    for k in KEYS:
        results[k] = snmp[k][0]

def _isOpenLDAP(base):
    """ is this an OpenLDAP server ..."""
    return base.get('monitoredInfo',[''])[0].startswith('OpenLDAP')

def _OpenLDAP(ldapresults, results={}):
    """
    OpenLDAP mappings
    """
    results['addentryops'] = _dn('cn=add,cn=operations,cn=monitor', ldapresults).get('monitorOpCompleted', [0])[0]
    results['monitorentryops'] = _dn('cn=modify,cn=operations,cn=monitor', ldapresults).get('monitorOpCompleted', [0])[0]
    results['removeentryops'] = _dn('cn=delete,cn=operations,cn=monitor', ldapresults).get('monitorOpCompleted', [0])[0]
    results['searchops'] = _dn('cn=search,cn=operations,cn=monitor', ldapresults).get('monitorOpCompleted', [0])[0]
    results['referrals'] = _dn('cn=referrals,cn=statistics,cn=monitor', ldapresults).get('monitorCounter', [0])[0]

def parse(ldapresults, results):
    """
    parse ldap.search_s result tuples and assign into a hash, keyed upon our
    datapoint names
    """
    base = _dn('cn=monitor', ldapresults)
    
    if _isFDS(base):
        _FDS(ldapresults, results)
    elif _isOpenLDAP(base):
        _OpenLDAP(ldapresults, results)
    else:
        raise NotImplementedError, 'No parser for %s' % ldapresults
    return results
