from __future__ import print_function
import os
import sys
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
    FORMATTERS[f_id] = formatter_function


def register_plugin(plugin):
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
                    raise UnilintException('Unknown plugin dependency: %s of %s' % (dep, plugin_id))
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
                print("plugin %s failed to activate: %s" % (plugin_id, str(upie)))
    return selected_plugins


def remove_duplicates(issues):
    """
    looks for lines in list of issues having the same line number and
    indicating the same problem
    :param issues: list of Issue
    """
    if not issues:
        return issues
    issues2 = order_issues(issues)
    result = []
    sameline_issues = []
    lastline = -1
    for issue in issues2:
        if issue.line_number_start != lastline:
            sameline_issues = []
            lastline = issue.line_number_start
        else:
            is_duplicate = False
            for oldissue in sameline_issues:
                # for now, will rely on manually crafted duplicate
                # detection
                for keyword_vector in [('too long'),
                                       ('indentation contains'),
                                       ('variable '),
                                       ('not used', 'unused')]:
                    if keyword_vector[0] in oldissue.message:
                        for keyword_match in keyword_vector:
                            if keyword_match in issue.message:
                                is_duplicate = True
                                break
                    if is_duplicate:
                        break
            if is_duplicate:
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
    sorts Issues by line number
    :param issues: list of Issue
    """
    def keyfun(iss):
        return "%s%s" % (iss.path, str(iss.line_number_start).rjust(5, '0'))
    if not issues:
        return issues
    return sorted(issues, key=keyfun)


class IgnorableFolderException(Exception):
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
    :param path_to_check: path to file or folder in which to run checks on files
    :param basepath: absolute path that user gave in cli
    :param args: all CLI argument
    :param subdirs: subdirectories
    :param files: the files to check
    """
    if not os.path.exists(path_to_check):
        print('Ignoring argument that does not exist: %s' % path_to_check)
        return
    issues = []
    categorized_resources = {}
    for plugin_id in args.selected_plugins:
        new_categories = \
            args.selected_plugins[plugin_id].categorize_type(args,
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

    for resource, categories in categorized_resources.items():
        if 'hidden' in categories:
            continue
        if 'backup' in categories:
            continue
        if args.debug:
            print("processing: %s as %s" % (resource, categories))
        for plugin_id in args.selected_plugins:
            result = args.selected_plugins[plugin_id].check_resource(args,
                                                                     resource,
                                                                     categories)
            extend_maybe(issues, result)
            if result is not None and not args.ordered and not args.raw:
                # get the output to the user as quickly as possible
                print_issues(args, result, basepath)
    return remove_duplicates(issues)


def run_cmd(paths, args):
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

        print("unilint %s" % (VERSION))
        for _, plugin in args.selected_plugins.items():
            meta = plugin.get_meta_information()
            if meta is not None and meta != '':
                print(meta)
        return 0

    args.selected_plugins = resolve_plugins(args.selected_plugins,
                                            args.deselected_plugins)

    issues = []
    for path in paths:
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
                    if not args.raw and args.ordered:
                        # print here unless we already printed in check_path
                        dir_issues = order_issues(new_issues)
                        print_issues(args, dir_issues, abs_path)
                except IgnorableFolderException:
                    # beware concurrent modification, requires [:]
                    ignoreddirs = subdirs[:]
                    for dirname in ignoreddirs:
                        subdirs.remove(dirname)
        else:
            # is file
            issues.extend(check_path(path,
                                     os.path.dirname(path),
                                     args=args,
                                     force=True) or [])
            if not args.raw and args.ordered:
                print_issues(args, issues, os.path.dirname(path))

        sys.stdout.flush()

        # write to std_err so that report on std_out remains unchanged
        sys.stderr.write("%s issues found\n" % len(issues or []))
    return 0


def get_unilint_parser():
    parser = ArgumentParser()
    parser.add_argument('path', nargs='*',
                        help='a folder or filename to check')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False,
                        help="verbose output.",
                        action="store_true")
    parser.add_argument("--version", dest="version", default=False,
                        help="print version and meta information",
                        action="store_true")
    parser.add_argument("--debug", dest="debug", default=False,
                        help="debug output.",
                        action="store_true")
    parser.add_argument("-l", "--level", dest="level", default=LEVEL_ERROR,
                        help="A number or one of %s." %
                        (','.join(["%s(=%s)" % (k, v) for k, v in LEVELS.items()])),
                        action="store")
    parser.add_argument("-p", "--plugins", dest="show_plugins", default=False,
                        help="List Available plugins",
                        action="store_true")
    parser.add_argument("-s", "--select-plugins", dest="selected_plugins", default=None,
                        help="Choose plugins by comma separated id, all others deselected",
                        action="store")
    parser.add_argument("-d", "--deselect-plugins", dest="deselected_plugins", default=None,
                        help="Choose plugins by comma separated id, ignored with --select-plugins",
                        action="store")
    parser.add_argument("-t", "--tests", dest="check_tests", default=False,
                        help="Also check unit tests",
                        action="store_true")
    parser.add_argument("--docs", dest="check_docs", default=False,
                        help="Also check doc files",
                        action="store_true")
    parser.add_argument("-g", "--generated", dest="check_generated", default=False,
                        help="Also check generated Files",
                        action="store_true")
    parser.add_argument("--format", dest="format", default=None,
                        help="Custom line format using flags %s" % ','.join(FLAGS),
                        action="store")
    parser.add_argument("-f", "--formatter", dest="formatter", default="brief",
                        help="One of: %s" % ','.join(FORMATTERS.keys()),
                        action="store")
    parser.add_argument("-o", "--ordered", dest="ordered", default=False,
                        help="Orders issues by file and line",
                        action="store_true")
    parser.add_argument("-r", "--raw", dest="raw", default=False,
                        help="Just prints the output of the checker as is",
                        action="store_true")
    return parser


def evaluate_options(args):
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

    return args, paths


def unilint_main(argv):
    prog = argv[0]
    args = argv[1:]

    parser = get_unilint_parser()
    args = parser.parse_args(args)

    args, paths = evaluate_options(args)

    return run_cmd(paths, args)
