#!/usr/bin/env python
# Copyright 2016 IBM Corp.
#
# All Rights Reserved.
#
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

import jinja2
import os.path
import unittest


TEMPLATE_FILE = os.path.sep.join(['playbooks', 'templates',
                                  'persistent-net-rules.j2'])


class TestPersistentNetTemplate(unittest.TestCase):

    def test_template(self):
        tmpl_vars = {'name_interfaces': {'eth0': 'eth0mac',
                                         'eth10': 'eth10mac',
                                         'eth11': 'eth11mac'}}

        template_path, template_file = os.path.split(TEMPLATE_FILE)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                                 trim_blocks=True)
        template = env.get_template(template_file)
        rendered_file = template.render(tmpl_vars)

        # For debugging convenience, we do a line by line compare if the
        # output does not match the expected
        if expected_output_1 != rendered_file:
            expected_lines = expected_output_1.splitlines()
            rendered_lines = rendered_file.splitlines()
            for x in range(len(expected_lines)):
                if expected_lines[x] != rendered_lines[x]:
                    print 'Rendered_file'
                    print rendered_file
                    self.assertEqual(expected_lines[x], rendered_lines[x])
            # Line differences should fail above but if the difference is
            # a different number of lines then fail here:
            if len(expected_lines) != len(rendered_lines):
                print 'Rendered_file'
                print rendered_file
                self.fail('Expected vs rendered line count is different. '
                          'Expected: %s Rendered: %s' % (len(expected_lines),
                                                         len(rendered_lines)))


expected_output_1 = """\
# Rule "eth11"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="eth11mac",\
 ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth11"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="eth11mac", \
ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="p*", NAME="eth11"

# Rule "eth10"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="eth10mac", \
ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth10"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="eth10mac", \
ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="p*", NAME="eth10"

# Rule "eth0"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="eth0mac", \
ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth0"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="eth0mac", \
ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="p*", NAME="eth0"

"""

if __name__ == "__main__":
    unittest.main()
