#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'certified'}


DOCUMENTATION = '''
---
module: ec2_key
version_added: "1.5"
short_description: maintain an ec2 key pair.
description:
    - maintains ec2 key pairs. This module has a dependency on python-boto >= 2.5
options:
  name:
    description:
      - Name of the key pair.
    required: true
  key_material:
    description:
      - Public key material.
    required: false
  force:
    description:
      - Force overwrite of already existing key pair if key has changed.
    required: false
    default: true
    version_added: "2.3"
  state:
    description:
      - create or delete keypair
    required: false
    default: 'present'
    aliases: []
  wait:
    description:
      - Wait for the specified action to complete before returning.
    required: false
    default: false
    aliases: []
    version_added: "1.6"
  wait_timeout:
    description:
      - How long before wait gives up, in seconds
    required: false
    default: 300
    aliases: []
    version_added: "1.6"

extends_documentation_fragment:
 - aws
 - ec2
author: "Vincent Viallet (@zbal)"
'''

EXAMPLES = '''
# Note: None of these examples set aws_access_key, aws_secret_key, or region.
# It is assumed that their matching environment variables are set.

# Creates a new ec2 key pair named `example` if not present, returns generated
# private key
- name: example ec2 key
  ec2_key:
    name: example

# Creates a new ec2 key pair named `example` if not present using provided key
# material.  This could use the 'file' lookup plugin to pull this off disk.
- name: example2 ec2 key
  ec2_key:
    name: example2
    key_material: 'ssh-rsa AAAAxyz...== me@example.com'
    state: present

# Given example2 is already existing, the key will not be replaced because the
# force flag was set to `false`
- name: example2 ec2 key
  ec2_key:
    name: example2
    key_material: 'ssh-rsa AAAAxyz...== me@example.com'
    force: false
    state: present

# Creates a new ec2 key pair named `example` if not present using provided key
# material
- name: example3 ec2 key
  ec2_key:
    name: example3
    key_material: "{{ item }}"
  with_file: /path/to/public_key.id_rsa.pub

# Removes ec2 key pair by name
- name: remove example key
  ec2_key:
    name: example
    state: absent
'''

RETURN = '''
changed:
  description: whether a keypair was created/deleted
  returned: always
  type: bool
  sample: true
key:
  description: details of the keypair (this is set to null when state is absent)
  returned: always
  type: complex
  contains:
    fingerprint:
      description: fingerprint of the key
      returned: when state is present
      type: string
      sample: 'b0:22:49:61:d9:44:9d:0c:7e:ac:8a:32:93:21:6c:e8:fb:59:62:43'
    name:
      description: name of the keypair
      returned: when state is present
      type: string
      sample: my_keypair
    private_key:
      description: private key of a newly created keypair
      returned: when a new keypair is created by AWS (key_material is not provided)
      type: string
      sample: '-----BEGIN RSA PRIVATE KEY-----
        MIIEowIBAAKC...
        -----END RSA PRIVATE KEY-----'
'''

import random
import string
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import HAS_BOTO, ec2_argument_spec, ec2_connect
from ansible.module_utils._text import to_bytes


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True),
        key_material=dict(required=False),
        force=dict(required=False, type='bool', default=True),
        state=dict(default='present', choices=['present', 'absent']),
        wait=dict(type='bool', default=False),
        wait_timeout=dict(default=300),
    )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    name = module.params['name']
    state = module.params.get('state')
    key_material = module.params.get('key_material')
    force = module.params.get('force')
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))

    changed = False

    ec2 = ec2_connect(module)

    # find the key if present
    key = ec2.get_key_pair(name)

    # Ensure requested key is absent
    if state == 'absent':
        if key:
            '''found a match, delete it'''
            if not module.check_mode:
                try:
                    key.delete()
                    if wait:
                        start = time.time()
                        action_complete = False
                        while (time.time() - start) < wait_timeout:
                            if not ec2.get_key_pair(name):
                                action_complete = True
                                break
                            time.sleep(1)
                        if not action_complete:
                            module.fail_json(msg="timed out while waiting for the key to be removed")
                except Exception as e:
                    module.fail_json(msg="Unable to delete key pair '%s' - %s" % (key, e))
            key = None
            changed = True

    # Ensure requested key is present
    elif state == 'present':
        if key:
            # existing key found
            if key_material and force:
                # EC2's fingerprints are non-trivial to generate, so push this key
                # to a temporary name and make ec2 calculate the fingerprint for us.
                #
                # http://blog.jbrowne.com/?p=23
                # https://forums.aws.amazon.com/thread.jspa?messageID=352828

                # find an unused name
                test = 'empty'
                while test:
                    randomchars = [random.choice(string.ascii_letters + string.digits) for x in range(0, 10)]
                    tmpkeyname = "ansible-" + ''.join(randomchars)
                    test = ec2.get_key_pair(tmpkeyname)

                # create tmp key
                tmpkey = ec2.import_key_pair(tmpkeyname, to_bytes(key_material))
                # get tmp key fingerprint
                tmpfingerprint = tmpkey.fingerprint
                # delete tmp key
                tmpkey.delete()

                if key.fingerprint != tmpfingerprint:
                    if not module.check_mode:
                        key.delete()
                        key = ec2.import_key_pair(name, to_bytes(key_material))

                        if wait:
                            start = time.time()
                            action_complete = False
                            while (time.time() - start) < wait_timeout:
                                if ec2.get_key_pair(name):
                                    action_complete = True
                                    break
                                time.sleep(1)
                            if not action_complete:
                                module.fail_json(msg="timed out while waiting for the key to be re-created")

                    changed = True

        # if the key doesn't exist, create it now
        else:
            '''no match found, create it'''
            if not module.check_mode:
                if key_material:
                    '''We are providing the key, need to import'''
                    key = ec2.import_key_pair(name, to_bytes(key_material))
                else:
                    '''
                    No material provided, let AWS handle the key creation and
                    retrieve the private key
                    '''
                    key = ec2.create_key_pair(name)

                if wait:
                    start = time.time()
                    action_complete = False
                    while (time.time() - start) < wait_timeout:
                        if ec2.get_key_pair(name):
                            action_complete = True
                            break
                        time.sleep(1)
                    if not action_complete:
                        module.fail_json(msg="timed out while waiting for the key to be created")

            changed = True

    if key:
        data = {
            'name': key.name,
            'fingerprint': key.fingerprint
        }
        if key.material:
            data.update({'private_key': key.material})

        module.exit_json(changed=changed, key=data)
    else:
        module.exit_json(changed=changed, key=None)


if __name__ == '__main__':
    main()
