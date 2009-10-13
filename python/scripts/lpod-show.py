#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from os.path import basename
from sys import exit, stdout, stdin
from urlparse import urlparse

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document
from lpod.vfs import vfs
from lpod.table import odf_table



def get_target_directory(dirname, container_url):

    # Compute a name if not given
    if dirname is None:
        # Find the filename
        path = urlparse(container_url).path
        dirname = basename(path)

        # The last . => '_'
        point = dirname.rfind('.')
        if point != -1:
            dirname = ''.join([dirname[:point], '_', dirname[point + 1:]])

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



def sheet_to_csv(document, target):
    content = document.get_xmlpart('content')

    for table in content.get_table_list():
        table = odf_table(odf_element=table)

        name = table.get_tagname()
        filename = clean_filename(name) + '.csv'

        csv_file = target.open(filename, 'w')
        table.export_to_csv(csv_file)



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file>'
    description = 'Extract informations from an OpenDocument file.'
    parser = OptionParser(usage, version=__version__, description=description)

    # "target"
    parser.add_option('-d', '--dirname', action='store', type='string',
                      dest='dirname', metavar='<dirname>',
                      help='lpod-show.py stores all its output files in a '
                           'directory. With this option you can choice the '
                           'name of this directory. By default a name is '
                           'computed based on the input file name.')

    # "sdtout"
    parser.add_option('--stdout', dest='stdout', action='store_true',
                      default=False,
                  help='For an odt, dump "text.txt" in the standard output.')

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

    # Arguments OK ?
    if opts.stdout and doc_type != 'text':
        parser.print_help()
        exit(1)

    # text
    if doc_type == 'text':
        text = document.get_formated_text()

        if opts.stdout:
            stdout.write(text.encode('utf-8'))
        else:
            target = get_target_directory(opts.dirname, container_url)
            text_file = target.open('text.txt', 'w')
            text_file.write(text.encode('utf-8'))
    # spreadsheet
    elif doc_type == 'spreadsheet':
        target = get_target_directory(opts.dirname, container_url)
        sheet_to_csv(document, target)



