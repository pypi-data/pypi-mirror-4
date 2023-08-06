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

logger = logging.getLogger(__name__)


class NVPBaseQuery(core.Query):

    def __init__(self, aic_connection, resource):
        super(NVPBaseQuery, self).__init__(aic_connection, resource)
        logger.info("Created NVPBaseQuery")
        self.query['fields'] = '*'

    def fields(self, fieldlist):
        if isinstance(fieldlist, str):
            fieldlist = [fieldlist]
        self.query['fields'] = ','.join(fieldlist)
        return self

    def results(self):
        results = super(NVPEntityQuery, self)._query('GET')
        return results


class NVPEntityQuery(NVPBaseQuery):

    def __init__(self, aic_connection, resource):
        super(NVPEntityQuery, self).__init__(aic_connection, resource)
        logger.info("Created NVPEntityQuery")
        self.query['_page_length'] = 1000
        self.nextpage = None

    def length(self, page):
        self.query['_page_length'] = page
        return self

    def alert(self, flag):
        self.query['alert'] = 'true' if flag else 'false'
        return self

    def alert_changed_since(self, comparison, date_time):
        """Comparison operator (string): >,>=,<,<=,=,!=
        """
        query_value = "%s%s" % (comparison, common.dttounix(date_time))
        self.query['alert_changed_since'] = query_value
        return self

    def display_name(self, name):
        self.query['display_name'] = name
        return self

    def identifier(self, ident):
        self.query['identifier'] = ident
        return self

    def last_modified(self, comparison, date_time):
        """Comparison operator (string): >,>=,<,<=,=,!=
        """
        query_value = "%s%s" % (comparison, common.dttounix(date_time))
        self.query['last_modified'] = query_value
        return self

    def tags(self, taglist):
        self.query['tag'] = taglist
        return self

    def tagscopes(self, tagscopelist):
        self.query['tag_scope'] = tagscopelist
        return self

    def uuid(self, uid):
        self.query['uuid'] = uid
        return self

    def next(self):
        if not self.nextpage:
            return None
        self.query['_page_cursor'] = self.nextpage
        return self.results()

    def results(self):
        results = super(NVPEntityQuery, self).results()
        if type(results) is dict and 'page_cursor' in results:
            self.nextpage = results['page_cursor']
        else:
            self.nextpage = None
        return results


class QOSQueueQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(QOSQueueQuery, self).results()


class SecurityProfileQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(SecurityProfileQuery, self).results()


class LRouterQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(LRouterQuery, self).results()


class TransportNodeQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(TransportNodeQuery, self).results()


class MDIServiceQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(MDIServiceQuery, self).results()


class TransportZoneQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(TransportZoneQuery, self).results()


class GatewayServiceQuery(NVPEntityQuery):
    #TODO: Add all entity specific features

    def results(self):
        return super(GatewayServiceQuery, self).results()


class LSwitchPortQuery(NVPEntityQuery):

    def admin_status_enabled(self, flag):
        self.query['admin_status_enabled'] = 'true' if flag else 'false'
        return self

    def attachment_bridge_id(self, string_operator, bridgeid):
        """Uses string matching on bridgeid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_bridge_id'] = '%s%s' % (string_operator,
                                                       bridgeid)
        return self

    def attachment_gwsvc_uuid(self, string_operator, gwsvcuuid):
        """Uses string matching on gwsvcuuid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_gwsvc_uuid'] = '%s%s' % (string_operator,
                                                        gwsvcuuid)
        return self

    def attachment_node_name(self, string_operator, nodename):
        """Uses string matching on nodename"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_node_name'] = '%s%s' % (string_operator,
                                                       nodename)
        return self

    def attachment_node_uuid(self, string_operator, nodeuuid):
        """Uses string matching on nodeuuid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_node_uuid'] = '%s%s' % (string_operator,
                                                       nodeuuid)
        return self

    def attachment_peer_port_uuid(self, string_operator, peerport):
        """Uses string matching on peerport"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_peer_port_uuid'] = '%s%s' % (string_operator,
                                                            peerport)
        return self

    def attachment_vif_mac(self, string_operator, vifmac):
        """Uses string matching on vifmac"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_vif_mac'] = '%s%s' % (string_operator,
                                                     vifmac)
        return self

    def attachment_vif_uuid(self, string_operator, vifuuid):
        """Uses string matching on vifuuid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_vif_uuid'] = '%s%s' % (string_operator,
                                                      vifuuid)
        return self

    def attachment_zone_uuid(self, string_operator, zoneuuid):
        """Uses string matching on zoneuuid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['attachment_zone_uuid'] = '%s%s' % (string_operator,
                                                       zoneuuid)
        return self

    def queue_uuid(self, string_operator, queueuuid):
        """Uses string matching on queueuuid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['queue_uuid'] = '%s%s' % (string_operator,
                                             queueuuid)
        return self

    def security_profile_uuid(self, string_operator, secuuid):
        """Uses string matching on secuuid"""
        if not common.is_stringop(string_operator):
            raise AttributeError("string_operator is invalid")
        self.query['security_profile_uuid'] = '%s%s' % (string_operator,
                                                        secuuid)
        return self

    def relations(self, relationslist):
        """Make a comment"""
        self.query['relations'] = relationslist
        return self

    def results(self):
        return super(LSwitchPortQuery, self).results()


class LSwitchQuery(NVPEntityQuery):

    def port_isolation(self, flag):
        self.query['port_isolation'] = 'true' if flag else 'false'
        return self

    def transport_zone_name(self, name):
        self.query['transport_zone_name'] = name
        return self

    def transport_zone_uuid(self, uid):
        self.query['transport_zone_uuid'] = uid
        return self

    def relations(self, relationslist):
        """Make a comment"""
        self.query['relations'] = relationslist
        return self

    def results(self):
        #TODO: This may require some modifications at this level
        return super(LSwitchQuery, self).results()
