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

'Base functions for all plugins'

from __future__ import absolute_import, print_function, unicode_literals


class UnilintPluginInitException(Exception):
    '''raised by Exceptions in plugins'''
    pass


# pylint: disable-msg=W0613
__pychecker__ = '--unusednames=cls,options,subdirs,issue_list'


#pylint: disable=R0921
class UnilintPlugin(object):
    '''
    Base class for all plugins defines all methods that will get
    invoked by unilint.

    A plugin may just categorize a file or folder, or it may check a
    file or folder.  Categorization is done as an extra step so that
    many plugins can share the categorization effort instead of
    duplicating it. Category IDs are up to the plugins.
    '''

    def __init__(self, shell_function):
        """
        The constructor takes the shell function so that unit tests
        can inject a mock function

        :param shell_function: a function like common.run_shell_command
        :raises UnilintPluginInitException: to signal the plugin cannot execute
        """
        self.shell_cmd = shell_function

    @classmethod
    def get_id(cls):
        """
        :returns: short lowercase string
        """
        raise NotImplementedError('get_id not implemented by Plugin class')

    def get_meta_information(self):
        """
        is supposed to return with information about the system
        relevant to this plugin, if any.

        :returns: an empty or a newline terminated string
        """
        return ''

    @classmethod
    def is_enabled_by_default(cls):
        """
        :returns: bool
        """
        return True

    @classmethod
    def get_depends(cls):
        """
        return of plugins on which this plugin depends (e.g. for
        categories)

        :returns: None or list of string ids
        """
        return None

    def categorize_type(self, options, path, subdirs, files):
        """
        returns a dict that can contain categories for path and any of
        files.
        Dict key must be full path (os.path.join(path, filename)).
        Subdirs can be used for heuristics, but should not be
        classified, they will be traversed later.
        Returns map with resourcename (file or folder), mapped to list
        of category string ids

        :param path: the folder to analyze
        :param subdirs: names of direct subdirs
        :param files: names of files in path
        :returns: dict of str->[str]
        """
        return None

    def check_resource(self, options, path, type_categories):
        """
        :param options: command line options to unilint
        :param path: resource to check, can be file or folder
        :param type_categories: what kind of resource the path
        :param recursed: Whether the parent folder has already been checked
        :returns: (list, list) of unilint.Issue and ignores, or None.
        """
        return None
