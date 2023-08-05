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
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
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

import os
from unilint.python_source_plugin import AbstractPythonPlugin
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.unilint_main import LEVEL_WARNING, LEVEL_STYLE, LEVELS
from unilint.issue import Issue

import re

NEWLINE_MATCHER=re.compile('^.+:[0-9]+: \[')


class PylintPlugin(AbstractPythonPlugin):

    def __init__(self, shell_function):
        super(PylintPlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return 'pylint'

    def get_meta_information(self):
        cmd = "pylint --version"
        value, output, message = self.shell_cmd(cmd,
                                                shell=True,
                                                us_env=True,
                                                ignore_returncodes=[127])
        if value == 0:
            return output
        raise UnilintPluginInitException("ERROR Cannot find pylint, install via apt or pip\n%s" % message)

    def check_resource(self, options, path, type_categories):
        if (not 'python-src' in type_categories and
            not 'script' in type_categories):
            return None

        levels = []

        if options.level > LEVELS[LEVEL_WARNING]:
            levels.append('w')  # warn
        if options.level > LEVELS[LEVEL_STYLE]:
            levels.append('r')  # refactor
            levels.append('c')  # convention

        lvl_cmd = ''
        if levels != []:
            lvl_cmd = "-d%s" % ','.join(levels)

        suppress_options = []
        if 'script' in type_categories:
            suppress_options.append('-d E0611')
        cmd = 'pylint %s --output-format=parseable -i y -r n %s %s' % (path, lvl_cmd, ' '.join(suppress_options))
        if options.verbose:
            print(cmd)
        _, output, _ = self.shell_cmd(cmd,
                                      shell=True,
                                      us_env=True,
                                      cwd=os.path.dirname(path),
                                      ignore_returncodes=range(50))
        output += '\n'
        basepath = os.path.dirname(path)
        if options.raw:
            print output
            return None
        return self.parse(output, basepath)

    def parse(self, output, basepath):
        # Examle output:
        #         dotcode_tf.py:39: [C0111, RosTfTreeDotcodeGenerator] Missing docstring
        #         dotcode_tf.py:47: [C0322, RosTfTreeDotcodeGenerator.__init__] Operator not preceded by a space
        #         self.listen_duration=1
        #                             ^
        issues = []

        lines = []
        # split lines except for multiline messages
        for line in output.splitlines():
            if line.strip() == '':
                continue
            if NEWLINE_MATCHER.match(line) or len(lines) == 0:
                lines.append(line)
            else:
                lines[-1] += "\n%s" % line

        for line in lines:
            issue_lines = line.splitlines()
            message_line = issue_lines[0]
            if len(issue_lines) > 1:
                # source = issue_lines[1]
                position = len(issue_lines[2]) -1
            else:
                # source = None
                position = None

            filename, line_number, rest = message_line.split(':', 2)

            category, message = rest.lstrip('[ ').split(']', 1)
            if ' ' in category:
                category = category.split()[0]

            severity = None
            if category.startswith('E'):
                severity = "error"
            if category.startswith('F'):
                severity = "error"
            if category.startswith('C'):
                severity = "style"
            if category.startswith('R'):
                severity = "warning"
            if category.startswith('W'):
                severity = "warning"

            issue = Issue(path=os.path.join(basepath, filename),
                          message=message.strip(),
                          checker_id=self.get_id(),
                          line_number_start=line_number,
                          line_number_end=line_number,
                          line_position=position,
                          severity=severity,
                          category=category.rstrip(','))
            issues.append(issue)
        return issues
