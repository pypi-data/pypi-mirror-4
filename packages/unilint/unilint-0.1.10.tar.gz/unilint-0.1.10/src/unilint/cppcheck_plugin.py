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

'plugin for cppcheck'

from __future__ import absolute_import, print_function, unicode_literals
import re
from unilint.cpp_source_plugin import AbstractCppPlugin
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.unilint_main import LEVEL_WARNING, LEVEL_STYLE, LEVELS
from unilint.issue import Issue

PROGRESS_PATTERN = re.compile('^[0-9]+/[0-9]')

__pychecker__ = '--unusednames=cls,options,subdirs'
_IGNORED_PREFIXES = [
    'Cppcheck - ',
    "Checking ",
    "::missingInclude:Cppcheck cannot find all the include file"]


class CppcheckPlugin(AbstractCppPlugin):
    'plugin for cppcheck'

    def __init__(self, shell_function):
        super(CppcheckPlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return 'cppcheck'

    def get_meta_information(self):
        cmd = "cppcheck --version"
        value, output, message = self.shell_cmd(cmd,
                                                shell=True,
                                                us_env=True,
                                                ignore_returncodes=[127])
        if value == 0:
            return output
        raise UnilintPluginInitException(
            "ERROR Cannot find cppcheck, install via apt or pip\n%s" % message)

    def check_resource(self, options, path, type_categories):
        'runs the tool and processes the output'
        if not 'cpp-file' in type_categories:
            return None

        levels = []

        if options.level < LEVELS[LEVEL_WARNING]:
            levels.append('information')
            levels.append('missingInclude')
            levels.append('unusedFunction')

        if options.level == LEVELS[LEVEL_STYLE]:
            levels = ['all']

        lvl_cmd = ''
        if levels != []:
            lvl_cmd = "--enable=%s" % ','.join(levels)

        template = '{file}:{line}:{id}:{message}'

        if 'cpp-file' in type_categories:
            cmd = "cppcheck --template %s %s %s" % (template, lvl_cmd, path)

        if options.verbose:
            print(cmd)

        _, output, _ = self.shell_cmd(cmd,
                                      shell=True,
                                      us_env=True,
                                      capture_std_err=True)

        if options.raw:
            print(output)
            return None
        else:
            return (self.parse(output), None)

    def parse(self, output):
        'creates an issue from an output line'
        issues = []
        for line in output.splitlines():
            ignore = False
            if line.strip() == '':
                continue
            for prefix in _IGNORED_PREFIXES:
                if line.startswith(prefix):
                    ignore = True
                    break
            if ignore:
                continue

            if PROGRESS_PATTERN.match(line):
                continue
            (filename, line_number, category, message) = line.split(':', 3)
            # severity=None
            # if category.startswith('E'):
            #     severity = "warning"
            # if category.startswith('W'):
            #     severity = "style"

            issue = Issue(path=filename,
                          message=message.strip(),
                          checker_id=self.get_id(),
                          line_number_start=line_number,
                          line_number_end=line_number,
                          # severity=severity,
                          category=category)
            issues.append(issue)
        return issues
