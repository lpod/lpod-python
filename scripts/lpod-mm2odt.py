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
from sys import exit, stdout, stdin

# Import from lxml
from lxml.etree import parse

# Import from lpod
from lpod import __version__
from lpod.toc import odf_create_toc
from lpod.document import odf_new_document_from_type
from lpod.heading import odf_create_heading
from lpod.vfs import vfs


def check_for_overwrite(odt_file_url):
    if vfs.exists(odt_file_url):
        message = 'The file "%s" exists, can i overwrite it? [y/N]'
        stdout.write(message % odt_file_url)
        stdout.flush()
        line = stdin.readline()
        line = line.strip().lower()
        if line != 'y':
            stdout.write('Operation aborted\n')
            stdout.flush()
            exit(0)



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
        body.append_element(heading)
        make_document(struct, body)



if  __name__ == '__main__':
    # Options initialisation
    usage = '%prog <file>'
    description = 'Transform a mind-map file to an OpenDocument Text file.'
    oparser = OptionParser(usage, version=__version__,
                           description=description)
    help = 'place output in the specified file.'
    oparser.add_option('-o', '--output', dest='output', metavar='<output>',
                       action='store', help=help)

    # Parse options
    opts, args = oparser.parse_args()
    if len(args) < 1:
        oparser.print_help()
        exit(1)

    # Get the 2 URLs
    mm_file_url = args[0]
    odt_file_url = opts.output
    # Default value for the URL of the ODT file.
    if not odt_file_url:
        mm_basename = basename(mm_file_url)
        odt_file_url = '%s.odt' % splitext(mm_basename)[0]
    # Check if the file already exists
    check_for_overwrite(odt_file_url)

    # Open the XML file
    mm = parse(open(mm_file_url))
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
    body.append_element(toc)
    # Make the document from the structure
    make_document([mm_structure], body)
    # Fill the TOC
    toc.auto_fill(document)

    # Save the document
    document.save(odt_file_url, pretty=True)
    # Feed back to the user
    message = u"`%s' created from `%s' by lpOD\n"
    message = message % (odt_file_url, mm_file_url)
    stdout.write(message.encode('utf-8'))
    stdout.flush()
