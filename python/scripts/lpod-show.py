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
from lpod.utils import get_value



def _get_target_directory(dirname, container_url):

    # Compute a name if not gived
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



def _extract_structured_text(odf_element):
    result = []
    for element in odf_element.get_children():
        tag = element.get_name()
        text = element.get_text()

        if text == '':
            continue

        if tag == 'text:h':
            result.append(u'\n')
            result.append(text)
            result.append(u'\n')
            result.append(u'=' * len(text))
            result.append(u'\n')

        elif tag == 'text:p':
            result.append(text)
            result.append(u'\n')

        else:
            result.append(_extract_structured_text(element))

    return u''.join(result)



def _clean_filename(filename):
    filename = filename.encode('utf-8')

    allowed_characters = set([u'.', u'-', u'_', u'@'])
    result = []
    for c in filename:
        if c not in allowed_characters and not c.isalnum():
            result.append('_')
        else:
            result.append(c)
    return ''.join(result)



def _sheet_to_csv(document, target):
    content = document.get_xmlpart('content')

    for table in content.get_table_list():
        table = odf_table(odf_element=table)

        name = table.get_name()
        filename = _clean_filename(name) + '.csv'

        columns_nb, rows_nb = table.get_size()

        csv = target.open(filename, 'w')
        for r in range(1, rows_nb + 1):
            row = []
            for c in range(1, columns_nb + 1):
                cell = table.get_cell( (c, r) )

                value = get_value(cell)
                if type(value) is unicode:
                    value = value.encode('utf-8')
                if type(value) is str:
                    value = value.strip()
                value = '' if value is None else str(value)
                value.replace('"', "'")

                row.append('"%s"' % value)

            csv.write(';'.join(row))
            csv.write('\n')



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

    # Parse !
    opts, args = parser.parse_args()

    # Container
    if len(args) != 1:
        parser.print_help()
        exit(1)
    container_url = args[0]

    target = _get_target_directory(opts.dirname, container_url)
    document = odf_get_document(container_url)

    doc_type = document.get_type()
    # text
    if doc_type == 'text':
        body = document.get_body()
        text = _extract_structured_text(body)
        text_file = target.open('text.txt', 'w')
        text_file.write(text.encode('utf-8'))
    elif doc_type == 'spreadsheet':
        _sheet_to_csv(document, target)



