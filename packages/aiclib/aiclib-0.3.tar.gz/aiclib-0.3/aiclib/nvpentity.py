# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Rackspace
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Created on August 22, 2012

@author: Justin Hammond, Rackspace Hosting
"""

import logging

import common
import core
import nvpquery

logger = logging.getLogger(__name__)


def requireuuid(fn):
    def wrapper(self):
        if not self.uuid:
            msg = "Missing UUID for verb (%s). Failing"
            logger.error(msg % fn.__name__)
            return None
        return fn(self)
    return wrapper


class NVPEntity(core.Entity):

    def __init__(self, connection):
        super(NVPEntity, self).__init__(connection)

    def ignore_cluster_majority(self, ignore):
        self.ignore_cluster_majority = ignore
        return self

    def tags(self, taglist):
        """Will set/update the tag list of the object.

        Arguments:
        tagList -- a list of dictionaries with the following format:
        {
            'tag':<some value>,  <--- is required
            'scope':<some value>
        }
        If a list is not given and only a dictionary is given it will put the
        dictionary in a list for you.
        """
        if not type(taglist) is list:
            taglist = [taglist]
        elif len(taglist) > 5:
            raise AttributeError("Tag list only supports up to 5 elements")
        self.info['tags'] = taglist
        return self

    def display_name(self, name):
        """Will set/update the display name of the object. By default if a
        display name is not given the generated UUID will be used as the
        display name.

        Arguments:
        name -- a string with max length of 40
        """
        if len(name) > 40:
            raise AttributeError("Display name is greater than 40 characters")
        self.info['display_name'] = name
        return self

    def _unroll(self):
        super(NVPEntity, self)._unroll()
        return self.info


class QOSQueue(NVPEntity):
    # All queue specific functionality has been implemented
    # TODO: it now needs to be tested
    def __init__(self, connection, uuid=None):
        super(QOSQueue, self).__init__(connection)
        self.uuid = uuid

    def _unroll(self):
        super(QOSQueue, self)._unroll()
        return self.info

    def dscp(self, value):
        """IP header DSCP value

        Arguments:
        value -- integer between 0 and 63
        """
        if value < 0 or value > 63:
            raise AttributeError("DSCP value out of range")
        self.info['dscp'] = value
        return self

    def maxbw_rate(self, rate):
        """Maximum bitrate for queue in kbps

        Arguments:
        rate -- positive integer
        """
        if rate < 0:
            raise AttributeError("Rate must be positive")
        self.info['max_bandwidth_rate'] = rate
        return self

    def minbw_rate(self, rate):
        """Minimum bitrate for queue in kbps

        Arguments:
        rate -- positive integer
        """
        if rate < 0:
            raise AttributeError("Rate must be positive")
        self.info['min_bandwidth_rate'] = rate
        return self

    def qos_marking(self, marking):
        """Will set the DSCP field.

        Arguments:
        marking -- string that can be 'trusted' or 'untrusted'
        """
        if marking != 'trusted' or marking != 'untrusted':
            raise AttributeError("Marking can be 'trusted' or 'untrusted'")
        self.info['qos_marking']
        return self

    def create(self):
        """Create (verb) will create the QoS queue"""
        uri = common.genuri('lqueue')
        return super(QOSQueue, self)._action('POST', uri)

    def query(self):
        """Returns the query object for the QoS queue"""
        uri = common.genuri('lqueue')
        queryobject = nvpquery.QOSQueueQuery(self.connection, uri)
        return queryobject

    def query_by_switch(self, switchuuid):
        """Returns the query object for all queues on all ports of the switch
        """
        uri = common.genuri('lswitch', switchuuid, 'lqueue')
        queryobject = nvpquery.QOSQueueQuery(self.connection, uri)
        return queryobject

    @requireuuid
    def update(self):
        """Update (verb) will update the QoS queue"""
        uri = common.genuri('lqueue', self.uuid)
        return super(QOSQueue, self)._action('PUT', uri)

    @requireuuid
    def read(self):
        """Read (verb) will read the QoS queue config"""
        uri = common.genuri('lqueue', self.uuid)
        return super(QOSQueue, self)._action('GET', uri)

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the QoS queue"""
        uri = common.genuri('lqueue', self.uuid)
        return super(QOSQueue, self)._action('DELETE', uri)


class SecurityRule(object):
    """Utility class for SecurityProfile's rules"""
    #TODO: Needs to be tested for convert to JSON

    def __init__(self, ethertype, ip_prefix=None, port_range_max=None,
                 port_range_min=None, profile_uuid=None, protocol=None):
        if ethertype != 4 and ethertype != 6:
            raise AttributeError("Ethertype must be 4 or 6")
        self.info = {}
        self.info['ethertype'] = ethertype

    def ip_prefix(self, prefix):
        self.info['ip_prefix'] = prefix
        return self

    def port_range_max(self, port_range):
        if port_range < 0 or port_range > 65535:
            raise AttributeError("Max port range is out of range")
        self.info['port_range_max'] = port_range
        return self

    def port_range_min(self, port_range):
        if port_range < 0 or port_range > 65535:
            raise AttributeError("Min port range is out of range")
        self.info['port_range_min'] = port_range
        return self

    def profile_uuid(self, uuid):
        self.info['profile_uuid'] = uuid
        return self

    def protocol(self, protid):
        if protid < 0 or protid > 255:
            raise AttributeError("IP protocol number out of range")
        self.info['protocol'] = protid
        return self

    def to_dict(self):
        return self.info


class SecurityProfile(NVPEntity):
    # All security profile specific functionality has been implemented
    #TODO: It now needs to be tested
    def __init__(self, connection, uuid=None):
        super(SecurityProfile, self).__init__(connection)
        self.uuid = uuid

    def _unroll(self):
        super(SecurityProfile, self)._unroll()
        return self.info

    def port_egress_rules(self, rulelist):
        """Sets rules for outbound traffic. All outbound traffic not matching
        the specified rules will be dropped.

        Arguments:
        rulelist -- a list of SecurityRule objects
        If a single SecurityRule object is given it will be put in a list
        for you
        """
        if not type(rulelist) is list:
            rulelist = [rulelist]
        if False in [isinstance(rule, SecurityRule) for rule in rulelist]:
            raise AttributeError("SecurityRule objects required")
        outlist = [rule.to_dict() for rule in rulelist]
        self.info['logical_port_egress_rules'] = outlist
        return self

    def port_ingress_rules(self, rulelist):
        """Sets rules for inbound traffic. All inbound traffic not matching
        the specified rules will be dropped.

        Arguments:
        rulelist -- a list of SecurityRule objects
        If a single SecurityRule object is given it will be put in a list
        for you
        """
        if not type(rulelist) is list:
            rulelist = [rulelist]
        if False in [isinstance(rule, SecurityRule) for rule in rulelist]:
            raise AttributeError("SecurityRule objects required")
        outlist = [rule.to_dict() for rule in rulelist]
        self.info['logical_port_ingress_rules'] = outlist
        return self

    def create(self):
        """Create (verb) will create the security profile"""
        uri = common.genuri('security-profile')
        return super(SecurityProfile, self)._action('POST', uri)

    def query(self):
        """Returns the query object for the security profile"""
        uri = common.genuri('security-profile')
        queryobject = nvpquery.SecurityProfileQuery(self.connection, uri)
        return queryobject

    @requireuuid
    def update(self):
        """Update (verb) will update the security profile"""
        uri = common.genuri('security-profile', self.uuid)
        return super(SecurityProfile, self)._action('PUT', uri)

    @requireuuid
    def read(self):
        """Read (verb) will read the security profile config"""
        uri = common.genuri('security-profile', self.uuid)
        return super(SecurityProfile, self)._action('GET', uri)

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the security profile"""
        uri = common.genuri('security-profile', self.uuid)
        return super(SecurityProfile, self)._action('DELETE', uri)


class TransportConnector(object):
    GRE = 'GREConnector'
    STT = 'STTConnector'
    BRIDGE = 'BridgeConnector'
    SECGRE = 'IPsecGREConnector'
    SECSTT = 'IPsecSTTConnector'
    _valid_entries = [GRE, STT, BRIDGE, SECGRE, SECSTT]

    def __init__(self, tzone_uuid, connector_type):
        if not connector_type in TransportConnector._valid_entries:
            raise AttributeError("connector_type is invalid")
        self.info = {}
        self.info['tzone_uuid'] = tzone_uuid
        self.info['connector_type'] = connector_type

    def to_dict(self):
        return self.info


class TransportNode(NVPEntity):
    #All node specific functionality has been implemented
    #TODO: It now needs to be tested
    def __init__(self, connection, uuid=None):
        super(TransportNode, self).__init__(connection)
        self.uuid = uuid

    def _unroll(self):
        super(TransportNode, self)._unroll()
        return self.info

    def admin_status_enabled(self, flag):
        """Will set the admin enabled status of the node"""
        self.info['admin_status_enabled'] = flag
        return self

    def credential(self, mgmt_credentials):
        """Will set the credential of the node

        Arguments:
        mgmt_credentials -- either MgmtAddrCredential, or
                            SecurityCertificateCredential string
        """
        self.info['credential'] = mgmt_credentials
        return self

    def integration_bridge(self, bridgeid):
        """Used to connect logical and transport networks"""
        if len(bridgeid) > 40:
            raise AttributeError("Bridge id must be <= 40 characters")
        self.info['intergration_bridge_id'] = bridgeid
        return self

    def rendezvous_client(self, flag):
        """Indicates if node management connections may be established
        via a rendezvous server"""
        self.info['mgmt_rendezvous_client'] = flag
        return self

    def rendezvous_server(self, flag):
        """indicates if node should act as rendezvous server"""
        self.info['mgmt_rendezvous_server'] = flag
        return self

    def transport_connectors(self, connector_list):
        """Will connect the node to transport zones with a given connector
        of the specified type.

        Arguments:
        connector_list -- a list of TransportConnector objects; if a single
                          object is given it will be put into a list for you
        """
        if not type(connector_list) is list:
            connector_list = [connector_list]
        if False in [isinstance(conn, TransportConnector) for conn in
                     connector_list]:
            raise AttributeError("TransportConnector objects required")
        outlist = [conn.to_dict() for rule in connector_list]
        self.info['transport_connectors'] = outlist
        return self

    def zone_forwarding(self, flag):
        """Indicates if node may be used to forward packets between
        transport zones."""
        self.info['zone_fowarding'] = flag
        return self

    def create(self):
        """Create (verb) will create the transport node"""
        uri = common.genuri('transport-node')
        return super(TransportNode, self)._action('POST', uri)

    def query(self):
        """Returns the query object for the transport node"""
        uri = common.genuri('transport-node')
        queryobject = nvpquery.TransportNodeQuery(self.connection, uri)
        return queryobject

    @requireuuid
    def status(self):
        """Will get the status of the transport node"""
        uri = common.genuri('transport-node', self.uuid, 'status')
        return super(TransportNode, self)._action('GET', uri)

    @requireuuid
    def update(self):
        """Update (verb) will update the transport node"""
        uri = common.genuri('transport-node', self.uuid)
        return super(TransportNode, self)._action('PUT', uri)

    @requireuuid
    def read(self):
        """Read (verb) will read the transport node config"""
        uri = common.genuri('transport-node', self.uuid)
        return super(TransportNode, self)._action('GET', uri)

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the transport node"""
        uri = common.genuri('transport-node', self.uuid)
        return super(TransportNode, self)._action('DELETE', uri)


class GatewayService(NVPEntity):
    #TODO: Basic support requires entity specific features on creation
    #TODO: Add all entity specific features
    def __init__(self, connection, uuid=None):
        super(GatewayService, self).__init__(connection)
        self.uuid = uuid

    def _unroll(self):
        super(GatewayService, self)._unroll()
        return self.info

    def create(self):
        """Create (verb) will create the Gateway Service"""
        uri = common.genuri('gateway-service')
        return super(GatewayService, self)._action('POST', uri)

    def query(self):
        """Returns the query object for the Gateway Service"""
        uri = common.genuri('gateway-service')
        queryobject = nvpquery.GatewayServiceQuery(self.connection, uri)
        return queryobject

    @requireuuid
    def update(self):
        """Update (verb) will update the Gateway Service"""
        uri = common.genuri('gateway-service', self.uuid)
        return super(GatewayService, self)._action('PUT', uri)

    @requireuuid
    def read(self):
        """Read (verb) will read the Gateway Service config"""
        uri = common.genuri('gateway-service', self.uuid)
        return super(GatewayService, self)._action('GET', uri)

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the Gateway Service"""
        uri = common.genuri('gateway-service', self.uuid)
        return super(GatewayService, self)._action('DELETE', uri)


class TransportZone(NVPEntity):

    def __init__(self, connection, uuid=None):
        super(TransportZone, self).__init__(connection)
        self.uuid = uuid

    def _unroll(self):
        super(TransportZone, self)._unroll()
        return self.info

    def create(self):
        """Create (verb) will create the transport zone"""
        uri = common.genuri('transport-zone')
        return super(TransportZone, self)._action('POST', uri)

    def query(self):
        """Returns the query object for the transport zone"""
        uri = common.genuri('transport-zone')
        queryobject = nvpquery.TransportZoneQuery(self.connection, uri)
        return queryobject

    @requireuuid
    def update(self):
        """Update (verb) will update the transport zone"""
        uri = common.genuri('transport-zone', self.uuid)
        return super(TransportZone, self)._action('PUT', uri)

    @requireuuid
    def read(self):
        """Read (verb) will read the transport zone config"""
        uri = common.genuri('transport-zone', self.uuid)
        return super(TransportZone, self)._action('GET', uri)

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the transport zone"""
        uri = common.genuri('transport-zone', self.uuid)
        return super(TransportZone, self)._action('DELETE', uri)


class LSwitch(NVPEntity):

    def __init__(self, connection, uuid=None):
        super(LSwitch, self).__init__(connection)
        self.uuid = uuid

    def port_isolation_enabled(self, enabled):
        """Will set/update the port_isolation_enabled flag on the switch
        """
        self.info['port_isolation_enabled'] = enabled
        return self

    def transport_zones(self, zones):
        """Will set/update the transport zones that the switch is connected
        """
        #TODO: Soon
        return self

    def _unroll(self):
        super(LSwitch, self)._unroll()
        return self.info

    def query(self):
        """Returns the query object for logical switches
        """
        queryobject = nvpquery.LSwitchQuery(self.connection,
                                            common.genuri('lswitch'))
        return queryobject

    def create(self):
        """Create (verb) will create the logical switch
        """
        return super(LSwitch, self)._action('POST', common.genuri('lswitch'))

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the logical switch
        Requires a UUID set at the object.
        """
        uri = common.genuri('lswitch', self.uuid)
        return super(LSwitch, self)._action('DELETE', uri)

    @requireuuid
    def status(self):
        """Status (verb) will return the network status of the logical switch
        Requires a UUID set at the object.
        """
        uri = common.genuri('lswitch', self.uuid, 'status')
        return super(LSwitch, self)._action('GET', uri)

    @requireuuid
    def read(self):
        """Read (verb) will return the configuration of the logical switch
        Requires a UUID set at the object.
        """
        uri = common.genuri('lswitch', self.uuid)
        return super(LSwitch, self)._action('GET', uri)

    @requireuuid
    def update(self):
        """Update (verb) will update the logical switch
        Requires a UUID set at the object.
        """
        uri = common.genuri('lswitch', self.uuid)
        return super(LSwitch, self)._action('PUT', uri)


class LSwitchPort(NVPEntity):

    def __init__(self, connection, lswitch_uuid, uuid=None):
        super(LSwitchPort, self).__init__(connection)
        self.lswitch_uuid = lswitch_uuid
        self.uuid = uuid

    def admin_status_enabled(self, enabled):
        self.info['admin_status_enabled'] = enabled
        return self

    def attachment_patch(self, peer_uuid, lrouter_uuid=None):
        if not common.isuuid(peer_uuid):
            raise AttributeError("Peer Port UUID is invalid")
        if lrouter_uuid and not common.isuuid(lrouter_uuid):
            raise AttributeError("Logical Router UUID is invalid")
        pass

    def attachment_vif(self, vif_uuid, hypervisor=None):
        pass

    def attachment_extended_network_bridge(self, tnode_uuid, bridgeid,
                                           vlan=None):
        pass

    def attachment_mdi(self, mdiservice, interconnectid):
        pass

    def attachment_l2gateway(self, gateway_uuid, vlan=None):
        pass

    def allowed_address_pairs(self, address_pair_list):
        """Will set/update the address pair list of the object.

        Arguments:
        addressPairList -- a list of dictionaries with the following format:
        {
            'mac':<some value>,  <--- is required
            'ip':<some value>
        }
        If a list is not given and only a dictionary is given it will put the
        dictionary in a list for you.
        """
        if not type(address_pair_list) is list:
            address_pair_list = [address_pair_list]
        self.info['allowed_address_pairs'] = address_pair_list
        return self

    def mirror_targets(self, mirrorlist):
        """Will set/update the mirror target list of the object.

        Arguments:
        mirror_targets -- a list of IPs that can have up to 3 items
        """
        if not type(mirrorlist) is list:
            mirrorlist = [mirrorlist]
        elif len(mirrorlist) > 3:
            raise AttributeError("Mirror list has greater than 3 items")
        self.info['mirror_targets'] = mirrorlist
        return self

    def portno(self, portnum):
        """Will set/update the port number of the object.

        Arguments:
        portnum -- a integer between 1 and 1000000 inclusive
        """
        if portnum < 1 or portnum > 1000000:
            raise AttributeError("Port number value out of range (1,1000000)")
        self.info['portno'] = portnum
        return self

    def qosuuid(self, uuid):
        """Will set/update the QoS queue UUID of the object.

        Arguments:
        uuid -- a string or None, if None is used 'null' will be sent and the
                QoS UUID of the object will be unset
        """
        if uuid is None:
            uuid = 'null'
        elif not common.isuuid(uuid):
            raise AttributeError("UUID is invalid")
        self.info['queue_uuid'] = uuid
        return self

    def security_profiles(self, uuidlist):
        """Will set/update the security profile list of of the object.

        Arguments:
        uuidlist -- A list of strings in UUID format
        If a list is not given and only a single UUID string is given it will
        put the string in a list for you.
        """
        if not type(uuidlist) is list:
            uuidlist = [uuidlist]
        if False in map(common.isuuid, uuidlist):
            raise AttributeError("One or more UUIDs are invalid")
        self['security_profiles'] = uuidlist
        return self

    def _unroll(self):
        super(LSwitchPort, self)._unroll()
        return self.info

    def create(self):
        """Create (verb) will create the logical port on the switch"""
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport')
        return super(LSwitchPort, self)._action("POST", uri)

    def query(self):
        """Returns the query object for logical switch ports
        """
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport')
        queryobject = nvpquery.LSwitchPortQuery(self.connection, uri)
        return queryobject

    @requireuuid
    def read(self):
        """Read (verb) will read the logical port's configuration"""
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport', self.uuid)
        return super(LSwitchPort, self)._action("GET", uri)

    @requireuuid
    def statistics(self):
        """statistics (verb) will return the port's stats"""
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport', self.uuid,
                            'statistic')
        return super(LSwitchPort, self)._action("GET", uri)

    @requireuuid
    def clear_statistics(self):
        """clear_statistics (verb) will clear the port's stats"""
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport', self.uuid,
                            'statistic')
        return super(LSwitchPort, self)._action("DELETE", uri)

    @requireuuid
    def status(self):
        """Status (verb) will return the logical port's status"""
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport', self.uuid,
                            'status')
        return super(LSwitchPort, self)._action("GET", uri)

    @requireuuid
    def delete(self):
        """Delete (verb) will delete the logical port.
        Requires a UUID set at the object"""
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport', self.uuid)
        return super(LSwitchPort, self)._action("DELETE", uri)

    @requireuuid
    def update(self):
        """Update (verb) will update the logical switch port
        Requires a UUID set at the object.
        """
        uri = common.genuri('lswitch', self.lswitch_uuid, 'lport', self.uuid)
        return super(LSwitchPort, self)._action('PUT', uri)
