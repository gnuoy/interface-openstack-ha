#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class OpenstackHAPeers(RelationBase):
    scope = scopes.UNIT

    @hook('{peers:openstack-ha}-relation-joined')
    def joined(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.connected')

    @hook('{peers:openstack-ha}-relation-changed')
    def changed(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.connected')
        if self.data_complete(conv):
            conv.set_state('{relation_name}.available')

    def ip_map(self, address_key='private-address'):
        nodes = []
        for conv in self.conversations():
            host_name = conv.scope.replace('/', '-')
            nodes.append((host_name, conv.get_remote(address_key)))

        return nodes

    @hook('{peers:openstack-ha}-relation-{broken,departed}')
    def departed_or_broken(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.connected')
        if not self.data_complete(conv):
            conv.remove_state('{relation_name}.available')

    def data_complete(self, conv):
        """
        Get the connection string, if available, or None.
        """
        data = {
            'private_address': conv.get_remote('private-address'),
        }
        if all(data.values()):
            return True
        return False
