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
from unilint.issue import Issue


class PyflakesPlugin(AbstractPythonPlugin):

    def __init__(self, shell_function):
        super(PyflakesPlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return 'pyflakes'

    def get_meta_information(self):
        try:
            import pyflakes
        except ImportError as e:
            raise UnilintPluginInitException("ERROR Cannot find pyflakes, install via apt or pip\n%s" % e)
        return "pyflakes: %s" % pyflakes.__version__

    @classmethod
    def is_enabled_by_default(cls):
        # pyflakes returns a subset of pylint, is only useful for quicker checks
        return False

    def check_resource(self, options, path, type_categories):
        if (not 'python-src' in type_categories and
            not 'script' in type_categories):
            return None

        cmd = "pyflakes %s"%path
        if options.verbose:
            print(cmd)
        _, output, _ = self.shell_cmd(cmd,
                                      shell=True,
                                      us_env=True)
        if options.raw:
            print output
            return None
        else:
            return self.parse(output)

    def parse(self, output):
        issues = []
        for line in output.splitlines():
            if line.strip() == '':
                continue
            tokens = line.split(':', 2)
            message = tokens[2].strip()
            severity = "warning"

            issue = Issue(path=tokens[0],
                          message=message,
                          checker_id=self.get_id(),
                          line_number_start=tokens[1],
                          line_number_end=tokens[1],
                          severity=severity)
            issues.append(issue)
        return issues
