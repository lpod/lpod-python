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
from os.path import basename, splitext
from sys import exit, stdout

# Import from lpod
from lpod import __version__
from lpod.document import odf_new_document_from_type, odf_get_document
from lpod.toc import odf_create_toc
from lpod.vfs import vfs
from lpod.table import import_from_csv



def init_doc(mimetype):
    # Text mode
    if mimetype == "application/vnd.oasis.opendocument.text":
        output_doc = odf_new_document_from_type("text")

        # Begin with a TOC
        output_body = output_doc.get_body()
        output_body.append_element(odf_create_toc())
    # Spreadsheet mode
    elif mimetype in ("application/vnd.oasis.opendocument.spreadsheet",
                      "text/csv"):
        output_doc = odf_new_document_from_type("spreadsheet")
    # Presentation mode
    else:
        output_doc = odf_new_document_from_type("presentation")

    return output_doc



def _add_pictures(document, output_doc):
    # Copy extra parts (images...)
    container = document.container
    for partname in container.get_parts():
        if partname.startswith('Pictures/'):
            data = container.get_part(partname)
            # Suppose uniqueness
            output_doc.container.set_part(partname, data)



def add_odt(filename, output_doc):
    document = odf_get_document(filename)

    # Copy content
    src_body = document.get_body()
    output_body = output_doc.get_body()
    for element in src_body.get_children():
        tagname = element.get_tagname()
        # Skip TOC, etc.
        if tagname in ('text:sequence-decls', 'text:table-of-content'):
            continue
        # Copy the rest recursively
        output_body.append_element(element.clone())

    # Add pictures/
    _add_pictures(document, output_doc)

    # TODO embedded objects
    print 'Add "%s"' % filename



def _get_table_name(name, output_body):
    if isinstance(name, str):
        encoding = stdout.encoding or 'utf8'
        name = unicode(name, encoding)
    already_names = set([ table.get_table_name()
                          for table in output_body.get_table_list() ])
    if name in already_names:
        i = 1
        while True:
            new_name = u"%s_%d" % (name, i)
            if new_name not in already_names:
                return new_name
            i += 1
    else:
        return name



def add_ods(filename, output_doc):
    document = odf_get_document(filename)

    # Add the sheets
    output_body = output_doc.get_body()
    ods_body = document.get_body()
    for table in ods_body.get_table_list():
        name = table.get_table_name()
        name = _get_table_name(name, output_body)
        table.set_table_name(name)

        output_body.append_element(table)

    # Add pictures/
    _add_pictures(document, output_doc)

    print 'Add "%s"' % filename



def add_csv(filename, output_doc):
    output_body = output_doc.get_body()

    # Make the name
    name = splitext(basename(filename))[0]
    name = _get_table_name(name, output_body)

    table = import_from_csv(filename, name)

    output_body.append_element(table)
    print 'Add "%s"' % filename



def add_odp(filename, output_doc):
    document = odf_get_document(filename)

    # Add the pages
    output_body = output_doc.get_body()
    already_names = set([ page.get_page_name()
                          for page in output_body.get_draw_page_list() ])
    odp_body = document.get_body()
    for page in odp_body.get_draw_page_list():
        name = page.get_page_name()

        if name in already_names:
            i = 1
            while True:
                new_name = u"%s_%d" % (name, i)
                if new_name not in already_names:
                    name = new_name
                    break
                i += 1
            page.set_page_name(name)

        already_names.add(name)
        output_body.append_element(page)

    # Add pictures/
    _add_pictures(document, output_doc)

    print 'Add "%s"' % filename



if  __name__ == '__main__':
    # Options initialisation
    usage = "%prog <file1> [<file2> ...]"
    description = "Merge all input files in an unique OpenDocument file"
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --output
    parser.add_option('-o', '--output', action='store', type='string',
            dest='output', metavar='FILE', default=None,
            help="Place output in file FILE (out.od[t|s|p] by default)")

    # Parse !
    opts, filenames = parser.parse_args()

    # Arguments
    if not filenames:
        parser.print_help()
        exit(1)
    output_filename = opts.output
    output_doc = None

    # Concatenate content in the output doc
    for filename in filenames:

        # Exists ?
        if not vfs.exists(filename):
            print "Skip", filename, "not existing"
            continue

        # A good file => Only text, spreadsheet and CSV
        mimetype = vfs.get_mimetype(filename)
        if mimetype not in ("application/vnd.oasis.opendocument.text",
                            "application/vnd.oasis.opendocument.spreadsheet",
                            "text/csv",
                            "application/vnd.oasis.opendocument.presentation"):
            print 'Skip "%s" with mimetype "%s"' % (filename, mimetype)
            continue

        # Not yet an output_doc ?
        if output_doc is None:
            # Create an empty doc
            output_doc = init_doc(mimetype)
            output_mimetype = output_doc.get_type()
            print '%s documents detected' % output_mimetype.title()

            # Make the filename
            if output_filename is None:
                output_filename = "out.od%s" % output_mimetype[0]
            if vfs.exists(output_filename):
                vfs.remove(output_filename)

        # Add a text doc
        if mimetype == "application/vnd.oasis.opendocument.text":
            if output_mimetype != "text":
                print "We cannot merge a mix of text/spreadsheet/presentation!"
                exit(1)
            add_odt(filename, output_doc)
        # Add a spreadsheet doc
        elif mimetype in ("application/vnd.oasis.opendocument.spreadsheet",
                          "text/csv"):
            if output_mimetype != "spreadsheet":
                print "We cannot merge a mix of text/spreadsheet/presentation!"
                exit(1)
            # CSV ?
            if mimetype == "text/csv":
                add_csv(filename, output_doc)
            else:
                add_ods(filename, output_doc)
        # Add a presentation doc
        else:
            if output_mimetype != "presentation":
                print "We cannot merge a mix of text/spreadsheet/presentation!"
                exit(1)
            add_odp(filename, output_doc)

    # Extra for odt
    if output_mimetype == 'text':
        output_body = output_doc.get_body()
        toc = output_body.get_toc()
        toc.toc_fill()

    # Save
    if output_doc is not None:
        output_doc.save(output_filename, pretty=True)
        print 'Document "%s" generated' % output_filename
    else:
        print "Nothing to save, ..."
