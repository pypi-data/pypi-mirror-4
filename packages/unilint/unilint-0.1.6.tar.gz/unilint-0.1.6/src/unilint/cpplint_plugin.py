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

import os
import re
from unilint.cpp_source_plugin import AbstractCppPlugin, CPP_EXTENSIONS
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.unilint_main import LEVEL_ALL, LEVEL_WARNING, \
    LEVEL_STYLE, LEVEL_ERROR, LEVEL_STYLE, LEVELS
from unilint.issue import Issue

class CpplintPlugin(AbstractCppPlugin):

    def __init__(self, shell_function):
        super(CpplintPlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return 'cpplint'

    def get_meta_information(self):
        cmd = "cpplint"
        value, output, message = self.shell_cmd(cmd,
                                                shell=True,
                                                us_env=True,
                                                ignore_returncodes=[1])
        if value == 0 or value == 1:
            return 'cpplint'
        raise UnilintPluginInitException("ERROR Cannot find cpplint, install via pypi\n%s" % message)

    def check_resource(self, options, path, type_categories):
        if not 'cpp-file' in type_categories:
            return None

        level = 0
        if options.level <= LEVELS[LEVEL_STYLE]:
            level = 2
        elif options.level <= LEVELS[LEVEL_WARNING]:
            level = 4
        elif options.level <= LEVELS[LEVEL_ERROR]:
            level = 5
        
        if 'cpp-file' in type_categories:
            cmd = "cpplint --verbose=%s %s" % (level, path)

        if options.verbose:
            print(cmd)

        _, output, _ = self.shell_cmd(cmd,
                                      shell=True,
                                      us_env=True,
                                      cwd=os.path.dirname(path),
                                      capture_std_err=True,
                                      ignore_returncodes=[1])

        if options.raw:
            print output
            return None
        else:
            return self.parse(output)

    def parse(self, output):
        """
        Example:
        costmap_model.cpp:136:  Missing space before ( in if(  [whitespace/parens] [5]
Done processing navigation/base_local_planner/src/costmap_model.cpp
Total errors found: 21
        """
        issues = []
        for line in output.splitlines():
            ignore = False
            if line.strip() == '':
                continue
            for prefix in ['Ignoring ', 'Done processing ', 'Total errors']:
                if line.startswith(prefix):
                    ignore = True
                    break
            if ignore:
                continue
            try:
                (filename, line_number, message) = line.split(':', 2)
            except:
                print(line)
                raise
            issue = Issue(path=filename,
                          message=message.strip(),
                          checker_id=self.get_id(),
                          line_number_start=line_number,
                          line_number_end=line_number,
                          # severity=severity,
                          # category=category
                          )
            issues.append(issue)
        return issues
