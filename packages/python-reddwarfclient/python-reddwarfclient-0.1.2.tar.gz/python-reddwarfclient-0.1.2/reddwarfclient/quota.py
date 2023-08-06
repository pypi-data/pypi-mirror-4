# Copyright (c) 2011 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from reddwarfclient import base
from reddwarfclient.common import check_for_exceptions


class Quota(base.Resource):
    """
    Quota is a resource used to hold quota information.
    """
    def __repr__(self):
        return "<Quota: %s>" % self.name


class Quotas(base.ManagerWithFind):
    """
    Manage :class:`Quota` information.
    """

    resource_class = Quota

    def show(self, tenant_id):
        """Get a list of all quotas for a tenant id"""

        url = "/mgmt/quotas/%s" % tenant_id
        resp, body = self.api.client.get(url)
        check_for_exceptions(resp, body)
        if not body:
            raise Exception("Call to " + url + " did not return a body.")
        return base.Resource(self, body)

    def update(self, tenant_id, instances, volume_size):
        """
        Set limits for quotas
        """
        url = "/mgmt/quotas/%s" % tenant_id
        body = {"quotas": {"instances": instances, "volumes": volume_size}}
        resp, body = self.api.client.put(url, body=body)
        check_for_exceptions(resp, body)
        if not body:
            raise Exception("Call to " + url + " did not return a body.")
        return base.Resource(self, body)
