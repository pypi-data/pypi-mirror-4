# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Thibault Kruse
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'pychecker plugin'

from __future__ import absolute_import, print_function, unicode_literals
import os
from unilint.python_source_plugin import AbstractPythonPlugin
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.issue import Issue
from unilint.unilint_main import LEVEL_ERROR, LEVELS


class PycheckerPlugin(AbstractPythonPlugin):
    'pychecker plugin'

    def __init__(self, shell_function):
        super(PycheckerPlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return 'pychecker'

    @classmethod
    def is_enabled_by_default(cls):
        # pychecker is evil, because it compiles code, which means
        # malicious code maybe executed.
        return False

    def get_meta_information(self):
        cmd = "pychecker --version"
        value, output, message = self.shell_cmd(cmd,
                                                shell=True,
                                                us_env=True,
                                                ignore_returncodes=[127])
        if value == 0:
            return "pychecker: %s" % output
        raise UnilintPluginInitException(
            "ERROR Can't find pychecker, install via apt or pip\n%s" % message)

    def check_resource(self, options, path, type_categories):
        'runs the tool and processes the output'
        if not 'python-src' in type_categories and \
                not 'python-module' in type_categories:
            return None

        suppress_cmds = []
        if options.level >= LEVELS[LEVEL_ERROR]:
            suppress_cmds.append('--no-argsused')
            suppress_cmds.append('--no-import')

        cmd = 'pychecker --only -#100 %s %s' % (' '.join(suppress_cmds), path)
        if options.verbose:
            print(cmd)

        _, output, _ = self.shell_cmd(cmd,
                                      shell=True,
                                      us_env=True,
                                      ignore_returncodes=[1, 2, 123])

        if options.raw:
            print(path)
            print(output)
            return None
        else:
            return (self.parse(output), None)

    def parse(self, output):
        'creates an issue from an output line'
        issues = []
        # Example output
        # /tmp/unilint/plugin.py:13: Local variable (pythonfound) not used
        # /tmp/unilint/pychecker_plugin.py:47: No global (Issue) found

        for line in output.splitlines():
            ignore = False
            if line.strip() == '':
                continue
            # File or pathname element
            for prefix in ['Warnings...', 'None']:
                if line.startswith(prefix):
                    ignore = True
                    break
            if ignore:
                continue

            if line.count(':') > 1:
                path, line_number, message = line.split(':', 2)
            else:
                path = ''
                message = line
            # pychecker seems to print weird double lines with
            # incomplete path when run through subprocess.Popen
            if not os.path.exists(path):
                continue
            message = message.strip()
            severity = "warning"

            issue = Issue(path=path,
                          message=message,
                          checker_id=self.get_id(),
                          line_number_start=line_number,
                          line_number_end=line_number,
                          severity=severity)
            issues.append(issue)
        return issues
