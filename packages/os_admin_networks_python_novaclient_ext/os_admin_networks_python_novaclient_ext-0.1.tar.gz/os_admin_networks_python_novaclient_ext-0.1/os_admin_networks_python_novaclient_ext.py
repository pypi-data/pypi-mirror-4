# Copyright 2012 OpenStack, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from novaclient import base
from novaclient import utils


class AdminNetwork(base.Resource):
    """
    A network.
    """
    HUMAN_ID = False
    NAME_ATTR = "label"

    def __repr__(self):
        return "<Network: %s>" % self.label

    def delete(self):
        self.manager.delete(self)


class AdminNetworkManager(base.ManagerWithFind):
    """
    Manage :class:`AdminNetwork` resources.
    """
    resource_class = AdminNetwork

    def list(self):
        """
        Get a list of all networks.

        :rtype: list of :class:`Network`.
        """
        return self._list("/os-admin-networks", "networks")

    def get(self, network):
        """
        Get a specific network.

        :param network: The ID of the :class:`Network` to get.
        :rtype: :class:`Network`
        """
        return self._get("/os-admin-networks/%s" % base.getid(network),
                         "network")

    def delete(self, network):
        """
        Delete a specific network.

        :param network: The ID of the :class:`Network` to delete.
        """
        self._delete("/os-admin-networks/%s" % base.getid(network))

    def create(self, **kwargs):
        """
        Create (allocate) a network. The following parameters are
        optional except for label; cidr or cidr_v6 must be specified, too.

        :param label: str
        :param bridge: str
        :param bridge_interface: str
        :param cidr: str
        :param cidr_v6: str
        :param dns1: str
        :param dns2: str
        :param fixed_cidr: str
        :param gateway: str
        :param gateway_v6: str
        :param multi_host: str
        :param priority: str
        :param project_id: str
        :param vlan_start: int
        :param vpn_start: int

        :rtype: list of :class:`Network`
        """
        body = {"network": kwargs}
        return self._create('/os-admin-networks', body, 'network')

    def disassociate(self, network):
        """
        Disassociate a specific network from project.

        :param network: The ID of the :class:`Network` to get.
        """
        self.api.client.post("/os-admin-networks/%s/action" %
                             base.getid(network), body={"disassociate": None})

    def add(self, network=None):
        """
        Associates the current project with a network. Network can be chosen
        automatically or provided explicitly.

        :param network: The ID of the :class:`Network` to associate (optional).
        """
        self.api.client.post(
            "/os-admin-networks/add",
            body={"id": base.getid(network) if network else None})


def do_admin_network_list(cs, _args):
    """Print a list of available networks."""
    network_list = cs.os_admin_networks_python_novaclient_ext.list()
    columns = ['ID', 'Label', 'Cidr']
    utils.print_list(network_list, columns)


@utils.arg('network',
     metavar='<network>',
     help="uuid or label of network")
def do_admin_network_show(cs, args):
    """Show details about the given network."""
    network = utils.find_resource(cs.os_admin_networks_python_novaclient_ext,
                                  args.network)
    utils.print_dict(network._info)
