# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import

import re

from kanzen import CONFIGS


KEYWORDS = [
    "and",
    "assert",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "exec",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "as",
    "lambda",
    "not",
    "or",
    "pass",
    "print",
    "raise",
    "return",
    "super",
    "try",
    "while",
    "with",
    "yield",
    "None",
    "True",
    "False"]

patIndent = re.compile('^\s+')
endCharsForIndent = [':', '{', '(', '[']
closeBraces = {'{': '}', '(': ')', '[': ']'}


def get_indentation(line):
    indentation = ''
    if len(line) > 0 and line[-1] in endCharsForIndent:
        if CONFIGS.get('use_tabs', False):
            indentation = '\t'
        else:
            indentation = ' ' * CONFIGS.get('indentation_length', 4)
    elif len(line) > 0 and line[-1] == ',':
        count = filter(lambda x: \
            (line.count(x) - line.count(closeBraces[x])) % 2 != 0,
            endCharsForIndent[1:])
        if count:
            if CONFIGS.get('use_tabs', False):
                indentation = '\t'
            else:
                indentation = ' ' * CONFIGS.get('indentation_length', 4)
    space = patIndent.match(line)
    if space is not None:
        return space.group() + indentation
    return indentation
