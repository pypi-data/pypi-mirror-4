pydhcp-ldap-schema
==================

Helper class that can simplyfy most of the tasks when managing ISC-DHCP
configuration stored in a LDAP tree.

Modifying existing configuration
--------------------------------

Example::

    import ldap
    from pydhcp_ldap_schema import DHCPEntry

    con = ldap.initialize('ldap://localhost')
    con.bind_s('user', 'pass')

    subNet = DHCPEntry.ldap_load(con, 'cn=192.168.1.0,cn=DHCP Config,dc=example,dc=com')
    print subNet['dhcpNetMask']      # prints ['24']
    subNet['dhcpNetMask'] = ['25']   # set new value

    subNet.ldap_modify(con)          # automatic change detection and commit if nessesery

    con.unbind_s()

Creating new nodes
------------------

Add fresh configuration::

    import ldap
    from pydhcp_ldap_schema import DHCPEntry

    con = ldap.initialize('ldap://localhost')
    con.bind_s('user', 'pass')

    service = DHCPEntry(['top', 'dhcpService'], cn=['DHCP Config'])
    service.ldap_add(con, 'cn=DHCP Config,dc=example,dc=com')       # create base entry

    dhcpServer = DHCPEntry(['top', 'dhcpServer'], cn=['dhcp.local'])
    dhcpServer['dhcpServiceDN'] = [service.dn]

    service.subobjects.insert_entry(dhcpServer)   # DN will be calculated

    dhcpServer.ldap_add(con)

    # and most important subnet declaration

    subnet = DHCPEntry(['top', 'dhcpSubnet'], cn=['192.168.1.0'])
    subnet['dhcpNetMask'] = ['24']

    service.subobjects.insert_entry(subnet)

    subnet.ldap_add(con)

    # Now you can start DHCPd server

    con.unbind_s()
