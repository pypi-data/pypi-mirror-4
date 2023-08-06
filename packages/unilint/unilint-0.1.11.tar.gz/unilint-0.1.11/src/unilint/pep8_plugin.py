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

'pep8 plugin'

from __future__ import absolute_import, print_function, unicode_literals
from unilint.python_source_plugin import AbstractPythonPlugin
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.unilint_main import LEVEL_WARNING, LEVEL_STYLE, LEVELS
from unilint.issue import Issue


class Pep8Plugin(AbstractPythonPlugin):
    'pep8 plugin'

    def __init__(self, shell_function):
        super(Pep8Plugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return 'pep8'

    def get_meta_information(self):
        cmd = "pep8 --version"
        value, output, message = self.shell_cmd(cmd,
                                                shell=True,
                                                us_env=True,
                                                ignore_returncodes=[127])
        if value == 0:
            return "pep8: %s" % output
        raise UnilintPluginInitException(
            "ERROR Cannot find pep8, install via apt or pip\n%s" % message)

    def check_resource(self, options, path, type_categories):
        'runs the tool and processes the output'
        if not 'python-src' in type_categories and \
                not 'script' in type_categories and \
                not 'python-module' in type_categories:
            return None

        levels = []

        # pep8 does 'only' concern documentation and style, so we will
        # not use it for level error

        if options.level >= LEVELS[LEVEL_WARNING]:
            if options.verbose:
                print('pep8 not used at this checking level')
            return None

        if options.level < LEVELS[LEVEL_WARNING]:
            levels.append('E')
        if options.level < LEVELS[LEVEL_STYLE]:
            levels.append('W')

        cmd = "pep8 %s -r --select=%s" % (path, ','.join(levels))

        if options.verbose:
            print(cmd)

        _, output, _ = self.shell_cmd(cmd,
                                      shell=True,
                                      us_env=True)
        if options.raw:
            print(output)
            return None
        else:
            return (self.parse(output), None)

    def parse(self, output):
        'creates an issue from an output line'
        # Example output:
        # /tmp/foo.py:4:1: E302 expected 2 blank lines, found 1
        issues = []
        for line in output.splitlines():
            if line.strip() == '':
                continue
            tokens = line.split(':', 3)
            (category, message) = tokens[3].strip().split(' ', 1)
            severity = None
            if category.startswith('E'):
                severity = "warning"
            if category.startswith('W'):
                severity = "style"

            issue = Issue(path=tokens[0],
                          message=message,
                          checker_id=self.get_id(),
                          line_number_start=tokens[1],
                          line_number_end=tokens[1],
                          line_position=tokens[2],
                          severity=severity,
                          category=category)
            issues.append(issue)
        return issues
