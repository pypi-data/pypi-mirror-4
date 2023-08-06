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

'plugin detecting python files'

from __future__ import absolute_import, print_function, unicode_literals
import os
from unilint.unilint_plugin import UnilintPlugin

PY_SOURCE = 'python_source'

__pychecker__ = '--unusednames=cls,options,subdirs'


class PythonSourcePlugin(UnilintPlugin):
    """Identifies files and folders with python code (heuristically)"""

    def __init__(self, shell_function):
        super(PythonSourcePlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return PY_SOURCE

    def categorize_type(self, options, path, subdirs, files):
        result = {}
        if not files:
            files = [path]
        for filepath in files:
            filename = os.path.basename(filepath)
            if filename == '__init__.py':
                result[path] = ['python-package']
            if filename == 'setup.py':
                if filepath != path:
                    filepath = os.path.join(path, filepath)
                result[filepath] = ['script']
            elif filename.endswith('.py'):
                if filepath != path:
                    filepath = os.path.join(path, filepath)
                result[filepath] = ['python-src']
        return result


#pylint: disable=R0921
class AbstractPythonPlugin(UnilintPlugin):
    """Defines a plugin that depends on the categories of PythonSourcePlugin"""
    def __init__(self, shell_function):
        super(AbstractPythonPlugin, self).__init__(shell_function)

    @classmethod
    def get_depends(cls):
        return [PY_SOURCE]

    @classmethod
    def get_id(cls):
        """
        :returns: short lowercase string
        """
        raise NotImplementedError('get_id not implemented by Plugin class')
