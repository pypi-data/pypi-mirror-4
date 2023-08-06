LDAPMonitor
-----------

LDAPMonitor provides a method for pulling performance metrics from any LDAP
server which implements the cn=Monitor standard.

The monitor works by directly querying the LDAP server using the configured
user dn and password credentials.  Make sure that your LDAP server is
available from your Zenoss console, you've enabled cn=monitor on it, and that 
the user has sufficient permissions to perform a 'cn=snmp,cn=monitor' search.


The following metrics will be collected and graphed for the LDAP Server:

    * Operations
      o  Add Entry
      o  Modify Entry
      o  Delete Entry
      o  Search Entry
    * Bindings
      o  Anonymous
      o  Simple Auth
      o  Unauthorised
    * Errors
      o  Bind Security
      o  Security
      o  Other Errors
      o  Failures
    * Response Time
    * Referrals

You can add LDAP monitoring to the device within Zenoss by simply binding the 
LDAPMonitor template to the device.

    1. Navigate to the device in the Zenoss web interface.
    2. Click the device menu, choose More then Templates.
    3. Click the templates menu, choose Bind Templates.
    4. Ctrl-click the LDAPMonitor template from /Devices/Server to choose it.
    5. Click OK.

You will now be collecting the LDAP Server metrics from this device.

