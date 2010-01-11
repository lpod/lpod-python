#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
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
from sys import exit, stdout

# Import from lpod
from lpod import __version__
from lpod.document import odf_new_document_from_type
from lpod.heading import odf_create_heading
from lpod.list import odf_create_list, odf_create_list_item
from lpod.paragraph import odf_create_paragraph
from lpod.toc import odf_create_toc


# Import from docutils
from docutils.readers.standalone import Reader
from docutils.core import publish_doctree



def find_convert(node, context):
    tagname = node.tagname
    if tagname == "section":
        convert_section(node, context)
    elif tagname == "paragraph":
        convert_paragraph(node, context)
    elif tagname == "enumerated_list":
        convert_list(node, context, "enumerated")
    elif tagname == "bullet_list":
        convert_list(node, context, "bullet")
    elif tagname == "topic":
        convert_topic(node, context)
    else:
        print "Warning node not supported: %s" % tagname



def convert_section(node, context):
    # Inc the heading level
    context["heading-level"] += 1

    # Reset the top to body
    context["top"] = context["body"]

    for children in node:
        if children.tagname == "title":
            title = children.astext()
            heading = odf_create_heading(level=context["heading-level"],
                                         text=title)
            context["body"].append_element(heading)
        else:
            find_convert(children, context)

    # Restore the heading level
    context["heading-level"] -= 1



def convert_paragraph(node, context):
    paragraph = odf_create_paragraph(text=node.astext())
    context["top"].append_element(paragraph)



def convert_list(node, context, list_type):
    # XXX unused
    enumtype = node.get("enumtype") #enumerated
    bullet = node.get("bullet") #bullet

    odf_list = odf_create_list()
    context["top"].append_element(odf_list)

    # Save the current top
    old_top = context["top"]

    for item in node:

        if item.tagname != "list_item":
            print "Warning node not supported: %s" % item.tagname
            continue

        # Create a new item
        odf_item = odf_create_list_item()
        odf_list.append_element(odf_item)

        # A new top
        context["top"] = odf_item

        for children in item:
            find_convert(children, context)

    # And restore the top
    context["top"] = old_top



def convert_topic(node, context):
    # Reset the top to body
    context["top"] = context["body"]

    # Yet an other TOC ?
    if context["toc"] is not None:
        print "Warning: a TOC is already inserted"
        return

    toc = odf_create_toc()
    context["body"].append_element(toc)
    context["toc"] = toc



def convert(rst_txt):
    # Create a new document
    doc = odf_new_document_from_type("text")
    body = doc.get_body()

    # Convert
    reader = Reader(parser_name="restructuredtext")
    domtree = publish_doctree(rst_txt, reader=reader)

    # Init a context
    context = {"body": body, "top": body, "toc": None, "heading-level": 0}

    # Go!
    for children in domtree:
        if children.tagname == "title":
            print "global title:", children.astext()
        else:
            find_convert(children, context)

    # Finish
    toc = context["toc"]
    if toc is not None:
        toc.auto_fill(doc)

    return doc



if  __name__ == "__main__":

    # Options initialisation
    usage = "%prog [-o output] <filename>"
    description = "Convert a rst file into an odt file"
    parser = OptionParser(usage, version=__version__,
            description=description)

    # --output
    parser.add_option("-o", "--output", action="store", type="string",
            dest="output", metavar="FILE",
            help="dump the output into the file FILE instead of the standard "
                 "output.")

    # Parse !
    opts, args = parser.parse_args()

    # Source
    if len(args) != 1:
        parser.print_help()
        exit(1)
    source = args[0]

    # Convert
    document = convert(open(source).read())

    # Save
    if opts.output is not None:
        document.save(target=opts.output)
    else:
        document.save(target=stdout)


