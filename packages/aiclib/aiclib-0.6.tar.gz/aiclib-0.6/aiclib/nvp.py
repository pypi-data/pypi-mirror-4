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
Created on August 23, 2012

@author: Justin Hammond, Rackspace Hosting
"""

import json
import logging

import common
import core
import nvpentity

logger = logging.getLogger(__name__)
_version = 'ws.v1'


def grab_uuid_of_type(text_or_dict, nvptype):
    if not type(text_or_dict) is dict:
        return text_or_dict
    errormsg = "Missing key (%s) from dictionary when expected."
    typeerror = "Incorrect type (%s); expected %s"
    if not 'uuid' in text_or_dict:
        logger.error(errormsg % "uuid")
        raise TypeError(errormsg % "uuid")
    if nvptype and not 'type' in text_or_dict:
        logger.error(errormsg % "type")
        raise TypeError(errormsg % "type")
        if text_or_dict['type'] != nvptype:
            logger.error(typeerror % (text_or_dict['type'], nvptype))
            raise TypeError(typeerror % (text_or_dict['type'], nvptype))
    return text_or_dict['uuid']


class Connection(core.CoreLib):

    def __init__(self, uri, poolmanager=None, username='admin',
                 password='admin'):
        super(Connection, self).__init__(uri, poolmanager, username, password)

    def nvp_function(self):
        entity = NVPFunction(self)
        return entity

    def lswitch(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, "LogicalSwitchConfig")
        entity = nvpentity.LSwitch(self, uuid=uuidvalue)
        return entity

    def qos(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.QOSQueue(self, uuid=uuidvalue)
        return entity

    def securityrule(self, ethertype):
        entity = nvpentity.SecurityRule(ethertype)
        return entity

    def securityprofile(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.SecurityProfile(self, uuid=uuidvalue)
        return entity

    def lrouter(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.LRouter(self, uuid=uuidvalue)
        return entity

    def transportconnector(self, uuid, connector_type):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.TransportConnector(uuidvalue, connector_type)
        return entity

    def transportnode(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.TransportNode(self, uuid=uuidvalue)
        return entity

    def gatewayservice(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.GatewayService(self, uuid=uuidvalue)
        return entity

    def zone(self, uuid=None):
        uuidvalue = grab_uuid_of_type(uuid, None)
        entity = nvpentity.TransportZone(self, uuid=uuidvalue)
        return entity

    def lswitch_port(self, lswitch_uuid, uuid=None):
        """Will create an Logical Switch port on the passed Logical switch
        or passed UUID of a Logical switch"""
        lswitch_uuid_value = grab_uuid_of_type(lswitch_uuid,
                                               "LogicalSwitchConfig")
        lport_uuid_value = grab_uuid_of_type(uuid,
                                             "LogicalSwitchPortConfig")
        entity = nvpentity.LSwitchPort(self, lswitch_uuid_value,
                                       lport_uuid_value)
        return entity

    def _action(self, entity, method, resource):
        """Will inject generation ID into the JSON result object if it exists
        """
        try:
            r = super(Connection, self)._action(entity, method, resource)
        except core.AICException as e:
            if e.code == 400 or e.code == 500:
                raise NVPException()
            elif e.code == 403:
                raise Forbidden()
            elif e.code == 404:
                raise ResourceNotFound()
            elif e.code == 408:
                raise RequestTimeout()
            elif e.code == 409:
                raise Conflict()
            elif e.code == 503:
                raise ServiceUnavailable()
            else:
                raise NVPException()

        logger.info("Response headers: %s" % r.headers)
        responselength = 0
        generationid = None

        if 'x-nvp-config-generation' in r.headers:
            generationid = r.getheader('x-nvp-config-generation')

        if 'content-length' in r.headers:
            responselength = int(r.getheader('content-length'))

        if responselength > 0:
            if r.getheader('content-type') == 'application/json':
                jsonreturn = json.loads(r.data)

                if generationid:
                    jsonreturn['_generationid'] = generationid
                return jsonreturn

            else:
                return r.data
        return


class NVPFunction(core.Entity):

    def __init__(self, connection):
        super(NVPFunction, self).__init__(connection)

    def logout(self):
        uri = common.genuri("logout")
        return super(NVPFunction, self)._action('GET', uri)

    def get_method_uris(self):
        uri = common.genuri("doc", "method")
        return super(NVPFunction, self)._action('GET', uri)

    def read_method(self, method_name):
        uri = common.genuri("doc", "method", method_name)
        return super(NVPFunction, self)._action('GET', uri)

    def get_schemas(self):
        uri = common.genuri("schema")
        return super(NVPFunction, self)._action('GET', uri)

    def read_schema(self, schema_name):
        uri = common.genuri("schema", schema_name)
        return super(NVPFunction, self)._action('GET', uri)


class NVPException(Exception):
    """This Exception class was created to duplicate the exception resolution
    available in legacy NvpApiClient.
    """
    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        try:
            self._error_string = self.message % kwargs

        except Exception:
            self._error_string = self.message

    def __str__(self):
        return self._error_string


class UnauthorizedRequest(NVPException):
    message = "Server denied session's authentication credentials."


class ResourceNotFound(NVPException):
    message = "An entity referenced in the request was not found."


class Conflict(NVPException):
    message = "Request conflicts with configuration on a different entity."


class ServiceUnavailable(NVPException):
    message = ("Request could not be completed because the associated "
               "resource could not be reached")


class Forbidden(NVPException):
    message = "The request is forbidden from access the referenced resource"


class RequestTimeout(NVPException):
    message = "The request has timed out."
