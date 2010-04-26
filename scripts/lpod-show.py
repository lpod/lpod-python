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
from lpod.scriptutils import add_option_output, printerr
from lpod.vfs import vfs



def get_target_directory(dirname):
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



def dump(txt, to_file):
    try:
        encoding = to_file.encoding if to_file.encoding else 'utf-8'
    except AttributeError:
        encoding = 'utf-8'
    txt = txt.encode(encoding)
    to_file.write(txt)



def dump_pictures(document, target):
    for part_name in document.get_parts():
        if part_name.startswith('Pictures/'):
            if not target.exists('Pictures'):
                target.make_folder('Pictures')
            data = document.get_part(part_name)
            encoding = stdout.encoding if stdout.encoding else 'utf-8'
            to_file = target.open(part_name.encode(encoding), 'w')
            to_file.write(data)



def spreadsheet_to_stdout(document):
    encoding = stdout.encoding
    if encoding is None:
        encoding = 'utf-8'
    body = document.get_body()
    for table in body.get_table_list():
        table.rstrip_table(aggressive=True)
        table.export_to_csv(stdout, encoding=encoding)
        stdout.write("\n")
    stdout.flush()



def spreadsheet_to_csv(document, target):
    body = document.get_body()
    for table in body.get_table_list():
        name = table.get_table_name()
        filename = clean_filename(name) + '.csv'
        csv_file = target.open(filename, 'w')

        table.rstrip_table(aggressive=True)
        table.export_to_csv(csv_file)
        csv_file.close()



if  __name__ == '__main__':
    # Options initialisation
    usage = ( '%prog -o <dir-name> [--rst] <odf-file>\n'
       '       %prog [--styles] [--meta] [--no-content] [--rst] <odf-file>')
    description = ("Dump text from an OpenDocument file to the standard "
                   "output, optionally styles and meta (and the Pictures/* "
                   "in '-o <dir-name>' mode)")
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --meta
    parser.add_option('-m', '--meta', action='store_true', default=False,
            help='dump metadata in stdout')
    # --styles
    parser.add_option('-s', '--styles', action='store_true', default=False,
            help='dump styles in stdout')
    # --no-content
    parser.add_option('-n', '--no-content', action='store_true',
            default=False, help='do not dump content in stdout')
    # --rst
    parser.add_option('-r', '--rst', action='store_true', default=False,
            help='Dump the content file with a reST syntax')
    # --output
    add_option_output(parser)
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
    if opts.output:
        target = get_target_directory(opts.output)
    # Meta / Styles / Pictures
    if opts.output:
        # Meta
        to_file = target.open('meta.txt', 'w')
        dump(document.get_formated_meta(), to_file)
        # Styles
        to_file = target.open('styles.txt', 'w')
        dump(document.show_styles(), to_file)
        # Pictures
        dump_pictures(document, target)
    else:
        if opts.meta:
            dump(document.get_formated_meta(), stdout)
        if opts.styles:
            dump(document.show_styles(), stdout)
    # text
    if doc_type in ('text', 'text-template', 'presentation',
            'presentation-template'):
        if opts.output:
            to_file = target.open('content.txt', 'w')
            dump(document.get_formatted_text(rst_mode=opts.rst), to_file)
        elif not opts.no_content:
            dump(document.get_formatted_text(rst_mode=opts.rst), stdout)
    # spreadsheet
    elif doc_type in ('spreadsheet', 'spreadsheet-template'):
        if opts.output:
            spreadsheet_to_csv(document, target)
        elif not opts.no_content:
            spreadsheet_to_stdout(document)
    else:
        printerr("The OpenDocument format", doc_type, "is not supported yet.")
        exit(1)
