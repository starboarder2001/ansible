.. _porting_2.5_guide:

*************************
Ansible 2.5 Porting Guide
*************************

This section discusses the behavioral changes between Ansible 2.4 and Ansible 2.5.

It is intended to assist in updating your playbooks, plugins and other parts of your Ansible infrastructure so they will work with this version of Ansible.

We suggest you read this page along with `Ansible Changelog <https://github.com/ansible/ansible/blob/devel/CHANGELOG.md#2.5>`_ to understand what updates you may need to make.

This document is part of a collection on porting. The complete list of porting guides can be found at :ref:`porting guides <porting_guides>`.

.. contents:: Topics

Playbook
========

Dynamic includes and attribute inheritance
------------------------------------------

In Ansible version 2.4, the concept of dynamic includes (``include_tasks``) versus static imports (``import_tasks``) was introduced to clearly define the differences in how ``include`` works between dynamic and static includes. 

All attributes applied to a dynamic ``include_*`` would only apply to the include itself, while attributes applied to a
static ``import_*`` would be inherited by the tasks within.

This separation was only partially implemented in Ansible version 2.4. As of Ansible version 2.5, this work is complete and the separation now behaves as designed; attributes applied to an ``include_*`` task will not be inherited by the tasks within. 

To achieve an outcome similar to how Ansible worked prior to version 2.5, playbooks
should use an explicit application of the attribute on the needed tasks, or use blocks to apply the attribute to many tasks. Another option is to use a static ``import_*`` when possible instead of a dynamic task.

**OLD** In Ansible 2.4:

.. code-block:: yaml

    - include_tasks: "{{ ansible_distribution }}.yml"
      tags:
        - distro_include


**NEW** In Ansible 2.5:

Including task:

.. code-block:: yaml

    - include_tasks: "{{ ansible_distribution }}.yml"
      tags:
        - distro_include

Included file:

.. code-block:: yaml

    - block:
        - debug:
            msg: "In included file"

        - apt:
            name: nginx
            state: latest
      tags:
        - distro_include

Deprecated
==========

Jinja tests used as filters
---------------------------

Using Ansible-provided jinja tests as filters will be removed in Ansible 2.9.

Prior to Ansible 2.5, jinja tests included within Ansible were most often used as filters. The large difference in use is that filters are referenced as ``variable | filter_name`` where as jinja tests are refereced as ``variable is test_name``.

Jinja tests are used for comparisons, while filters are used for data manipulation and have different applications in jinja. This change is to help differentiate the concepts for a better understanding of jinja, and where each can be appropriately used.

As of Ansible 2.5, using an Ansible provided jinja test with filter syntax, will display a deprecation error.

**OLD** In Ansible 2.4 (and earlier) the use of an Ansible included jinja test would likely look like this:

.. code-block:: yaml

    when:
        - result | failed
        - not result | success

**NEW** In Ansible 2.5 it should be changed to look like this:

.. code-block:: yaml

    when:
        - result is failed
        - results is not successful

In addition to the deprecation warnings, many new tests have been introduced that are aliases of the old tests. These new tests make more sense grammatically with the jinja test syntax, such as the new ``successful`` test which aliases ``success``.

.. code-block:: yaml

    when: result is successful

See :doc:`playbooks_tests` for more information.

Additionally, a script was created to assist in the conversion for tests using filter syntax to proper jinja test syntax. This script has been used to convert all of the Ansible integration tests to the correct format. There are a few limitations documented, and all changes made by this script should be evaluated for correctness before executing the modified playbooks. The script can be found at `https://github.com/ansible/ansible/blob/devel/hacking/fix_test_syntax.py <https://github.com/ansible/ansible/blob/devel/hacking/fix_test_syntax.py>`_.

Modules
=======

Major changes in popular modules are detailed here.

github_release
--------------

In Ansible versions 2.4 and older, after creating a GitHub release using the ``create_release`` state, the ``github_release`` module reported state as ``skipped``.
In Ansible version 2.5 and later, after creating a GitHub release using the ``create_release`` state, the ``github_release`` module now reports state as ``changed``.


Modules removed
---------------

The following modules no longer exist:

* :ref:`nxos_mtu <nxos_mtu>` use :ref:`nxos_system <nxos_system>`'s ``system_mtu`` option or :ref:`nxos_interface <nxos_interface>` instead
* :ref:`cl_interface_policy <cl_interface_policy>` use :ref:`nclu <nclu>` instead
* :ref:`cl_bridge <cl_bridge>` use :ref:`nclu <nclu>` instead
* :ref:`cl_img_install <cl_img_install>` use :ref:`nclu <nclu>` instead
* :ref:`cl_ports <cl_ports>` use :ref:`nclu <nclu>` instead
* :ref:`cl_license <cl_license>` use :ref:`nclu <nclu>` instead
* :ref:`cl_interface <cl_interface>` use :ref:`nclu <nclu>` instead
* :ref:`cl_bond <cl_bond>` use :ref:`nclu <nclu>` instead
* :ref:`ec2_vpc <ec_vpc>` use :ref:`ec2_vpc_net <ec2_vpc_net>` along with supporting modules :ref:`ec2_vpc_igw <ec2_vpc_igw>`, :ref:`ec2_vpc_route_table <ec2_vpc_route_table>`, :ref:`ec2_vpc_subnet <ec2_vpc_subnet>`, :ref:`ec2_vpc_dhcp_options <ec2_vpc_dhcp_options>`, :ref:`ec2_vpc_nat_gateway <ec2_vpc_nat_gateway>`, :ref:`ec2_vpc_nacl <ec2_vpc_nacl>` instead.
* :ref:`ec2_ami_search <ec2_ami_search` use :ref:`ec2_ami_facts <ec2_ami_facts>` instead
* :ref:`docker <docker>` use :ref:`docker_container <docker_container>` and :ref:`docker_image <docker_image>` instead

Deprecation notices
-------------------

The following modules will be removed in Ansible 2.9. Please update update your playbooks accordingly.

* Apstra's ``aos_*`` modules are deprecated as they do not work with AOS 2.1 or higher. See new modules at `https://github.com/apstra <https://github.com/apstra>`_.
* :ref:`nxos_ip_interface <nxos_ip_interface>` use :ref:`nxos_l3_interface <nxos_l3_interface>` instead.
* :ref:`nxos_portchannel <nxos_portchannel>` use :ref:`nxos_linkagg <nxos_linkagg>` instead.
* :ref:`nxos_switchport <nxos_switchport>` use :ref:`nxos_l2_interface <nxos_l2_interface>` instead.
* :ref:`panos_security_policy <panos_security_policy>` use :ref:`panos_security_rule <panos_security_rule>` instead.
* :ref:`panos_nat_policy <panos_nat_policy>` use :ref:`panos_nat_rule <panos_nat_rule>` instead.
* :ref:`vsphere_guest <vsphere_guest>` use :ref:`vmware_guest <vmware_guest>` instead.

Noteworthy module changes
-------------------------

* The :ref:`stat <stat>` and :ref:`win_stat <win_stat>` modules have changed the default of the option ``get_md5`` from ``true`` to ``false``.

This option will be removed starting with Ansible version 2.9. The options ``get_checksum: True``
and ``checksum_algorithm: md5`` can still be used if an MD5 checksum is
desired.

* ``osx_say`` module was renamed into :ref:`say <say>`.

Plugins
=======

As a developer, you can now use 'doc fragments' for common configuration options on plugin types that support the new plugin configuration system.

Inventory
---------

Inventory plugins have been fine tuned, and we have started to add some common features:

* The ability to use a cache plugin to avoid costly API/DB queries is disabled by default.
  If using inventory scripts, some may already support a cache, but it is outside of Ansible's knowledge and control.
  Moving to the interal cache will allow you to use Ansible's existing cache refresh/invalidation mechanisms.

* A new 'auto' plugin, enabled by default, that can automatically detect the correct plugin to use IF that plugin is using our 'common YAML configuration format'.
  The previous host_list, script, yaml and ini plugins still work as they did, the auto plugin is now the last one we attempt to use.
  If you had customized the enabled plugins you should revise the setting to include the new auto plugin.

Shell
-----

Shell plugins have been migrated to the new plugin configuration framework. It is now possible to customize more settings, and settings which were previously 'global' can now also be overriden using host specific variables.

For example, ``system_temps`` is a new setting that allows you to control what Ansible will consider a 'system temporary dir'. This is used when escalating privileges for a non-administrative user. Previously this was hardcoded to '/tmp', which some systems cannot use for privilege escalation. This setting now defaults to ``[ '/var/tmp', '/tmp']``.

Another new setting is ``admin_users`` which allows you to specify a list of users to be considered 'administrators'. Previouslu this was hardcoded to ``root``. It now it defaults to ``[root, toor, admin]``.  This information is used when choosing between your ``remote_temp`` and ``system_temps`` directory.

For a full list, check the shell plugin you are using, the default shell plugin is ``sh``.

Those that had to work around the global configuration limitations can now migrate to a per host/group settings,
but also note that the new defaults might conflict with existing usage if the assumptions don't correlate to your environment.


Porting custom scripts
======================

No notable changes.

Networking
==========


Change in deprecation notice of top-level connection arguments
--------------------------------------------------------------
.. code-block:: yaml

    - name: example of using top-level options for connection properties
      ios_command:
        commands: show version
        host: "{{ inventory_hostname }}"
        username: cisco
        password: cisco
        authorize: yes
        auth_pass: cisco

**OLD** In Ansible 2.4:

Will result in:

.. code-block:: yaml

   [WARNING]: argument username has been deprecated and will be removed in a future version
   [WARNING]: argument host has been deprecated and will be removed in a future version
   [WARNING]: argument password has been deprecated and will be removed in a future version


**NEW** In Ansible 2.5:


.. code-block:: yaml

   [DEPRECATION WARNING]: Param 'username' is deprecated. See the module docs for more information. This feature will be removed in version
   2.9. Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
   [DEPRECATION WARNING]: Param 'password' is deprecated. See the module docs for more information. This feature will be removed in version
   2.9. Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
   [DEPRECATION WARNING]: Param 'host' is deprecated. See the module docs for more information. This feature will be removed in version 2.9.
   Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.

Notice when using provider dictionary with new persistent connection types
--------------------------------------------------------------------------

Using a provider dictionary with one of the new persistent connection types for networking
(network_cli, netconf, etc.) will result in a warning. When using these connections
the standard Ansible infrastructure for controlling connections should be used.
(Link to basic inventory documentation?)

Developers: Shared Module Utilities Moved
-----------------------------------------

Beginning with Ansible 2.5, shared module utilities for network modules moved to ``ansible.module_utils.network``. 

* Platform-independent utilities are found in ``ansible.module_utils.network.common``

* Platform-specific utilities are found in ``ansible.module_utils.network.{{ platform }}``

If your module uses shared module utilities, you must update all references. For example, change:

OLD In Ansible 2.4

.. code-block:: python

   from ansible.module_utils.vyos import get_config, load_config

NEW In Ansible 2.5

.. code-block:: python

   from ansible.module_utils.network.vyos.vyos import get_config, load_config


See the module utilities developer guide see :doc:`dev_guide/developing_module_utilities` for more information.
