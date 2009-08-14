#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from os.path import basename, splitext
from sys import exit, stdout, stdin

# Import from lxml
from lxml.etree import parse

# Import from lpod
from lpod import __version__
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
    oparser = OptionParser(usage, version=__version__, description=description)
    help = 'place output in the specified file.'
    oparser.add_option('-o', '--output', dest='output', metavar='<output>',
                       action='store', help=help)
    # Parse options
    opts, args = oparser.parse_args()

    if len(args) < 1:
        oparser.print_help()
        exit(1)

    # Get the 2 urls
    mm_file_url = args[0]
    odt_file_url = opts.output
    # Default value for the url of the odt file.
    if not odt_file_url:
        mm_basename = basename(mm_file_url)
        odt_file_url = '%s.odt' % splitext(mm_basename)[0]
    # Check if the file already exists
    check_for_overwrite(odt_file_url)


    # Open the xml file
    mm = parse(open(mm_file_url))
    # Get the first node of the mind map
    first_node = mm.xpath('/map/node')[0]
    # Make the structure
    mm_structure = make_mm_structure(first_node, 0)

    # Create a new odt document
    document = odf_new_document_from_type('text')
    # Make the document from the structure
    make_document([mm_structure], document.get_body())

    # Save the document
    document.save(odt_file_url, pretty=True)
    # Feed back to the user
    message = "`%s' created from `%s' by lpOD\n"
    stdout.write(message % (odt_file_url, mm_file_url))

