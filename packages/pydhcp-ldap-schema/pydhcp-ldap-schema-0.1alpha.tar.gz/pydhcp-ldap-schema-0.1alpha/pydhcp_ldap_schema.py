# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from ldap import dn as DN, modlist

class DHCPObject(object):
    """
    Base class for all DHCP mapping objects.
    """

    allowed_attributes = set()
    allowed_subobjects = set()
    required_attributes = set()
    object_class = []

    class Attributes(dict):

        def __init__(self, owner):
            self.owner = owner
            super(DHCPObject.Attributes, self).__init__()

        def __setitem__(self, key, value):
            if key not in (
                    self.owner.allowed_attributes.union(self.owner.required_attributes)
                ):
                raise KeyError(key)

            super(DHCPObject.Attributes, self).__setitem__(key, value)

    class Subobjects(dict):

        def __init__(self, owner):
            self.owner = owner
            super(DHCPObject.Subobjects, self).__init__()

        def __setitem__(self, key, value):
            if not isinstance(value, tuple(self.owner.allowed_subobjects)):
                raise ValueError('Invalid subobject type: %s' % type(value))

            if key != value.cn:
                raise KeyError(key)

            super(DHCPObject.Subobjects, self).__setitem__(key, value)
            value.parent = self.owner

        def replace_or_add(self, subobject):
            self.__setitem__(subobject.cn, subobject)

    def __init__(self, base_dn=None, cn=None, parent=None):
        self.base_dn = base_dn
        self.cn = cn
        self.attributes = DHCPObject.Attributes(self)
        self.subobjects = DHCPObject.Subobjects(self)
        self.parent = parent

    @property
    def dn(self):
        base_dn = DN.str2dn(self.base_dn)
        cn = DN.str2dn(self.cn)
        return DN.dn2str(cn + base_dn)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = parent = value

        if parent and self not in parent.subobjects.values():
            parent.subobjects[self.cn] = self

    def __repr__(self):
        return '<%s(dn="%s")>' % (self.__class__.__name__, self.dn)

    def create_subobject(self, obj_type, cn):
        return obj_type(self.dn, cn, self)

    def getAddModlist(self):
        return modlist.addModlist(self.attributes)

    def getModifyModlist(self, old_entry):
        return modlist.modifyModlist(old_entry, self.attributes)

    @classmethod
    def build_from_resultset(cls, resultset):
        dn, container = resultset
        object_class = container.pop('objectClass')
        cn = 'cn=' + container.pop('cn')[0]
        base_dn = DN.dn2str(DN.str2dn(dn)[1:])

        obj = cls(base_dn, cn)

        for key in container:
            obj.attributes[key] = container[key]

        return obj


class DHCPLocator(DHCPObject):
    """
    Locator object for DHCP configuration in the tree.
    There will be a single dhcpLocator object in the tree with links to all
    the DHCP objects in the tree.
    """

    allowed_attributes = set([
        'dhcpServiceDN', 'dhcpServerDN', 'dhcpSharedNetworkDN', 'dhcpSubnetDN',
        'dhcpPoolDN', 'dhcpGroupDN', 'dhcpHostDN', ' dhcpClassesDN', 'dhcpKeyDN',
        'dhcpZoneDN', 'dhcpFailOverPeerDN', 'dhcpOption', 'dhcpComments',
    ])
    object_class = ['top', 'dhcpLocator']

class DHCPFailOverPeer(DHCPObject):
    """
    This class defines the Fail over peer.
    """

    allowed_attributes = set([
        'dhcpFailOverResponseDelay ', 'dhcpFailOverUnackedUpdates',
        'dhcpMaxClientLeadTime', 'dhcpFailOverSplit', 'dhcpHashBucketAssignment',
        'dhcpFailOverLoadBalanceTime', 'dhcpComments',
    ])
    required_attributes = set([
        'dhcpFailOverPrimaryServer', 'dhcpFailOverSecondaryServer',
        'dhcpFailoverPrimaryPort', 'dhcpFailOverSecondaryPort',
    ])
    object_class = ['top', 'dhcpFailOverPeer']

class DHCPDnsZone(DHCPObject):
    """
    DNS Zone for updating leases.
    """

    allowed_attributes = set([
        'dhcpKeyDN', 'dhcpComments',
    ])
    required_attributes = set([
        'dhcpDnsZoneServer',
    ])
    object_class = ['top', 'dhcpDnsZone']

class DHCPTSigKey(DHCPObject):
    """
    TSIG key for secure dynamic updates.
    """

    allowed_attributes = set([
        'dhcpComments',
    ])
    required_attributes = set([
        'dhcpKeyAlgorithm', 'dhcpKeySecret',
    ])
    object_class = ['top', 'dhcpTSigKey']

class DHCPServer(DHCPObject):
    """
    DHCP Server Object.
    """

    allowed_attributes = set([
        'dhcpServiceDN', 'dhcpLocatorDN', 'dhcpVersion', 'dhcpImplementation',
        'dhcpHashBucketAssignment', 'dhcpDelayedServiceParameter',
        'dhcpMaxClientLeadTime', 'dhcpFailOverEndpointState', 'dhcpStatements',
        'dhcpComments', 'dhcpOption',
    ])
    object_class = ['top', 'dhcpServer']

class DHCPLog(DHCPObject):
    """
    This is the object that holds past information about the IP address.
    The cn is the time/date stamp when the address was assigned or released,
    the address state at the time, if the address was assigned or released.
    """

    allowed_attributes = set([
        'dhcpAddressState', 'dhcpExpirationTime', 'dhcpStartTimeOfState',
        'dhcpLastTransactionTime', 'dhcpBootpFlag', 'dhcpDomainName',
        'dhcpDnsStatus', 'dhcpRequestedHostName', 'dhcpAssignedHostName',
        'dhcpReservedForClient', 'dhcpAssignedToClient', 'dhcpRelayAgentInfo',
        'dhcpHWAddress', 'dhcpErrorLog',
    ])
    object_class = ['top', 'dhcpLog']

class DHCPLeasses(DHCPObject):
    """
    This class represents an IP Address, which may or may not have been leased.
    """

    allowed_attributes = set([
        'dhcpExpirationTime', 'dhcpStartTimeOfState', 'dhcpLastTransactionTime',
        'dhcpBootpFlag', 'dhcpDomainName', 'dhcpDnsStatus', 'dhcpRequestedHostName',
        'dhcpAssignedHostName', 'dhcpReservedForClient', 'dhcpAssignedToClient',
        'dhcpRelayAgentInfo', 'dhcpHWAddress',
    ])
    allowed_subobjects = set([
        DHCPLog,
    ])
    required_attributes = set(['dhcpAddressState'])
    object_class = ['top', 'dhcpLeasses']

class DHCPOptions(DHCPObject):
    """
    Represents information about a collection of options defined.
    """

    allowed_attributes = set([
        'dhcpOption', 'dhcpComments',
    ])
    object_class = ['top', 'dhcpOptions']

class DHCPSubClass(DHCPObject):
    """
    Represents information about a collection of related classes.
    """

    allowed_attributes = set([
        'dhcpClassData', 'dhcpOptionsDN', 'dhcpStatements', 'dhcpComments',
        'dhcpOption',
    ])
    object_class = ['top', 'dhcpSubClass']

class DHCPClass(DHCPObject):
    """
    Represents information about a collection of related clients.
    """

    allowed_attributes = set([
        'dhcpSubClassesDN', 'dhcpOptionsDN', 'dhcpStatements', 'dhcpComments',
        'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPSubClass, DHCPOptions,
    ])
    object_class = ['top', 'dhcpClass']

class DHCPHost(DHCPObject):
    """
    This represents information about a particular client.
    """

    allowed_attributes = set([
        'dhcpLeaseDN', 'dhcpHWAddress', 'dhcpOptionsDN', 'dhcpStatements',
        'dhcpComments', 'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPOptions,
    ])
    object_class = ['top', 'dhcpHost']

class DHCPGroup(DHCPObject):
    """
    Group object that lists host DNs and parameters. This is a container object.
    """

    allowed_attributes = set([
        'dhcpHostDN', 'dhcpOptionsDN', 'dhcpStatements', 'dhcpComments',
        'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPHost, DHCPOptions,
    ])
    object_class = ['top', 'dhcpGroup']

class DHCPPool(DHCPObject):
    """
    This stores configuration information about a pool.
    """

    allowed_attributes = set([
        'dhcpClassesDN', 'dhcpPermitList', 'dhcpLeasesDN', 'dhcpOptionsDN',
        'dhcpZoneDN', 'dhcpKeyDN', 'dhcpStatements', 'dhcpComments', 'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPOptions, DHCPLeasses, DHCPLog,
    ])
    required_attributes = set(['dhcpRange'])
    object_class = ['top', 'dhcpPool']

class DHCPSubnet(DHCPObject):
    """
    This class defines a subnet. This is a container object.
    """

    allowed_attributes = set([
        'dhcpRange', 'dhcpPoolDN', 'dhcpGroupDN', 'dhcpHostDN', 'dhcpClassesDN',
        'dhcpLeasesDN', 'dhcpOptionsDN', 'dhcpZoneDN', 'dhcpKeyDN',
        'dhcpFailOverPeerDN', 'dhcpStatements', 'dhcpComments', 'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPPool, DHCPGroup, DHCPHost, DHCPClass, DHCPOptions, DHCPLeasses,
        DHCPLog, DHCPTSigKey, DHCPDnsZone, DHCPFailOverPeer,
    ])
    required_attributes = set(['dhcpNetMask'])
    object_class = ['top', 'dhcpSubnet']

class DHCPSharedNetwork(DHCPObject):
    """
    This stores configuration information for a shared network.
    """

    allowed_attributes = set([
        'dhcpSubnetDN', 'dhcpPoolDN', 'dhcpOptionsDN', 'dhcpZoneDN',
        'dhcpStatements', 'dhcpComments', 'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPSubnet, DHCPPool, DHCPOptions, DHCPLog, DHCPTSigKey, DHCPDnsZone,
        DHCPFailOverPeer,
    ])
    object_class = ['top', 'dhcpSharedNetwork']

class DHCPService(DHCPObject):
    """
    Service object that represents the actual DHCP Service configuration.
    This is a container object.
    """

    allowed_attributes = set([
        'dhcpPrimaryDN', 'dhcpSecondaryDN', 'dhcpServerDN', 'dhcpSharedNetworkDN',
        'dhcpSubnetDN', 'dhcpGroupDN', 'dhcpHostDN', 'dhcpClassesDN',
        'dhcpOptionsDN', 'dhcpZoneDN', 'dhcpKeyDN', 'dhcpFailOverPeerDN',
        'dhcpStatements', 'dhcpComments', 'dhcpOption',
    ])
    allowed_subobjects = set([
        DHCPSharedNetwork, DHCPSubnet, DHCPGroup, DHCPGroup, DHCPClass,
        DHCPOptions, DHCPLeasses, DHCPLog, DHCPServer, DHCPTSigKey, DHCPDnsZone,
        DHCPFailOverPeer, DHCPLocator,
    ])
    object_class = ['top', 'dhcpService']
