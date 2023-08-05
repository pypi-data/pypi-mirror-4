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
from unilint.unilint_plugin import UnilintPlugin
from unilint.common import is_script

__pychecker__ = '--unusednames=cls,options,subdirs'

COMMON_SOURCE = 'common_source'


class CommonSourcePlugin(UnilintPlugin):
    """Identifies files and folders with python code (heuristically)"""

    def __init__(self, shell_function):
        super(CommonSourcePlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return COMMON_SOURCE

    def categorize_type(self, options, path, subdirs, files):
        result = {}
        if files is not None:
            if os.path.basename(path) in ['bin']:
                for filename in files:
                    fullname = os.path.join(path, filename)
                    if is_script(fullname):
                        result[fullname] = ['script']
        else:
            if os.path.basename(os.path.dirname(path)) in ['bin']:
                if is_script(path):
                    result[path] = ['script']

        # TODO use os.path functions
        if '/doc/' in path or \
                '/doc-pak/' in path or \
                path.endswith('/doc') or \
                path.endswith('doc-pak'):
            if path not in result:
                result[path] = ['doc']
            else:
                result[path].append('doc')

        if (path.endswith('/test') or path.endswith('tests')):
            if path not in result:
                result[path] = ['test']
            else:
                result[path].append('test')

        if not files:
            files = [path]

        for filepath in files:
            filename = os.path.basename(filepath)
            def _categorize(path, filepath, category):
                if filepath != path:
                    filepath = os.path.join(path, filepath)
                result[filepath] = [category]
            for prefix in ['.', '#']:
                if filename.startswith(prefix):
                    _categorize(path, filepath, 'hidden')
                    break
            for suffix in ['~', '.orig', '.bak']:
                if filename.endswith(suffix):
                    _categorize(path, filepath, 'backup')
                    break
            for infix in ['.BACKUP.', '.BASE.', '.LOCAL.', '.REMOTE.']:
                if infix in filename:
                    _categorize(path, filepath, 'backup')
                    break
        return result
