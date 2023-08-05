# pydhcp-ldap-schema

## By example:

    import ldap
    import pydhcp_ldap_schema as schema

    con = ldap.initialize('ldap://localhost')
    con.bind_s('user', 'pass')

    results = con.search_s('dc=domain,dc=com', ldap.SCOPE_ONELEVEL, '(objectClass=dhcpService)')
    service = schema.DHCPService.build_from_resultset(results[0])

    service.attributes['dhcpPrimaryDN'] = ['cn=New CN,dc=example,dc=com']
    dn, old_entry = results[0]
    modlist = service.getModifyModlist(old_entry)

    con.modify_s(dn, modlist)
    con.unbind_s()
