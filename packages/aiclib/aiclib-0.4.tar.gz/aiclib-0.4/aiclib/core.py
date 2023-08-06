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
Created on August 17, 2012

@author: Justin Hammond, Rackspace Hosting
"""

import json
import logging
import errno
import socket
import time
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import urllib3

import common


logger = logging.getLogger(__name__)


class CoreLib(object):

    def __init__(self, uri, poolmanager=None, username='admin',
                 password='admin'):
        """Constructor for the AICLib object.

        Arguments:
        uri -- the address of the nvp controller including scheme (required)

        Keyword arguments:
        poolmanager -- a pool manager provided by urlib3 (default None)
        username -- the username to log into the nvp controller
        password -- the password to log into the nvp controller
        """
        if poolmanager is None:
            self.conn = urllib3.connection_from_url(uri)

        else:
            self.conn = poolmanager.connection_from_url(uri)

        self.connection = Connection(connection=self.conn,
                                     username=username,
                                     password=password)

    def _action(self, entity, method, resource):
        if entity is None:
            return

        logger.info("(%s @ %s): %s" % (method, resource,
                                       entity._unroll()))
        try:
            r = self.connection.request(method, resource,
                                        body=entity._unroll())
        except socket.error, v:
            errorcode = v[0]

            if errorcode == errno.ECONNREFUSED:
                logger.error("Connection refused")

            raise urllib3.exceptions.HTTPError("Connection refused")
        return r


class Entity(dict):

    def __init__(self, connection):
        self.connection = connection

    def _action(self, method, resource):
        """This is the ancestor method that all 'verbs' must call to perform
        an action.
        """
        return self.connection._action(self, method, resource)

    def _unroll(self):
        return self


class Query(object):

    def __init__(self, connection, resource):
        self.connection = connection
        self.query = {}
        self.resource = resource

    def _query(self, method):
        return self.connection._action(self, method, self.resource)

    def _unroll(self):
        return self.query


class Connection(object):
    _encode_url_methods = set(['DELETE', 'GET', 'HEAD', 'OPTIONS'])
    _encode_body_methods = set(['PATCH', 'POST', 'PUT', 'TRACE'])

    def __init__(self, username, password, connection=None):
        self._conn = connection
        self.authenticated = False
        self.username = username
        self.password = password
        self.maxRetries = 5
        self._headers = {}
        self.generationnumber = 0
        self.authkey = ''

    @property
    def connection(self):
        if(not self.authenticated and
           not self._login(self.username, self.password)):
                logger.error("Authorization failed.")
                raise IOError('401', 'Unauthorized')
        return self._conn

    def _login(self, username, password):
        fields = {'username': username, 'password': password}
        r = self._conn.request_encode_body('POST', common.genuri('login'),
                                           fields=fields,
                                           encode_multipart=False)
        if self._iserror(r):
            logger.error("Need to handle error")
            return False
        else:
            self.authkey = r.headers['set-cookie']
            logger.info("Authorized (%s)" % (self.authkey))
        self.authenticated = True
        return True

    @property
    def headers(self):
        self._headers = {
            'Cookie': self.authkey,
            'Content-Type': 'application/json',
            'X-Nvp-Wait-For-Config-Generation': self.generationnumber,
        }
        return self._headers

    def request(self, method, apicall, generationnumber=0, body=None):
        retrypause = 0
        internalramp = 10
        url = apicall

        # TODO(jkoelker) refactor this to use the retry kwarg to urlopen
        for retryCount in xrange(self.maxRetries):
            self.generationnumber = generationnumber
            json_body = json.dumps(body)

            if method in self._encode_url_methods:
                logger.info("Encoded URL: %s" % urlencode(body))
                url += '?' + urlencode(body, doseq=True)
                r = self.connection.urlopen(method, url,
                                            headers=self.headers)

            else:
                r = self.connection.urlopen(method, apicall,
                                            json_body,
                                            headers=self.headers)

            if self._iserror(r):
                try:
                    self._handle_error(r)
                    continue

                except EnvironmentError:
                    if 'retry-after' in r.headers:
                        logger.info("Waiting for server: ",
                                    r.headers['retry-after'])
                        retrypause = r.headers['retry-after']
                        time.sleep(retrypause)

                    else:
                        logger.info("Headers missing retry delay")
                        self.connection.close()

                        time.sleep(internalramp)
                        internalramp += .5
                except:
                    logger.error("Unhandled error:")
                    raise

            self._handle_headers(r)
            return r

        raise AICException(408, 'Request Timeout -- Maxed retry attempts')

    def _handle_headers(self, resp):
        return

    def _iserror(self, resp):
        errorcheck = resp.status - 200
        if errorcheck >= 100:
            return True
        logger.info("Request success %s (%s)" % (resp.status, resp.reason))
        return False

    def _handle_error(self, resp):
        logger.info("Received error %s (%s)" % (resp.status, resp.reason))
        comment = "%s: %s" % (resp.reason, resp.data)

        if resp.status == 400:
            logger.error("Bad request")
            raise AICException(400, comment)

        elif resp.status == 401:
            logger.info("Authorization expired; renewing")
            self.authenticated = False
            authstatus = self._login(self.username, self.password)

            if not authstatus:
                logger.error("Re-authorization failed.")
                raise AICException(401, 'Unauthorized')

        elif resp.status == 403:
            logger.error("Access forbidden")
            raise AICException(403, comment)

        elif resp.status == 404:
            logger.error("Resource not found")
            raise AICException(404, comment)

        elif resp.status == 409:
            logger.error("Conflicting configuration")
            raise AICException(409, comment)

        elif resp.status == 500:
            logger.error("Internal server error")
            raise AICException(500, comment)

        elif resp.status == 503:
            logger.error("Service unavailable")
            raise AICException(503, comment)


class AICException(Exception):

    def __init__(self, error_code, message, **kwargs):
        super(AICException, self).__init__(kwargs)
        self.code = error_code
        self.message = message
