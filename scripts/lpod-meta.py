#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
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
from sys import exit, stdin

# Import from lpod
from lpod import __version__, ODF_META
from lpod.document import odf_get_document
from lpod.datatype import Date, DateTime
from lpod.scriptutils import printerr



def set_metadata(doc, set_list):
    meta = doc.get_part(ODF_META)
    for set_info in set_list:
        if '=' not in set_info:
            printerr('Bad argument -s "%s" (must be "name=value")' % set_info)
            exit(1)
        name, value = set_info.split('=', 1)
        name = name.lower().strip()
        value = value.strip()

        if name in ("title", "subject", "initial_creator",
                    "keywords", "generator", "description"):
            value = value.decode(stdin.encoding)
            func = meta.__getattribute__('set_' + name)
            func(value)
        elif name == "language":
            meta.set_language(value)
        elif name in ("modification_date", "creation_date"):
            try:
                if 'T' in value:
                    date = DateTime.decode(value)
                else:
                    date = Date.decode(value)
            except ValueError, error:
                printerr('Bad argument -s "%s": %s' % (set_info, error))
                exit(1)
            func = meta.__getattribute__('set_' + name)
            func(date)
        else:
            printerr('Unknown metadata name "%s", please choose: ' % name)
            printerr("       title, subject, initial_creator, keywords, "
                    "generator, description, modification_date or "
                    "creation_date")
            exit(1)

        # XXX User defined metadata?

    doc.save()



if  __name__ == '__main__':
    # Options initialisation
    usage = "%prog [options] <file>"
    description = "Dump metadata informations on the standard output"
    parser = OptionParser(usage, version=__version__, description=description)

    # Set
    help = 'Replace and/or set the metadata NAME with the value VALUE'
    parser.add_option('-s', '--set', action='append', dest='set_list',
            metavar='NAME=VALUE', help=help)

    # Parse !
    options, args = parser.parse_args()

    # Open the document
    if len(args) != 1:
        parser.print_help()
        exit(1)
    doc = odf_get_document(args[0])

    if options.set_list:
        # Set metadata, ...
        set_metadata(doc, options.set_list)
    else:
        # Dump
        print doc.get_formated_meta().encode('utf-8')
