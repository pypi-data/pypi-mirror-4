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

'pylint plugin'

from __future__ import absolute_import, print_function, unicode_literals
import os
import re
import logging

from unilint.python_source_plugin import AbstractPythonPlugin
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.unilint_main import LEVEL_WARNING, LEVEL_STYLE, LEVELS, LEVEL_ALL
from unilint.issue import Issue


NEWLINE_MATCHER = re.compile('^.+:[0-9]+: \[')
INDICATOR_MATCHER = re.compile('^\s*\^+\s*\^*$')


class PylintPlugin(AbstractPythonPlugin):
    'pylint plugin'

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
        raise UnilintPluginInitException(
            "ERROR Cannot find pylint, install via apt or pip\n%s" % message)

    def check_resource(self, options, path, type_categories):
        'runs the tool and processes the output'
        if not 'python-src' in type_categories and \
                not 'script' in type_categories and \
                not 'python-package' in type_categories:
            return None

        levels = []

        suppress_options = []
        if options.level > LEVELS[LEVEL_WARNING]:
            levels.append('w')  # warn
        if options.level > LEVELS[LEVEL_STYLE]:
            levels.append('r')  # refactor
            levels.append('c')  # convention

        lvl_cmd = ''
        if levels != []:
            lvl_cmd = "-d%s" % ','.join(levels)

        if 'script' in type_categories:
            suppress_options.append('E0611')
        if options.level > LEVELS[LEVEL_ALL]:
            # 'Locally disabling ...'
            suppress_options.extend(['I0011', 'R0801'])

        suppress_options_string = ''
        if suppress_options:
            suppress_options_string = '-d %s' % ','.join(suppress_options)

        if options.pythonpath:
            pythonpath = 'PYTHONPATH=%s:$PYTHONPATH;' % options.pythonpath
        else:
            pythonpath = ''

        cmd = ('%spylint %s --output-format=parseable -i y -r n %s %s' %
               (pythonpath,
                os.path.abspath(path),
                lvl_cmd,
                suppress_options_string))
        log = logging.getLogger(__name__)
        log.debug(cmd)

        _, output, _ = self.shell_cmd(
            cmd,
            shell=True,
            us_env=True,
            ignore_returncodes=range(50))
        output += '\n'
        if options.raw:
            print(output)
            return []
        result = self.parse(output)
        log.debug('%s issues found' % len(result))
        ignores = None
        if 'python-package' in type_categories:
            ignores = ['^%s.*py$' % path]
        return (result, ignores)

    def parse(self, output):
        'creates an issue from an output line'
        # Example output:
        # foo/bar/dotcode_tf.py:39: [C0111, comp1] Missing docstring
        # foo/bar/dotcode_tf.py:47: [C0322, com1.__init__] Operator empty
        # self.listen_duration=1
        #                     ^
        # test/integration/pep8_test.py:1: [R0801] Similar lines in 22 files
        # ==integration.all_plugins_test:16
        # ==integration.all_plugins_test:25
        # ==integration.all_plugins_test:34
        issues = []

        lines = []
        # split lines except for multiline messages
        for line in output.splitlines():
            if line.strip() == '':
                continue
            if NEWLINE_MATCHER.match(line) or len(lines) == 0:
                lines.append([line, None])
            else:
                lines[-1][0] += "\n%s" % line
                if INDICATOR_MATCHER.match(line):
                    lines[-1][1] = 'indicator'

        for (line, flag) in lines:
            issue_lines = line.splitlines()
            multiline_message = False
            position = None
            if len(issue_lines) == 1:
                message_line = issue_lines[0]
            elif len(issue_lines) == 3 and flag == 'indicator':
                message_line = issue_lines[0]
                position = len(issue_lines[2]) - 1
            else:
                # multifile error
                message_line = issue_lines[0]
                multiline_message = True
            filename, line_number, rest = message_line.split(':', 2)

            category, message = rest.lstrip('[ ').split(']', 1)
            if multiline_message:
                message += ('\n%s' % '\n'.join(issue_lines[1:]))
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

            issue = Issue(path=filename,
                          message=message.strip(),
                          checker_id=self.get_id(),
                          line_number_start=line_number,
                          line_number_end=line_number,
                          line_position=position,
                          severity=severity,
                          category=category.rstrip(','))
            issues.append(issue)
        return issues
