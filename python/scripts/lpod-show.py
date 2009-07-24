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



def _get_text(document):
    content = document.get_xmlpart('content')
    body = content.get_text_body()

    result = []
    for element in body.get_element_list('//*'):
        tag = element.get_name()

        text = [ text for text in element.xpath('text:span/text()|text()') ]
        text = u''.join(text)

        if text == '':
            continue

        if tag == 'text:h':
            if result:
                result.append(u'\n')

            result.append(text)
            result.append(u'\n')
            result.append(u'=' * len(text))
            result.append(u'\n')
        elif tag == 'text:p':
            result.append(text)
            result.append(u'\n')

    return u''.join(result)



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

    text = _get_text(document)
    text_file = target.open('text.txt', 'w')
    text_file.write(text)


