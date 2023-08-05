# -*- coding: utf-8 -*-
#
# This file is part of pydhcp-ldap-schema.
#
# pydhcp-ldap-schema is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# pydhcp-ldap-schema is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with pydhcp-ldap-schema; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

__version__ = '0.1beta'

from collections import MutableMapping

import ldap
import ldap.modlist
import ldap.dn

SCHEMA_DEFINITION = {
    'dhcpLocator': {
        'allowed_attributes': set([
            'dhcpServiceDN', 'dhcpServerDN', 'dhcpSharedNetworkDN', 'dhcpSubnetDN',
            'dhcpPoolDN', 'dhcpGroupDN', 'dhcpHostDN', ' dhcpClassesDN', 'dhcpKeyDN',
            'dhcpZoneDN', 'dhcpFailOverPeerDN', 'dhcpOption', 'dhcpComments',
        ]),
    },
    'dhcpFailOverPeer': {
        'allowed_attributes': set([
            'dhcpFailOverResponseDelay ', 'dhcpFailOverUnackedUpdates',
            'dhcpMaxClientLeadTime', 'dhcpFailOverSplit', 'dhcpHashBucketAssignment',
            'dhcpFailOverLoadBalanceTime', 'dhcpComments',
        ]),
        'required_attributes': set([
            'dhcpFailOverPrimaryServer', 'dhcpFailOverSecondaryServer',
            'dhcpFailoverPrimaryPort', 'dhcpFailOverSecondaryPort',
        ]),
    },
    'dhcpDnsZone': {
        'allowed_attributes': set([
            'dhcpKeyDN', 'dhcpComments',
        ]),
        'required_attributes': set([
            'dhcpDnsZoneServer',
        ]),
    },
    'dhcpTSigKey': {
        'allowed_attributes': set([
            'dhcpComments',
        ]),
        'required_attributes': set([
            'dhcpKeyAlgorithm', 'dhcpKeySecret',
        ]),
    },
    'dhcpServer': {
        'allowed_attributes': set([
            'dhcpServiceDN', 'dhcpLocatorDN', 'dhcpVersion', 'dhcpImplementation',
            'dhcpHashBucketAssignment', 'dhcpDelayedServiceParameter',
            'dhcpMaxClientLeadTime', 'dhcpFailOverEndpointState', 'dhcpStatements',
            'dhcpComments', 'dhcpOption',
        ]),
    },
    'dhcpLog': {
        'allowed_attributes': set([
            'dhcpAddressState', 'dhcpExpirationTime', 'dhcpStartTimeOfState',
            'dhcpLastTransactionTime', 'dhcpBootpFlag', 'dhcpDomainName',
            'dhcpDnsStatus', 'dhcpRequestedHostName', 'dhcpAssignedHostName',
            'dhcpReservedForClient', 'dhcpAssignedToClient', 'dhcpRelayAgentInfo',
            'dhcpHWAddress', 'dhcpErrorLog',
        ]),
    },
    'dhcpLeasses': {
        'allowed_attributes': set([
            'dhcpExpirationTime', 'dhcpStartTimeOfState', 'dhcpLastTransactionTime',
            'dhcpBootpFlag', 'dhcpDomainName', 'dhcpDnsStatus', 'dhcpRequestedHostName',
            'dhcpAssignedHostName', 'dhcpReservedForClient', 'dhcpAssignedToClient',
            'dhcpRelayAgentInfo', 'dhcpHWAddress',
        ]),
        'allowed_subobjects': set(['top', 'dhcpLog', ]),
        'required_attributes': set(['dhcpAddressState']),
    },
    'dhcpOptions': {
        'allowed_attributes': set([
            'dhcpOption', 'dhcpComments',
        ]),
    },
    'dhcpSubClass': {
        'allowed_attributes': set([
            'dhcpClassData', 'dhcpOptionsDN', 'dhcpStatements', 'dhcpComments',
            'dhcpOption',
        ]),
    },
    'dhcpClass': {
        'allowed_attributes': set([
            'dhcpSubClassesDN', 'dhcpOptionsDN', 'dhcpStatements', 'dhcpComments',
            'dhcpOption',
        ]),
        'allowed_subobjects': set(['top', 'dhcpSubClass', 'dhcpOptions', ]),
    },
    'dhcpHost': {
        'allowed_attributes': set([
            'dhcpLeaseDN', 'dhcpHWAddress', 'dhcpOptionsDN', 'dhcpStatements',
            'dhcpComments', 'dhcpOption',
        ]),
        'allowed_subobjects': set(['top', 'dhcpOptions', ]),
    },
    'dhcpGroup': {
        'allowed_attributes': set([
            'dhcpHostDN', 'dhcpOptionsDN', 'dhcpStatements', 'dhcpComments',
            'dhcpOption',
        ]),
        'allowed_subobjects': set(['top', 'dhcpHost', 'dhcpOptions', ]),
    },
    'dhcpPool': {
        'allowed_attributes': set([
            'dhcpClassesDN', 'dhcpPermitList', 'dhcpLeasesDN', 'dhcpOptionsDN',
            'dhcpZoneDN', 'dhcpKeyDN', 'dhcpStatements', 'dhcpComments', 'dhcpOption',
        ]),
        'allowed_subobjects': set(['top', 'dhcpOptions', 'dhcpLeasses', 'dhcpLog', ]),
        'required_attributes': set(['dhcpRange']),
    },
    'dhcpSubnet': {
        'allowed_attributes': set([
            'dhcpRange', 'dhcpPoolDN', 'dhcpGroupDN', 'dhcpHostDN', 'dhcpClassesDN',
            'dhcpLeasesDN', 'dhcpOptionsDN', 'dhcpZoneDN', 'dhcpKeyDN',
            'dhcpFailOverPeerDN', 'dhcpStatements', 'dhcpComments', 'dhcpOption',
        ]),
        'allowed_subobjects': set(['top',
            'dhcpPool', 'dhcpGroup', 'dhcpHost', 'dhcpClass', 'dhcpOptions',
            'dhcpLeasses', 'dhcpLog', 'dhcpTSigKey', 'dhcpDnsZone',
            'dhcpFailOverPeer',
        ]),
        'required_attributes': set(['dhcpNetMask']),
    },
    'dhcpSharedNetwork': {
        'allowed_attributes': set([
            'dhcpSubnetDN', 'dhcpPoolDN', 'dhcpOptionsDN', 'dhcpZoneDN',
            'dhcpStatements', 'dhcpComments', 'dhcpOption',
        ]),
        'allowed_subobjects': set(['top',
            'dhcpSubnet', 'dhcpPool', 'dhcpOptions', 'dhcpLog', 'dhcpTSigKey',
            'dhcpDnsZone', 'dhcpFailOverPeer',
        ]),
    },
    'dhcpService': {
        'allowed_attributes': set([
            'dhcpPrimaryDN', 'dhcpSecondaryDN', 'dhcpServerDN', 'dhcpSharedNetworkDN',
            'dhcpSubnetDN', 'dhcpGroupDN', 'dhcpHostDN', 'dhcpClassesDN',
            'dhcpOptionsDN', 'dhcpZoneDN', 'dhcpKeyDN', 'dhcpFailOverPeerDN',
            'dhcpStatements', 'dhcpComments', 'dhcpOption',
        ]),
        'allowed_subobjects': set(['top',
            'dhcpSharedNetwork', 'dhcpSubnet', 'dhcpGroup','dhcpClass',
            'dhcpOptions', 'dhcpLeasses', 'dhcpLog', 'dhcpServer', 'dhcpTSigKey',
            'dhcpDnsZone', 'dhcpFailOverPeer', 'dhcpLocator',
        ]),
    },
    'top': {},
}

class DHCPEntry(dict):
    """Base object that can represent DHCP schema entries.
    """

    class Subobjects(dict):

        def __init__(self, owner):
            self.owner = owner
            super(DHCPEntry.Subobjects, self).__init__()

        def __setitem__(self, dn, entry):
            if not entry.object_class.issubset(self.owner.allowed_subobjects):
                raise TypeError('Entry "%s" not in allowed subobject types.'
                    % type(entry)
                )

            if dn != entry.dn:
                raise KeyError('Key DN "%s" mismatch to entry DN "%s".' % (
                    dn, entry.dn
                ))

            super(DHCPEntry.Subobjects, self).__setitem__(dn, entry)

        def insert_entry(self, entry):
            cn = 'cn=%s,' % ldap.dn.escape_dn_chars(entry['cn'][0])
            entry.dn = cn + self.owner.dn

            self[entry.dn] = entry

    object_class_registry = {}

    def __init__(self, object_class, **attributes):
        self.dn = ''
        object_class = frozenset(object_class)

        if object_class not in self.object_class_registry:
            allowed_attributes = set()
            required_attributes = set()
            allowed_subobjects = set()

            for class_ in object_class:
                def_ = SCHEMA_DEFINITION[class_]

                allowed_attributes.update(def_.get('allowed_attributes', set()))
                required_attributes.update(def_.get('required_attributes', set()))
                allowed_subobjects.update(def_.get('allowed_subobjects', set()))

                required_attributes.update(set(['cn', 'objectClass']))
                allowed_attributes.update(required_attributes)

            self.object_class_registry[object_class] = def_ = {}

            def_['allowed_attributes'] = allowed_attributes
            def_['required_attributes'] = required_attributes
            def_['allowed_subobjects'] = allowed_subobjects

        self.object_class = object_class
        self.subobjects = DHCPEntry.Subobjects(self)
        super(DHCPEntry, self).__init__(**attributes)

    @property
    def object_class(self):
        return frozenset(self['objectClass'])

    @object_class.setter
    def object_class(self, value):
        super(DHCPEntry, self).__setitem__('objectClass', list(value))

    @property
    def allowed_attributes(self):
        return self.object_class_registry[self.object_class]['allowed_attributes']

    @property
    def required_attributes(self):
        return self.object_class_registry[self.object_class]['required_attributes']

    @property
    def allowed_subobjects(self):
        return self.object_class_registry[self.object_class]['allowed_subobjects']

    def __setitem__(self, key, value):
        if key not in self.allowed_attributes:
            raise KeyError(key)

        super(DHCPEntry, self).__setitem__(key, value)

    def __repr__(self):
        return '<%s(dn="%s", objectClass=%s)>' % (
            self.__class__.__name__,
            self.dn,
            list(self.object_class),
        )

    def ldap_load_children(self, connection):
        results = connection.search_s(self.dn, ldap.SCOPE_ONELEVEL)

        for dn, entry in results:
            obj = DHCPEntry(entry.pop('objectClass'), **entry)
            obj.dn = dn

            self.subobjects[dn] = obj

    def ldap_add(self, connection, dn=None):
        if not dn and not self.dn:
            raise RuntimeError('Missing DN.')

        result = connection.add_s(dn or self.dn, ldap.modlist.addModlist(self))
        self.dn = dn

        return result

    def ldap_delete(self, connection):
        result = connection.delete_s(self.dn)
        self.dn = ''

        return result

    def ldap_modify(self, connection):
        obj = self.ldap_load(connection, self.dn)

        mdlst = ldap.modlist.modifyModlist(obj, self)

        if mdlst:
            return connection.modify_s(self.dn, mdlst)

    @staticmethod
    def ldap_load(connection, dn):
        dn, entry = connection.search_s(dn, ldap.SCOPE_BASE)[0]
        entry = entry.copy()

        obj = DHCPEntry(entry.pop('objectClass'), **entry)
        obj.dn = dn

        return obj
