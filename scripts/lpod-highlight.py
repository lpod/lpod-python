#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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

# Import from the standard library
from optparse import OptionParser
from sys import exit, stdin

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document
from lpod.scriptutils import add_option_output, printinfo
from lpod.style import odf_create_style
from lpod.styles import rgb2hex


def highlight(odf_file_url, pattern, color=None, background_color=None,
              italic=False, bold=False, target=None, pretty=True):

    # Make display_name and name
    display_name = [u"Highlight"]
    if color and color != 'none':
        display_name.append(unicode(color).capitalize())
    if background_color and background_color != 'none':
        display_name.append(unicode(background_color).capitalize())
    if italic:
        display_name.append(u"Italic")
    if bold:
        display_name.append(u"Bold")
    display_name = u" ".join(display_name)
    name = display_name.replace(u" ", u"_20_")

    # Is our style already installed?
    style = document.get_style('text', name)
    if style is None:
        color = rgb2hex(color) if color != 'none' else None
        background_color = (rgb2hex(background_color)
                if background_color != 'none' else None)
        style = odf_create_style('text', name,
                italic=italic, bold=bold, color=color,
                background_color=background_color)
        document.insert_style(style, automatic=True)

    # Patch!
    body = document.get_body()
    i = -1
    for i, paragraph in enumerate(body.get_paragraph_list(content=pattern) +
                                  body.get_heading_list(content=pattern)):
        # Don't colour the table of content
        if paragraph.get_parent().get_tag() in ('text:index-title',
                'text:index-body'):
            continue
        paragraph.set_span(name, regex=pattern)
    document.save(target=target, pretty=pretty)
    printinfo((i + 1), "paragraphs changed (0 error, 0 warning).")



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file> <pattern>'
    description = ("highlight the text matching the given regular "
                   "expression (Python syntax). May not display in some "
                   "office suites.")
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --color
    help = ("the name or #rrggbb color of the font color: black, blue, "
            "brown, cyan, green, grey, magenta, orange, pink, red, violet, "
            "white, yellow or none (default)")
    parser.add_option('-c', '--color', default='none', metavar='COLOR',
            help=help)
    # --background
    help = ("the name or #rrggbb color of the background color: black, "
            "blue, brown, cyan, green, grey, magenta, orange, pink, red, "
            "violet, white, yellow (default) or none")
    parser.add_option('-g', '--background', default='yellow',
            metavar='BACKGROUND', help=help)
    # --italic
    parser.add_option('-i', '--italic', dest='italic', action='store_true',
            default=False, help='set the italic font style')
    # --bold
    parser.add_option('-b', '--bold', dest='bold', action='store_true',
            default=False, help='set the bold font weight')
    # --output
    add_option_output(parser)
    # Parse options
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        exit(1)
    odf_file_url, pattern = args
    pattern = unicode(pattern, stdin.encoding)
    document = odf_get_document(odf_file_url)
    highlight(document, pattern, options.color, options.background,
            options.italic, options.bold, target=options.output)
