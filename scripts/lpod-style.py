#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
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
from optparse import OptionParser
from sys import exit, stdout

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document
from lpod.scriptutils import add_option_output, StdoutWriter, printinfo


def show_styles(document, target, automatic=True, common=True,
        properties=False):
    """Show the different styles of a document and their properties.
    """
    output = document.show_styles(automatic=automatic, common=common,
            properties=properties)
    # Print the output
    if target is None:
        target = stdout
    encoding = target.encoding if target.encoding is not None else 'utf-8'
    target.write(output.encode(encoding))
    target.flush()



def delete_styles(document, target, pretty=True):
    n = document.delete_styles()
    document.save(target=target, pretty=pretty)
    printinfo(n, "styles removed (0 error, 0 warning).")



def merge_styles(document, from_file, target=None, pretty=True):
    source = odf_get_document(from_file)
    document.delete_styles()
    document.merge_styles_from(source)
    document.save(target=target, pretty=pretty)
    printinfo("Done (0 error, 0 warning).")



if  __name__ == '__main__':
    # Options initialisation
    usage = '%prog <file>'
    description = 'A command line interface to manipulate styles of ' \
                  'OpenDocument files.'
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --automatic
    parser.add_option('-a', '--automatic', action='store_true', default=False,
            help="show automatic styles only")
    # --common
    parser.add_option('-c', '--common', action='store_true', default=False,
            help="show common styles only")
    # --properties
    parser.add_option('-p', '--properties', action='store_true',
            help="show properties of styles")
    # --delete
    help = ("return a copy with all styles (except default) deleted from "
            "<file>")
    parser.add_option('-d', '--delete', action='store_true', help=help)
    # --merge
    help = ('copy styles from FILE to <file>. Any style with the same name '
            'will be replaced.')
    parser.add_option('-m', '--merge-styles-from', dest='merge',
            metavar='FILE', help=help)
    # --output
    add_option_output(parser)
    # Parse options
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit(1)
    document = odf_get_document(args[0])
    if options.delete:
        target = options.output
        if target is None:
            target = StdoutWriter()
        delete_styles(document, target)
    elif options.merge:
        merge_styles(document, options.merge, target=options.output)
    else:
        automatic = options.automatic
        common = options.common
        if not automatic ^ common:
            automatic, common = True, True
        target = options.output
        if target is not None:
            target = open(target, 'wb')
        show_styles(document, target, automatic=automatic,
                common=common, properties=options.properties)
