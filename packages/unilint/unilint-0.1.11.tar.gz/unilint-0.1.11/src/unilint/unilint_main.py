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

"contains main function and helpers"

from __future__ import absolute_import, print_function, unicode_literals
import os
import sys
import logging
import re
from argparse import ArgumentParser

from unilint.__version__ import VERSION
from unilint.common import UnilintException
from unilint.common_source_plugin import COMMON_SOURCE
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.custom_format import FLAGS, print_formatted

from unilint.common import run_shell_command

PLUGINS = {}
FORMATTERS = {}

LEVEL_ALL = "all"
LEVEL_STYLE = "style"
LEVEL_WARNING = "warning"
LEVEL_ERROR = "error"

LEVELS = {LEVEL_ALL: 0, LEVEL_STYLE: 10, LEVEL_WARNING: 20, LEVEL_ERROR: 30}


def register_formatter(f_id, formatter_function):
    """
    Add a formatter with an id so that users may select it
    """
    FORMATTERS[f_id] = formatter_function


def register_plugin(plugin):
    """
    Add a static code analyzer plugin
    """
    pid = plugin.get_id()
    if pid is None or pid == '':
        raise UnilintException('Invalid plugin id %s' % (pid))
    PLUGINS[pid] = plugin


def extend_maybe(some_container, other_container):
    """
    extends list or dict with list values with other list or dict
    unless other is None
    """
    if other_container is not None:
        if type(some_container) == dict:
            for key, val in other_container.items():
                if key in some_container:
                    some_container[key].extend(val)
                else:
                    some_container[key] = val
        else:
            some_container.extend(other_container)


def resolve_plugins(selected_plugins_string,
                    deselected_plugins_string,
                    quiet=False):
    """
    Takes in a comma separated String or none, returns a dict
    str->plugin_instance
    """
    result_plugin_ids = []
    if selected_plugins_string is not None and selected_plugins_string != '':
        selected_plugins_ids = selected_plugins_string.split(',')

        for plugin_id in selected_plugins_ids:
            if plugin_id.strip() == '':
                continue
            if not plugin_id in PLUGINS:
                raise UnilintException('Unknown plugin: %s' % plugin_id)
            result_plugin_ids.append(plugin_id)
    else:
        deselected_plugins_ids = []
        if deselected_plugins_string is not None:
            deselected_plugins_ids = deselected_plugins_string.split(',')

        for plugin_id in PLUGINS:
            if plugin_id not in deselected_plugins_ids and \
                    PLUGINS[plugin_id].is_enabled_by_default():
                result_plugin_ids.append(plugin_id)

    dependencies = []
    for plugin_id in result_plugin_ids:
        deps = PLUGINS[plugin_id].get_depends()
        if deps is not None:
            for dep in deps:
                if not dep in PLUGINS:
                    raise UnilintException(
                        'Unknown plugin dependency: %s of %s' %
                        (dep, plugin_id))
                if not dep in result_plugin_ids and not dep in dependencies:
                    dependencies.append(dep)
    for dep_id in dependencies:
        result_plugin_ids.append(dep_id)

    selected_plugins = {}
    for plugin_id in result_plugin_ids:
        try:
            selected_plugins[plugin_id] = PLUGINS[plugin_id](run_shell_command)
        except UnilintPluginInitException as upie:
            if not quiet:
                print("plugin %s failed to activate: %s" %
                      (plugin_id, str(upie)))
    return selected_plugins


def index_different(id1, id2):
    '''quick check returning true only if both values as ints positive
    and different'''
    if not id1 or not id2:
        return False
    if int(id1) < 0 or int(id2) < 0:
        return False
    if int(id1) != int(id2):
        return True
    return False


def select_best_dupe(issue1, issue2):
    '''Given two issues identified as duplicate, return the one with
    higher severity, and then the one having more location
    information'''
    if issue2.severity < issue1.severity:
        return issue2
    elif (issue2.severity == issue1.severity and
          (not issue1.line_position or int(issue1.line_position) < 0) and
          (issue2.line_position and int(issue2.line_position) >= 0)):
        return issue2
    return issue1


def remove_duplicates(issues):
    """
    looks for lines in list of issues having the same line number and
    indicating the same problem

    :param issues: list of Issue
    """
    if not issues:
        return issues
    issues_ord = order_issues(issues)
    result = []
    sameline_issues = []
    lastline = -1

    for issue in issues_ord:
        is_likely_duplicate = True
        if not sameline_issues:
            is_likely_duplicate = False
        elif (index_different(issue.line_number_start, lastline)):
            sameline_issues = []
            lastline = int(issue.line_number_start or -1)
            is_likely_duplicate = False
        if issue.line_number_start and int(issue.line_number_start) >= 0:
            lastline = int(issue.line_number_start)

        if is_likely_duplicate:
            # check whether new issue is a duplicate
            is_duplicate = False
            for oldissue in sameline_issues:
                if index_different(issue.line_position,
                                   oldissue.line_position):
                    continue
                # for now, will rely on manually crafted duplicate
                # detection for similar error in different code analysers
                for keyword_vec in [('too long', ),
                                    ('indentation contains', ),
                                    ('variable ', ),
                                    ('not used', 'unused', 'Unused'),
                                    ('one statement', 'multiple statements')]:
                    for keyword_match_old in keyword_vec:
                        if keyword_match_old in oldissue.message:
                            for keyword_match in keyword_vec:
                                if keyword_match in issue.message:
                                    is_duplicate = True
                                    break
                    if is_duplicate:
                        break
            if is_duplicate:
                result[-1] = select_best_dupe(result[-1], issue)
                continue
        sameline_issues.append(issue)
        result.append(issue)
    return result


def print_issues(args, issues, path):
    """
    print to stdout

    :param args: all CLI arguments
    :param issues: list of Issue to print
    :param path: basepath to which to append issue relative path
    """
    if args.formatter is not None:
        FORMATTERS[args.formatter](args, issues, path)
    elif args.format is not None:
        print_formatted(args.format, issues, path)


def order_issues(issues):
    """
    sorts Issues by line number and line position

    :param issues: list of Issue
    """
    def keyfun(iss):
        '''helper to sort issues'''
        lin = str(iss.line_number_start).rjust(5, str('0'))
        pon = str(iss.line_position).rjust(3, str('0'))
        return "%s%sz%s" % (os.path.abspath(iss.path), lin, pon)

    if not issues:
        return issues
    return sorted(issues, key=keyfun)


class IgnorableFolderException(Exception):
    '''Helper to break out of multiple loops'''
    pass


def check_path(path_to_check,
               basepath,
               args,
               subdirs=None,
               files=None,
               force=False):
    """
    runs all selected plugins on the given files in order,
    optionally printing issue messages as soon as available

    :param path_to_check: path to file/folder in which to run checks on files
    :param basepath: absolute path that user gave in cli
    :param args: all CLI argument
    :param subdirs: subdirectories
    :param files: the files to check
    :param force: if True, also scans tests, docs and generated folders
    """
    categorized_resources = {}
    for plugin in args.selected_plugins.values():
        new_categories = \
            plugin.categorize_type(args,
                                   path_to_check,
                                   subdirs,
                                   files) or {}

        for resource, categories in new_categories.items():
            # ignore folder ?
            if path_to_check == resource and not force:
                if 'generated' in categories:
                    if not args.check_generated:
                        raise IgnorableFolderException()
                if 'test' in categories:
                    if not args.check_tests:
                        raise IgnorableFolderException()
                if 'doc' in categories:
                    if not args.check_docs:
                        raise IgnorableFolderException()
        extend_maybe(categorized_resources, new_categories)
    issues = []
    plugin_ignores = {pid: [] for pid in args.selected_plugins.values()}
    for resource, categories in sorted(categorized_resources.items()):
        resource_issues = []
        if 'hidden' in categories:
            continue
        if 'broken' in categories:
            continue
        if 'backup' in categories:
            continue
        log = logging.getLogger(__name__)
        log.debug("processing: %s as %s" % (resource, categories))
        for plugin in args.selected_plugins.values():
            ignore_plugin = False
            for ignore_pattern in plugin_ignores[plugin]:
                if re.match(ignore_pattern, resource):
                    ignore_plugin = True
                    break
            if ignore_plugin:
                continue
            try:
                result = plugin.check_resource(args,
                                               resource,
                                               categories)
                if result:
                    (new_issues, ignores) = result
                    extend_maybe(resource_issues, new_issues)
                    if ignores:
                        plugin_ignores[plugin].extend(ignores)
                    if not args.ordered and not args.raw:
                        # get the output to the user as quickly as possible
                        print_issues(args, new_issues, basepath)
            except KeyboardInterrupt as kbi:
                raise UnilintException(
                    'Interrupted while running %s on %s: %s' %
                    (plugin.get_id(), resource, kbi))
        if resource_issues:
            resource_issues = remove_duplicates(resource_issues)
            extend_maybe(issues, resource_issues)
            if args.ordered and not args.raw:
                # print here unless we already printed
                resource_issues = resource_issues
                print_issues(args, resource_issues, basepath)
    return issues


def get_pythonpath(path):
    '''applies heuristics like nose to conveniently set the PYTHONPATH'''
    if not os.path.exists(os.path.dirname(path)):
        return ''
    if not os.path.isdir(path) or \
            os.path.isfile(os.path.join(path, '__init__.py')):
        if not os.path.dirname(path) == path:
            return get_pythonpath(os.path.dirname(path))
        else:
            return ''
    else:
        paths = [path]
        additional = [os.path.join(path, p) for p in['src', 'lib', 'test']]
        parent = os.path.dirname(path)
        additional = [os.path.join(parent, p) for p in['src', 'lib', 'test']]
        paths += [p for p in additional if os.path.isdir(p)]
        return ':'.join(paths)


def run_cmd(paths, args):
    '''main function'''
    if args.show_plugins is True:
        print('\n'.join(PLUGINS.keys()))
        return 0

    # if common is not selected, select it. can still be deselected.
    if args.selected_plugins is not None:
        if not COMMON_SOURCE in args.selected_plugins:
            args.selected_plugins += ',%s' % COMMON_SOURCE

    if args.version:
        args.selected_plugins = resolve_plugins(args.selected_plugins,
                                                args.deselected_plugins,
                                                quiet=True)

        print(("unilint %s" % (VERSION)).encode('UTF-8'))
        for _, plugin in args.selected_plugins.items():
            meta = plugin.get_meta_information()
            if meta is not None and meta != '':
                print(meta.encode('UTF-8'))
        return 0

    args.selected_plugins = resolve_plugins(args.selected_plugins,
                                            args.deselected_plugins)

    issues = []
    for path in paths:
        if not os.path.exists(path):
            print('Ignoring argument that does not exist: %s' % path)
            continue
        # PYTHONPATH for path
        args.pythonpath = get_pythonpath(os.path.abspath(path))

        if args.debug:
            print('linting from %s' % path)
            print('Activated plugins %s' % args.selected_plugins.keys())

        if len(PLUGINS) == 0:
            raise UnilintException('No plugins registered with unilint')

        if path is None:
            if len(args) == 0:
                raise UnilintException('Unable to use cwd as path')
            else:
                raise UnilintException('Unable to run on path %s' % args[0])

        abs_path = os.path.abspath(path)
        if os.path.isdir(abs_path):
            for (parentdir, subdirs, files) in os.walk(abs_path):
                ignoreddirs = []
                for dirname in subdirs:
                    if (dirname in ['build', '.svn', 'CVS', '.hg', '.git']
                            or 'egg-info' in dirname):

                        ignoreddirs.append(dirname)
                for dirname in ignoreddirs:
                    subdirs.remove(dirname)
                if len(files) == 0 and len(subdirs) == 0:
                    continue
                try:
                    new_issues = check_path(path_to_check=parentdir,
                                            basepath=abs_path,
                                            args=args,
                                            subdirs=subdirs,
                                            files=files,
                                            force=os.path.samefile(parentdir,
                                                                   path))
                    extend_maybe(issues, new_issues)
                except IgnorableFolderException:
                    # beware concurrent modification, requires [:]
                    ignoreddirs = subdirs[:]
                    for dirname in ignoreddirs:
                        subdirs.remove(dirname)
        else:
            # is file
            new_issues = issues.extend(check_path(path,
                                                  os.path.dirname(path),
                                                  args=args,
                                                  force=True) or [])
            extend_maybe(issues, new_issues)
        sys.stdout.flush()

        # write to std_err so that report on std_out remains unchanged
        sys.stderr.write("%s issues found\n" % len(issues or []))
    return 0


def get_unilint_parser(description=None):
    '''Adds all options and arguments'''
    parser = ArgumentParser(description=description)
    parser.add_argument(
        'path', nargs='*',
        help='a folder or filename to check')
    parser.add_argument(
        "-v", "--verbose", dest="verbose", default=False,
        help="verbose output.",
        action="store_true")
    parser.add_argument(
        "--version", dest="version", default=False,
        help="print version and meta information",
        action="store_true")
    parser.add_argument(
        "--debug", dest="debug", default=False,
        help="debug output.",
        action="store_true")
    parser.add_argument(
        "-l", "--level", dest="level", default=LEVEL_ERROR,
        help="A number or one of %s." %
        (','.join(["%s(=%s)" % (k, v) for k, v in LEVELS.items()])),
        action="store")
    parser.add_argument(
        "-p", "--plugins", dest="show_plugins", default=False,
        help="List Available plugins",
        action="store_true")
    parser.add_argument(
        "-s", "--select-plugins", dest="selected_plugins", default=None,
        help="Choose plugins by comma separated id, all others deselected",
        action="store")
    parser.add_argument(
        "-d", "--deselect-plugins", dest="deselected_plugins", default=None,
        help="Choose plugins by comma separated id, unless selected",
        action="store")
    parser.add_argument(
        "-t", "--tests", dest="check_tests", default=False,
        help="Also check unit tests",
        action="store_true")
    parser.add_argument(
        "--docs", dest="check_docs", default=False,
        help="Also check doc files",
        action="store_true")
    parser.add_argument(
        "-g", "--generated", dest="check_generated", default=False,
        help="Also check generated Files",
        action="store_true")
    parser.add_argument(
        "--format", dest="format", default=None,
        help="Custom line format using flags %s" % ','.join(FLAGS),
        action="store")
    parser.add_argument(
        "-f", "--formatter", dest="formatter", default="brief",
        help="One of: %s" % ','.join(FORMATTERS.keys()),
        action="store")
    parser.add_argument(
        "-o", "--ordered", dest="ordered", default=False,
        help="Orders issues by file and line",
        action="store_true")
    parser.add_argument(
        "-r", "--raw", dest="raw", default=False,
        help="Just prints the output of the checker as is",
        action="store_true")
    return parser


def evaluate_options(args):
    """
    check command line options are valid

    :returns: args, path
    """
    if len(args.path) == 0:
        paths = [os.getcwd()]
    else:
        paths = os.path.join(args.path)
    if args.formatter not in FORMATTERS.keys():
        raise UnilintException("Unknown Formatter: %s" % args.formatter)

    try:
        args.level = int(args.level)
    except ValueError:
        if not args.level in LEVELS:
            raise UnilintException('Unknown level: %s\nAvailable: %s' %
                                   (args.level, LEVELS))

        else:
            args.level = LEVELS[args.level]

    # LOGGING
    logoutput = logging.StreamHandler()
    logoutput.propagate = False
    logoutput.setLevel(logging.NOTSET)
    log = logging.getLogger(__name__.rpartition('.')[0])
    log.handlers = []
    log.propagate = False
    log.addHandler(logoutput)

    if args.debug:
        formatter = logging.Formatter(
            '[%(asctime)s-%(name)s]%(levelname)s: %(message)s')
        logoutput.setFormatter(formatter)
        log.setLevel(logging.DEBUG)
        log.debug('Debug log enabled for %s' % log.name)
    elif args.verbose:
        log.setLevel(logging.INFO)
        log.debug('Verbose logging enabled for %s' % log.name)

    return args, paths


def unilint_main(argv):
    """
    CLI entry point
    """
    args = argv[1:]
    parser = get_unilint_parser()
    args = parser.parse_args(args)

    args, paths = evaluate_options(args)

    return run_cmd(paths, args)
