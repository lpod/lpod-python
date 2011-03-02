# -*- coding: UTF-8 -*-
#
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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

# Import from the Standard Library
from mimetypes import guess_type
from os.path import exists, isfile
from StringIO import StringIO
from sys import stdin, stdout, stderr

# Import from lpod


"""Utilities shared by the scripts.
"""


def check_target_file(path, kind="file"):
    if exists(path):
        message = 'The %s "%s" exists, overwrite it? [y/N]'
        stderr.write(message % (kind, path))
        stderr.flush()
        line = stdin.readline()
        line = line.strip().lower()
        if line != 'y':
            stderr.write('Operation aborted\n')
            stderr.flush()
            exit(0)



def check_target_directory(path):
    return check_target_file(path, kind="directory")



encoding_map = {'gzip': 'application/x-gzip', 'bzip2': 'application/x-bzip2'}


def get_mimetype(filename):
    if not isfile(filename):
        return 'application/x-directory'
    mimetype, encoding = guess_type(filename)
    if encoding is not None:
        return encoding_map.get(encoding, encoding)
    if mimetype is not None:
        return mimetype
    return 'application/octet-stream'



def add_option_output(parser, metavar="FILE", complement=""):
    help = "dump the output into %s %s" % (metavar, complement)
    parser.add_option("-o", "--output", metavar=metavar, help=help)



def printinfo(*args, **kw):
    # TODO switch to print function
    indent = kw.get('indent', 0)
    if indent:
        stderr.write(' ' * indent)
    encoding = stderr.encoding if stderr.encoding is not None else 'utf-8'
    output = ' '.join(arg.encode(encoding) for arg in args)
    stderr.write(output)
    stderr.write("\n")


def printwarn(*args, **kw):
    printinfo("Warning:", *args, **kw)


def printerr(*args, **kw):
    printinfo("Error:", *args, **kw)



class StdoutWriter(StringIO):
    """Some proxy to write output to stdout in scripts. Because The zipfile
    module raises "IOError: [Errno 29] Illegal seek" when writing to stdout
    directly.
    """

    def write(self, s):
        stdout.write(s)
        StringIO.write(self, s)
