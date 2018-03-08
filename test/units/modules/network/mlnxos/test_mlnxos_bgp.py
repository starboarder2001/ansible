#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.compat.tests.mock import patch
from ansible.modules.network.mlnxos import mlnxos_bgp
from units.modules.utils import set_module_args
from .mlnxos_module import TestMlnxosModule, load_fixture


class TestMlnxosBgpModule(TestMlnxosModule):

    module = mlnxos_bgp

    def setUp(self):
        super(TestMlnxosBgpModule, self).setUp()
        self.mock_get_config = patch.object(
            mlnxos_bgp.MlnxosBgpModule, "_get_bgp_summary")
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            'ansible.module_utils.network.mlnxos.mlnxos.load_config')
        self.load_config = self.mock_load_config.start()

    def tearDown(self):
        super(TestMlnxosBgpModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_load_config.stop()

    def load_fixtures(self, commands=None, transport='cli'):
        config_file = 'mlnxos_bgp_show.cfg'
        self.get_config.return_value = load_fixture(config_file)
        self.load_config.return_value = None

    def test_bgp_no_change(self):
        neighbor = dict(remote_as=173, neighbor='10.2.3.4')
        set_module_args(dict(as_number=172, router_id='1.2.3.4',
                             neighbors=[neighbor]))
        self.execute_module(changed=False)

    def test_bgp_remove(self):
        set_module_args(dict(as_number=172, state='absent'))
        commands = ['no router bgp 172']
        self.execute_module(changed=True, commands=commands)

    def test_bgp_change(self):
        neighbor = dict(remote_as=173, neighbor='10.2.3.4')
        set_module_args(dict(as_number=174, router_id='1.2.3.4',
                             neighbors=[neighbor]))
        commands = ['no router bgp 172', 'router bgp 174', 'exit',
                    'router bgp 174 router-id 1.2.3.4 force',
                    'router bgp 174 neighbor 10.2.3.4 remote-as 173']
        self.execute_module(changed=True, commands=commands)

    def test_bgp_add_neighbor(self):
        neighbors = [dict(remote_as=173, neighbor='10.2.3.4'),
                     dict(remote_as=175, neighbor='10.2.3.5')]
        set_module_args(dict(as_number=172, router_id='1.2.3.4',
                             neighbors=neighbors))
        commands = ['router bgp 172 neighbor 10.2.3.5 remote-as 175']
        self.execute_module(changed=True, commands=commands)

    def test_bgp_del_neighbor(self):
        set_module_args(dict(as_number=172))
        commands = ['router bgp 172 no neighbor 10.2.3.4 remote-as 173']
        self.execute_module(changed=True, commands=commands)
