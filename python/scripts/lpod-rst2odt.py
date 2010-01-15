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
from lpod.link import odf_create_link
from lpod.list import odf_create_list, odf_create_list_item
from lpod.note import odf_create_note
from lpod.paragraph import odf_create_paragraph, odf_create_line_break
from lpod.paragraph import odf_create_undividable_space
from lpod.span import odf_create_span
from lpod.style import odf_create_style
from lpod.toc import odf_create_toc


# Import from docutils
from docutils.readers.standalone import Reader
from docutils.core import publish_doctree



def find_convert(node, context):
    tagname = node.tagname
    if tagname == "#text":
        convert_text(node, context)
    elif tagname == "section":
        convert_section(node, context)
    elif tagname == "paragraph":
        convert_paragraph(node, context)
    elif tagname == "enumerated_list":
        convert_list(node, context, "enumerated")
    elif tagname == "bullet_list":
        convert_list(node, context, "bullet")
    elif tagname == "topic":
        convert_topic(node, context)
    elif tagname == "footnote":
        convert_footnote(node, context)
    elif tagname == "footnote_reference":
        convert_footnote_reference(node, context)
    elif tagname == "emphasis":
        convert_emphasis(node, context)
    elif tagname == "strong":
        convert_strong(node, context)
    elif tagname == "literal":
        convert_literal(node, context)
    elif tagname == "literal_block":
        convert_literal_block(node, context)
    elif tagname == "reference":
        convert_reference(node, context)
    elif tagname == "definition_list":
        convert_definition_list(node, context)
    elif tagname == "block_quote":
        convert_block_quote(node, context)
    else:
        print "Warning node not supported: %s" % tagname



def convert_text(node, context):
    context["top"].append_element(node.astext())



def convert_section(node, context):
    # Inc the heading level
    context["heading-level"] += 1

    # Reset the top to body
    context["top"] = context["body"]

    # Convert
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
    paragraph = odf_create_paragraph()
    context["top"].append_element(paragraph)

    # Save the current top
    old_top = context["top"]

    # Convert
    context["top"] = paragraph
    for children in node:
        find_convert(children, context)

    # And restore the top
    context["top"] = old_top



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



def convert_footnote(node, context):
    # XXX ids is a list ??
    refid = node.get("ids")[0]

    # Find the footnote
    footnotes = context["footnotes"]
    if refid not in footnotes:
        print 'Warning: unknown footnote "%s"' % refid
        return
    footnote_body = footnotes[refid].get_element("text:note-body")

    # Save the current top
    old_top = context["top"]

    # Fill the note
    context["top"] = footnote_body
    for children in node:
        # We skip the label (already added)
        if children.tagname == "label":
            continue
        find_convert(children, context)

    # And restore the top
    context["top"] = old_top



def convert_footnote_reference(node, context):
    refid = node.get("refid")
    citation = node.astext()

    footnote = odf_create_note(note_id=refid, citation=citation)
    context["top"].append_element(footnote)

    context["footnotes"][refid] = footnote



def _convert_style_like(node, context, style):
    # Create the span
    span = odf_create_span(style=style.get_style_name())
    context["top"].append_element(span)

    # Save the current top
    old_top = context["top"]

    # Convert
    context["top"] = span
    for children in node:
        find_convert(children, context)

    # And restore the top
    context["top"] = old_top



def convert_emphasis(node, context):
    # Yet an emphasis style ?
    styles = context["styles"]
    if "emphasis" in styles:
        emphasis = styles["emphasis"]
    else:
        emphasis = odf_create_style("text", italic=True)
        styles["emphasis"] = emphasis
        context["doc"].insert_style(emphasis, automatic=True)

    # Convert
    _convert_style_like(node, context, emphasis)



def convert_strong(node, context):
    # Yet a strong style ?
    styles = context["styles"]
    if "strong" in styles:
        strong = styles["strong"]
    else:
        strong = odf_create_style("text", bold=True)
        styles["strong"] = strong
        context["doc"].insert_style(strong, automatic=True)

    # Convert
    _convert_style_like(node, context, strong)



def _get_literal_style(context, family):
    # family = "text" or "paragraph"

    FONT = "FreeMono"

    # Yet a literal style ?
    styles = context["styles"]
    style_name = "%s-literal" % family
    if  style_name in styles:
        return styles[style_name]

    # A monospace font
    if not ("text-literal" in styles or "paragraph-literal" in styles):
        font = odf_create_style("font-face", name=FONT)
        font.set_attribute("svg:font-family", FONT)
        font.set_attribute("style:font-family-generic", "modern")
        font.set_attribute("style:font-pitch", "fixed")
        context["doc"].insert_style(font)

    # And the style
    if family == "paragraph":
        style = odf_create_style(family, parent="Standard")
    else:
        style = odf_create_style(family)
    style.set_style_properties(properties={"style:font-name": FONT},
                               area="text")
    context["doc"].insert_style(style, automatic=True)

    # Save it
    styles[style_name] = style
    return style



def convert_literal(node, context):
    literal = _get_literal_style(context, "text")

    # Convert
    _convert_style_like(node, context, literal)


def convert_literal_block(node, context):
    literal = _get_literal_style(context, "paragraph")
    paragraph = odf_create_paragraph(style=literal.get_style_name())
    context["top"].append_element(paragraph)

    # Convert
    for children in node:
        # Only text
        if children.tagname != "#text":
            print 'node "%s" not supported in literal block' % children.tagname
            continue
        text = children.astext()

        tmp = []
        spaces = 0
        for c in text:
            if c == '\n':
                if tmp:
                    tmp = u"".join(tmp)
                    paragraph.append_element(tmp)
                    tmp = []
                spaces = 0
                paragraph.append_element(odf_create_line_break())
            elif c == '\r':
                continue
            elif c == ' ':
                spaces += 1
            elif c == '\t':
                # Tab = 4 spaces
                spaces += 4
            else:
                if spaces >= 2:
                    if tmp:
                        tmp = u"".join(tmp)
                        paragraph.append_element(tmp)
                        tmp = []
                    paragraph.append_element(
                              odf_create_undividable_space(spaces))
                    spaces = 0
                elif spaces == 1:
                    tmp.append(' ')
                    spaces = 0
                tmp.append(c)
        if tmp:
            tmp = u"".join(tmp)
            paragraph.append_element(tmp)



def convert_reference(node, context):
    refuri = node.get("refuri")
    text = node.astext()

    link = odf_create_link(refuri)
    link.set_text(text)
    context["top"].append_element(link)



def convert_definition_list(node, context):
    # TODO Add the style
    for item in node:
        if item.tagname != "definition_list_item":
            print 'node "%s" not supported in definition_list' % item.tagname
            continue

        for children in item:
            tagname = children.tagname
            if tagname == "term":
                paragraph = odf_create_paragraph(text=children.astext())
                context["top"].append_element(paragraph)
            elif tagname == "definition":
                for subchildren in children:
                    find_convert(subchildren, context)
            else:
                print ('node "%s" not supported in definition_list_item' %
                       item.tagname)



def convert_block_quote(node, context):
    # TODO Add the style
    for children in node:
        find_convert(children, context)



def convert(rst_txt):
    # Create a new document
    doc = odf_new_document_from_type("text")
    body = doc.get_body()

    # Convert
    reader = Reader(parser_name="restructuredtext")
    domtree = publish_doctree(rst_txt, reader=reader)

    # Init a context
    context = {"doc": doc, "body": body, "top": body, "styles": {},
               "heading-level": 0, "toc": None, "footnotes": {}}

    # Go!
    for children in domtree:
        if children.tagname == "title":
            print "global title:", children.astext()
        else:
            find_convert(children, context)

    # Finish the work
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


