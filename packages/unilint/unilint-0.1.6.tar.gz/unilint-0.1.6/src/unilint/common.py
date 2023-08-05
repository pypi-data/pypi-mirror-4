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
import logging
import subprocess
import copy


class UnilintException(Exception):
    pass


def is_binary(filename):
    """Return true if the given filename is binary."""
    fin = open(filename, 'rb')
    try:
        chunksize = 1024
        while 1:
            chunk = fin.read(chunksize)
            if '\0' in chunk:  # found null byte
                return True
            if len(chunk) < chunksize:
                break  # done
    finally:
        fin.close()
    return False


def is_script(path):
    return (re.match('^#|.*~$|^_|^\.', os.path.basename(path)) is None and
            not is_binary(path))


def run_shell_command(cmd,
                      cwd=None,
                      shell=False,
                      us_env=True,
                      show_stdout=False,
                      verbose=False,
                      ignore_returncodes=None,
                      capture_std_err=False):
    """
    executes a command and hides the stdout output, loggs
    stderr output when command result is not zero. Make sure to sanitize arguments in the command.

    :param cmd: A string to execute.
    :param shell: Whether to use os shell, this is DANGEROUS, as vulnerable to shell injection.
    :returns: ( returncode, stdout, stderr)
    :raises: OSError
    """
    try:
        env = copy.copy(os.environ)
        if us_env:
            env["LANG"] = "en_US.UTF-8"
        proc = subprocess.Popen(cmd,
                                shell=shell,
                                cwd=cwd,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                env=env)
        # when we read output in while loop, it will not be returned
        # in communicate()
        stderr_buf = []
        stdout_buf = []
        if verbose or show_stdout:
            # listen to stdout and print
            while True:
                line = proc.stdout.readline()
                if line != '':
                    if verbose:
                        print(line),
                        stdout_buf.append(line)
                line2 = proc.stderr.readline()
                if line2 != '':
                    if verbose:
                        print(line2),
                        stderr_buf.append(line2)
                if ((not line and not line2) or proc.returncode is not None):
                    break
        (stdout, stderr) = proc.communicate()
        stdout_buf.append(stdout)
        stdout = "\n".join(stdout_buf)
        stderr_buf.append(stderr)
        stderr = "\n".join(stderr_buf)
        if capture_std_err is True:
            stdout = "\n".join(stderr_buf)

        message = None
        if proc.returncode != 0 and \
                (ignore_returncodes is None or
                 not proc.returncode in ignore_returncodes) and \
                stderr is not None and stderr != '':
            logger = logging.getLogger('unilint')
            message = "Command failed: '%s'" % (cmd)
            if cwd is not None:
                message += "\n run at: '%s'" % (cwd)
            message += "\n errcode: %s:\n%s" % (proc.returncode, stderr)
            logger.warn(message)
        result = stdout
        if result is not None:
            result = result.rstrip()
        return (proc.returncode, result, message)
    except OSError as ose:
        logger = logging.getLogger('unilint')
        message = ("Command failed with OSError. '%s' <%s, %s>:\n%s" %
                   (cmd, shell, cwd, ose))
        logger.error(message)
        raise
