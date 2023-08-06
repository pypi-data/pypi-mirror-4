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

"""module unilint"""

import logging

from unilint.unilint_main import register_plugin

from unilint.common_source_plugin import CommonSourcePlugin
from unilint.python_source_plugin import PythonSourcePlugin
from unilint.cpp_source_plugin import CppSourcePlugin

from unilint.pep8_plugin import Pep8Plugin
from unilint.pyflakes_plugin import PyflakesPlugin
from unilint.pylint_plugin import PylintPlugin
from unilint.pychecker_plugin import PycheckerPlugin

from unilint.cppcheck_plugin import CppcheckPlugin
from unilint.cpplint_plugin import CpplintPlugin

from unilint.standard_formatters import register_standard_formatters


register_standard_formatters()

register_plugin(CommonSourcePlugin)
register_plugin(PythonSourcePlugin)
register_plugin(CppSourcePlugin)

register_plugin(Pep8Plugin)
register_plugin(PyflakesPlugin)
register_plugin(PycheckerPlugin)
register_plugin(PylintPlugin)
register_plugin(CppcheckPlugin)
register_plugin(CpplintPlugin)
