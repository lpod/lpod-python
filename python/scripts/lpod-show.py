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
from sys import exit, stdout, stdin

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document
from lpod.vfs import vfs
from lpod.table import odf_table



def get_target_directory(dirname, container_url):
    # Check the name and create the directory
    if vfs.exists(dirname):
        message = 'The directory "%s" exists, can i overwrite it? [y/N]'
        stdout.write(message % dirname)
        stdout.flush()
        line = stdin.readline()
        line = line.strip().lower()
        if line == 'y':
            vfs.remove(dirname)
        else:
            exit(0)
    vfs.make_folder(dirname)
    return vfs.open(dirname)



def clean_filename(filename):
    filename = filename.encode('utf-8')
    allowed_characters = set([u'.', u'-', u'_', u'@'])
    result = []
    for c in filename:
        if c not in allowed_characters and not c.isalnum():
            result.append('_')
        else:
            result.append(c)
    return ''.join(result)



def text_to_stdout(document):
    text = document.get_formated_text()
    stdout.write(text.encode(stdout.encoding))
    stdout.flush()



def text_to_text(document, target):
    text_file = target.open('content.txt', 'w')
    text = document.get_formated_text()
    text_file.write(text.encode('utf-8'))
    text_file.close()



def spreadsheet_to_stdout(document):
    body = document.get_body()
    for table_element in body.get_table_list():
        table = odf_table(odf_element=table_element)
        table.export_to_csv(stdout, encoding=stdout.encoding)
        stdout.write("\n")
    stdout.flush()



def spreadsheet_to_csv(document, target):
    body = document.get_body()
    for table_element in body.get_table_list():
        table = odf_table(odf_element=table_element)
        name = table.get_tagname()
        filename = clean_filename(name) + '.csv'
        csv_file = target.open(filename, 'w')
        table.export_to_csv(csv_file)
        csv_file.close()



if  __name__ == '__main__':
    # Options initialisation
    usage = "%prog <file>"
    description = ("Dump text from an OpenDocument file to the standard "
                   "output")
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --dirname
    parser.add_option('-d', '--dirname', action='store', type='string',
            dest='dirname', metavar='DIRNAME',
            help="Dump output in files in the given directory.")
    # Parse !
    opts, args = parser.parse_args()
    # Container
    if len(args) != 1:
        parser.print_help()
        exit(1)
    container_url = args[0]
    # Open it!
    document = odf_get_document(container_url)
    doc_type = document.get_type()
    if opts.dirname:
        target = get_target_directory(opts.dirname, container_url)
    # text
    if doc_type in ('text', 'text-template', 'presentation',
            'presentation-template'):
        if opts.dirname:
            text_to_text(document, target)
        else:
            text_to_stdout(document)
    # spreadsheet
    elif doc_type in ('spreadsheet', 'spreadsheet-template'):
        if opts.dirname:
            spreadsheet_to_csv(document, target)
        else:
            spreadsheet_to_stdout(document)
    else:
        print "The OpenDocument format", doc_type, "is not supported yet."
        exit(1)
