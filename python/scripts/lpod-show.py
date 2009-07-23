#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from sys import exit

# Import from lpod
from lpod import __version__



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file>'
    description = 'Extract informations from an OpenDocument file.'
    parser = OptionParser(usage, version=__version__, description=description)

    # Parse !
    opts, args = parser.parse_args()

    # Container
    if len(args) != 1:
        parser.print_help()
        exit(1)
    container = args[0]

    print 'file:', container





