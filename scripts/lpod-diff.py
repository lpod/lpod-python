#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from the standard library
from difflib import unified_diff, ndiff
from optparse import OptionParser
from sys import exit, stdout
from time import ctime
from os import stat

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document



if  __name__ == '__main__':

    # Options initialisation
    usage = "%prog <doc1.odt> <doc2.odt>"
    description = "Show a diff between doc1.odt and doc2.odt"
    parser = OptionParser(usage, version=__version__, description=description)

    # --ndiff
    parser.add_option('-n', '--ndiff', action='store_true', default=False,
            help='use a contextual "ndiff" format to show the output')

    # Parse !
    options, args = parser.parse_args()

    # Go !
    if len(args) != 2:
        parser.print_help()
        exit(1)

    # Open the 2 documents, diff only for ODT
    doc1 = odf_get_document(args[0])
    doc2 = odf_get_document(args[1])
    if doc1.get_type() != 'text' or doc2.get_type() != 'text':
        parser.print_help()
        exit(1)

    # Convert in text before the diff
    text1 = doc1.get_formatted_text(True).splitlines(True)
    text2 = doc2.get_formatted_text(True).splitlines(True)

    # Make the diff !
    if options.ndiff:
        result = ndiff(text1, text2, None, None)
        result = [ line for line in result if not line.startswith(u' ') ]
    else:
        fromdate = ctime(stat(args[0]).st_mtime)
        todate = ctime(stat(args[1]).st_mtime)
        result = unified_diff(text1, text2, args[0], args[1], fromdate, todate)
    result = u''.join(result)
    encoding = stdout.encoding if stdout.encoding is not None else 'utf-8'
    result = result.encode(encoding)

    # And print it !
    print result
