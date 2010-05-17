#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
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
from os.path import basename, splitext
from sys import exit, stdout

# Import from lxml
from lxml.etree import parse

# Import from lpod
from lpod import __version__
from lpod.toc import odf_create_toc
from lpod.document import odf_new_document_from_type
from lpod.heading import odf_create_heading
from lpod.scriptutils import add_option_output, check_target_file


def make_mm_structure(node, level):
    sub_struct = []
    for node in node.xpath('node'):
        sub_struct.append(make_mm_structure(node, level + 1))
    text = node.attrib['TEXT']
    return (level, text, sub_struct)



def make_document(structure, body):
    for level, text, struct in structure:
        # Create the heading with the corresponding level
        heading = odf_create_heading(level, text=text)
        # Add the heading to the document's body
        body.append(heading)
        make_document(struct, body)



if  __name__ == '__main__':
    # Options initialisation
    usage = '%prog <file>'
    description = 'Transform a mind-map file to an OpenDocument Text file.'
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --output
    add_option_output(parser)

    # Parse options
    opts, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        exit(1)

    # Get the 2 paths
    inname = args[0]
    outname = opts.output
    # Default value for the name of the output file.
    if not outname:
        mm_basename = basename(inname)
        outname = '%s.odt' % splitext(mm_basename)[0]
    # Check if the file already exists
    check_target_file(outname)

    # Open the XML file
    mm = parse(open(inname, 'rb'))
    # Get the first node of the mind map
    first_node = mm.xpath('/map/node')[0]
    # Make the structure
    mm_structure = make_mm_structure(first_node, 0)

    # Create a new ODT document
    document = odf_new_document_from_type('text')
    body = document.get_body()
    # Remove the default paragraph
    body.clear()
    # Begin with a TOC
    toc = odf_create_toc()
    body.append(toc)
    # Make the document from the structure
    make_document([mm_structure], body)
    # Fill the TOC
    toc.toc_fill()

    # Save the document
    document.save(outname, pretty=True)
    # Feed back to the user
    message = u"`%s' created from `%s' by lpOD\n"
    message = message % (outname, inname)
    stdout.write(message.encode('utf-8'))
    stdout.flush()
