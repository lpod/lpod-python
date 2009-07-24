#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from sys import exit, stdout, stdin
from urlparse import urlparse
from os.path import basename

# Import from lpod
from lpod import __version__
from lpod.vfs import vfs


def get_target_directory(dirname, container):

    # Compute a name if not gived
    if dirname is None:
        # Find the filename
        path = urlparse(container).path
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
    container = args[0]

    target_directory = get_target_directory(opts.dirname, container)





