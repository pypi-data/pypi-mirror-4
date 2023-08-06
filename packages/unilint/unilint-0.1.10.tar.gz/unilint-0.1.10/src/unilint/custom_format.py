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

'template based issue formatting'

import os
from string import Template
from unilint.common import UnilintException

FILENAME = 'f'
RELPATH = 'F'
MESSAGE = 'M'
LINE = 'L'
POSITION = 'P'
CHECKER = 'C'
TYPE = 'T'
SEVERITY = 'S'
FLAGSYMBOLS = [FILENAME, RELPATH, MESSAGE, LINE, POSITION, CHECKER, TYPE,
               SEVERITY]
FLAGS = ['$%s' % flag_temp for flag_temp in FLAGSYMBOLS]


def print_formatted(format_template, issue_list, basepath):
    '''print issue according to template'''
    if format_template is None:
        return
    flag_provided = False

    for flag in FLAGS:
        if flag in format_template:
            flag_provided = True
            break
    if not flag_provided:
        raise UnilintException(
            "No known flags provided : %s" % format_template)

    template = Template(format_template)

    for issue in issue_list:
        issuepath = issue.path or basepath
        if basepath != issuepath:
            loc_str = os.path.relpath(issuepath, basepath)
        else:
            loc_str = issuepath
        attr = {FILENAME: os.path.basename(issuepath),
                RELPATH: loc_str,
                MESSAGE: issue.message,
                LINE: issue.line_number_start or '',
                POSITION: issue.line_position or '',
                CHECKER: issue.checker_id,
                TYPE: issue.category or '',
                SEVERITY: issue.severity or ''}
        print(template.substitute(attr))
