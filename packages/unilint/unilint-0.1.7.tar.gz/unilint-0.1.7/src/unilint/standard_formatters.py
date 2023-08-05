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

from unilint.unilint_main import register_formatter
from unilint.custom_format import print_formatted

# pylint: disable-msg=W0613


def register_standard_formatters():
    def print_brief(unused_options, issue_list, basepath):
        if issue_list is None:
            return
        for issue in issue_list:
            issuepath = issue.path or basepath
            if basepath != issuepath:
                loc_str = os.path.relpath(issuepath, basepath)
            else:
                loc_str = issuepath
            location = "%s :%s:%s:" % (loc_str,
                                       str(issue.line_number_start or '').ljust(3),
                                       str(issue.line_position or '').ljust(3))
            location = location.ljust(20)
            print("%s   %s" % (location, issue.message))

    def print_full(unused_options, issue_list, basepath):
        print_formatted('[$C\t$S\t$T]$F:$L:$P:\t$M', issue_list, basepath)

    def print_short(unused_options, issue_list, basepath):
        print_formatted('$f:$L: $M', issue_list, basepath)

    register_formatter('brief', print_brief)
    register_formatter('full', print_full)
    register_formatter('short', print_short)
