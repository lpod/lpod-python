#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
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
from sys import exit

# Import from lpod
from lpod import __version__
from lpod.document import odf_new_document_from_type, odf_get_document
from lpod.toc import odf_create_toc
from lpod.vfs import vfs



if  __name__ == '__main__':
    # Options initialisation
    usage = "%prog <file1> [<file2> ...]"
    description = "Merge all input files in an unique OpenDocument file"
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --output
    parser.add_option('-o', '--output', action='store', type='string',
            dest='output', metavar='FILE', default="out.odt",
            help="Place output in file FILE (out.odt by default)")

    # Parse !
    opts, args = parser.parse_args()

    # Arguments
    filenames = args
    if not filenames:
        parser.print_help()
        exit(1)

    # Create the output file
    output_filename = opts.output
    if vfs.exists(output_filename):
        vfs.remove(output_filename)
    output_doc = odf_new_document_from_type('text')

    # Begin with a TOC
    dest_body = output_doc.get_body()
    dest_body.append_element(odf_create_toc())

    # Concatenate content in the output doc
    for filename in filenames:
        if not vfs.exists(filename):
            print "Skip", filename, "not existing"
            continue
        document = odf_get_document(filename)
        type = document.get_type()
        if type not in ('text', 'text-template'):
            print "Skip", filename, type, "not text"
            continue
        # Copy content
        src_body = document.get_body()
        for element in src_body.get_children():
            tagname = element.get_tagname()
            # Skip TOC, etc.
            if tagname in ('text:sequence-decls', 'text:table-of-content'):
                continue
            # Copy the rest recursively
            dest_body.append_element(element.clone())
        # Copy extra parts (images...)
        container = document.container
        for partname in container._odf_container__get_contents():
            if partname.startswith('Pictures/'):
                data = container.get_part(partname)
                # Suppose uniqueness
                output_doc.container.set_part(partname, data)
            # TODO embedded objects
        del document
        print "Added", filename, "document"

    output_doc.save(output_filename, pretty=True)
    print "Document", output_filename, "generated."
