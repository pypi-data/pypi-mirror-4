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


class Issue:

    def __init__(self, path, message, checker_id,
                 line_number_start=None, line_number_end=None,
                 line_position=None,
                 source_code=None,
                 severity=None, category=None):
        """
        :param path: filename or folder name
        :param message: What is wrong
        :param checker_id: by which checker this was found
        :param line_number_start: where the issue starts in the file
        :param line_number_end: where the issue ends in the file
        (same as start for one liners)
        :param line_position: The char to highlight in line
        :param severity: unilint unified severity
        :param category: checker specific category
        """
        self.path = path
        self.message = message
        self.checker_id = checker_id
        self.line_number_start = line_number_start
        self.line_number_end = line_number_end
        self.line_position = line_position
        self.source_code = source_code
        self.severity = severity
        self.category = category

    def __repr__(self):
        attributes = [self.path,
                      self.message,
                      self.line_number_start,
                      self.line_number_end,
                      self.line_position,
                      self.source_code,
                      self.severity,
                      self.category]
        attributes = [a for a in attributes if a is not None]
        return "[%s]%s" % (self.checker_id,
                           ":".join([str(a) for a in attributes]))
