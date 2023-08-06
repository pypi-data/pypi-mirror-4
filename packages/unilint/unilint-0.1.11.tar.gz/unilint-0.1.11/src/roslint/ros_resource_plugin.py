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

"plugin to check for flaws in ROS packages"

from __future__ import absolute_import, print_function, unicode_literals
import os
from unilint.common import is_script

from unilint.unilint_plugin import UnilintPlugin

ROS_SOURCE = 'ros_source'

__pychecker__ = '--unusednames=options,subdirs'


class RosResourcePlugin(UnilintPlugin):
    """Identifies files and folders used by ROS conventions (heuristically)"""

    def __init__(self, shell_function):
        super(RosResourcePlugin, self).__init__(shell_function)

    @classmethod
    def get_id(cls):
        return ROS_SOURCE

    def categorize_type(self, options, path, subdirs, files):
        """
        :returns: list of String
        """
        result = {}
        if files is None:
            if os.path.basename(os.path.dirname(path)) in \
                    ['nodes', 'scripts', 'script']:
                if is_script(path):
                    result[path] = ['script']
        else:
            if os.path.basename(path) in ['nodes', 'scripts', 'script']:
                for filename in files:
                    fullname = os.path.join(path, filename)
                    if not filename.endswith('.py') and is_script(fullname):
                        result[fullname] = ['script']
                return result

            if os.path.basename(path) in ['srv', 'msg', 'cfg']:
                is_generated = False
                for filename in files:
                    if filename == '__init__.py':
                        is_generated = True
                if is_generated:
                    result[path] = ['generated']
                    return result
                else:
                    result[path] = [os.path.basename(path)]
            if 'stack.xml' in files:
                result[os.path.join(path)] = ['rosstack']
            if 'manifest.xml' in files:
                result[os.path.join(path)] = ['rospackage']
        return result


#pylint: disable=R0921
class AbstractRosPlugin(UnilintPlugin):
    """Defines a plugin that depends on the categories of RosResourcePlugin"""

    def __init__(self, shell_function):
        super(AbstractRosPlugin, self).__init__(shell_function)

    @classmethod
    def get_depends(cls):
        return ROS_SOURCE

    @classmethod
    def get_id(cls):
        """
        :returns: short lowercase string
        """
        raise NotImplementedError('get_id not implemented by Plugin class')
