#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from sys import exit, stdout

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document


def show(odf_file_url, automatic=True, common=True, properties=False):
    """Show the different styles of a document and their properties.
    """
    document = odf_get_document(odf_file_url)
    output = document.show_styles(automatic=automatic, common=common,
            properties=properties)
    # Print the styles
    stdout.write(output.encode('utf-8'))
    stdout.flush()



def merge(odf_file_url, from_file, pretty=True):
    source = odf_get_document(from_file)
    dest = odf_get_document(odf_file_url)
    dest.merge_styles_from(source)
    dest.save(pretty=pretty)
    print "Done (0 error, 0 warning)."



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file>'
    description = 'A command line interface to manipulate styles of ' \
                  'OpenDocument files.'
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --automatic
    parser.add_option('-a', '--automatic', dest='automatic',
            action='store_true', default=False,
            help="show automatic styles only")
    # --common
    parser.add_option('-c', '--common', dest='common', action='store_true',
            default=False, help="show common styles only")
    # --properties
    parser.add_option('-p', '--properties', dest='properties',
            action='store_true', help="show properties of styles")
    # --delete
    parser.add_option('-d', '--delete', dest='delete',
            action='store_true', help="delete all styles (except default)")
    # --merge
    help = ('copy styles from FILE to <file>. Any style with the same name '
            'will be replaced.')
    parser.add_option('-m', '--merge-styles-from', dest='merge',
            action='store', metavar='FILE', help=help)
    # Parse options
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit(1)
    odf_file_url = args[0]
    if options.delete:
        raise NotImplementedError
    elif options.merge:
        merge(odf_file_url, options.merge)
    else:
        automatic = options.automatic
        common =  options.common
        if not automatic ^ common:
            automatic, common = True, True
        show(odf_file_url, automatic=automatic, common=common,
                properties=options.properties)
