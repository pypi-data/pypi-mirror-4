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


def tag(scope, value):
    """Create a Tag dict."""
    return {'scope': scope, 'tag': value}


def tags(obj):
    """Tards or untards an object's tags."""
    if 'tags' in obj:
        return dict((t['scope'], t['tag']) for t in obj['tags'])
    return [tag(k, v) for k, v in obj.iteritems()]


def copy_securityrule(securityrule):
    """Return a new SecurityRule dict with profile_uuid removed."""
    return dict((k, v) for k, v in securityrule.iteritems()
                if k != 'profile_uuid')
