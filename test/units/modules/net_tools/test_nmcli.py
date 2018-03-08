# Copyright: (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import json

from ansible.modules.net_tools import nmcli

pytestmark = pytest.mark.usefixtures('patch_ansible_module')

TESTCASE_CONNECTION = [
    {
        'type': 'ethernet',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'generic',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'team',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'bond',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'bond-slave',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'bridge',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'vlan',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
]

TESTCASE_GENERIC = [
    {
        'type': 'generic',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'generic_non_existant',
        'ip4': '10.10.10.10',
        'gw4': '10.10.10.1',
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_BOND = [
    {
        'type': 'bond',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'bond_non_existant',
        'mode': 'active-backup',
        'ip4': '10.10.10.10',
        'gw4': '10.10.10.1',
        'state': 'present',
        'primary': 'non_existent_primary',
        '_ansible_check_mode': False,
    }
]


def mocker_set(mocker, connection_exists=False):
    """
    Common mocker object
    """
    mocker.patch('ansible.modules.net_tools.nmcli.HAVE_DBUS', True)
    mocker.patch('ansible.modules.net_tools.nmcli.HAVE_NM_CLIENT', True)
    get_bin_path = mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')
    get_bin_path.return_value = '/usr/bin/nmcli'
    connection = mocker.patch.object(nmcli.Nmcli, 'connection_exists')
    connection.return_value = connection_exists
    return connection


@pytest.fixture
def mocked_generic_connection_create(mocker):
    mocker_set(mocker)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = {"rc": 100, "out": "aaa", "err": "none"}
    return command_result


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BOND, indirect=['patch_ansible_module'])
def test_bond_connection_create(mocked_generic_connection_create):
    """
    Test : Bond connection created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'bond'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'
    assert args[0][7] == 'ifname'
    assert args[0][8] == 'bond_non_existant'
    assert args[0][9] == 'mode'
    assert args[0][10] == 'active-backup'
    assert args[0][11] == 'ip4'
    assert args[0][12] == '10.10.10.10'
    assert args[0][13] == 'gw4'
    assert args[0][14] == '10.10.10.1'
    assert args[0][15] == 'primary'
    assert args[0][16] == 'non_existent_primary'


def mocker_set(mocker, connection_exists=False):
    """
    Common mocker object
    """
    mocker.patch('ansible.modules.net_tools.nmcli.HAVE_DBUS', True)
    mocker.patch('ansible.modules.net_tools.nmcli.HAVE_NM_CLIENT', True)
    get_bin_path = mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')
    get_bin_path.return_value = '/usr/bin/nmcli'
    connection = mocker.patch.object(nmcli.Nmcli, 'connection_exists')
    connection.return_value = connection_exists
    return connection


@pytest.fixture
def mocked_generic_connection_create(mocker):
    mocker_set(mocker)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = {"rc": 100, "out": "aaa", "err": "none"}
    return command_result


@pytest.fixture
def mocked_generic_connection_modify(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = {"rc": 100, "out": "aaa", "err": "none"}
    return command_result


@pytest.fixture
def mocked_connection_exists(mocker):
    connection = mocker_set(mocker, connection_exists=True)
    return connection


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC, indirect=['patch_ansible_module'])
def test_generic_connection_create(mocked_generic_connection_create):
    """
    Test : Generic connection created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'generic'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'
    assert args[0][9] == 'ip4'
    assert args[0][10] == '10.10.10.10'
    assert args[0][11] == 'gw4'
    assert args[0][12] == '10.10.10.1'


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC, indirect=['patch_ansible_module'])
def test_generic_connection_modify(mocked_generic_connection_modify):
    """
    Test : Generic connection modify
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'
    assert args[0][4] == 'ipv4.address'
    assert args[0][5] == '10.10.10.10'
    assert args[0][6] == 'ipv4.gateway'
    assert args[0][7] == '10.10.10.1'


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_CONNECTION, indirect=['patch_ansible_module'])
def test_dns4_none(mocked_connection_exists, capfd):
    """
    Test if DNS4 param is None
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert results['changed']
