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

# Import from the Standard Library
from sys import stdout, stderr

# Import from docutils
from docutils.core import publish_doctree

# Import from imaging
from PIL import Image

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.frame import odf_create_image_frame, odf_create_text_frame
from lpod.heading import odf_create_heading
from lpod.link import odf_create_link
from lpod.list import odf_create_list, odf_create_list_item
from lpod.note import odf_create_note
from lpod.paragraph import odf_create_paragraph, odf_create_line_break
from lpod.paragraph import odf_create_undividable_space
from lpod.span import odf_create_span
from lpod.style import odf_create_style
from lpod.table import odf_create_cell, odf_create_table, odf_create_row
from lpod.table import odf_create_column, odf_create_header_rows
from lpod.toc import odf_create_toc
from lpod.vfs import vfs, Error


DPI = 72


def warn(message):
    print >> stderr, "Warning:", message



def convert_text(node, context):
    context["top"].append_element(node.astext())



def convert_section(node, context):
    # Inc the heading level
    context["heading-level"] += 1

    # Reset the top to body
    context["top"] = context["body"]

    # Convert
    for child in node:
        convert_node(child, context)

    # Restore the heading level
    context["heading-level"] -= 1



def convert_title(node, context):
    level = context["heading-level"]
    if level == 0:
        # The document did not start with a section
        level = 1
    heading = odf_create_heading(level, node.astext(),
            style='Heading_20_%s' % level)
    context["body"].append_element(heading)



def convert_paragraph(node, context):
    paragraph = odf_create_paragraph()
    context["top"].append_element(paragraph)

    # Save the current top
    old_top = context["top"]

    # Convert
    context["top"] = paragraph
    for child in node:
        convert_node(child, context)

    # And restore the top
    context["top"] = old_top



def convert_list(node, context, list_type):
    # Predefined styles
    if list_type == "enumerated":
        style_name = "Numbering_20_1"
    else:
        style_name = "List_20_1"

    odf_list = odf_create_list(style=style_name)
    context["top"].append_element(odf_list)

    # Save the current top
    old_top = context["top"]

    for item in node:

        if item.tagname != "list_item":
            warn("node not supported: %s" % item.tagname)
            continue

        # Create a new item
        odf_item = odf_create_list_item()
        odf_list.append_element(odf_item)

        # A new top
        context["top"] = odf_item

        for child in item:
            convert_node(child, context)

    # And restore the top
    context["top"] = old_top



def convert_list_enumerated(node, context):
    return convert_list(node, context, "enumerated")



def convert_list_bullet(node, context):
    return convert_list(node, context, "bullet")



def convert_topic(node, context):
    # Reset the top to body
    context["top"] = context["body"]

    # Yet an other TOC ?
    if context["skip_toc"]:
        return
    if context["toc"] is not None:
        warn("a TOC is already inserted")
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
        warn('unknown footnote "%s"' % refid)
        return
    footnote_body = footnotes[refid].get_element("text:note-body")

    # Save the current top
    old_top = context["top"]

    # Fill the note
    context["top"] = footnote_body
    for child in node:
        # We skip the label (already added)
        if child.tagname == "label":
            continue
        convert_node(child, context)

    # And restore the top
    context["top"] = old_top



def convert_footnote_reference(node, context):
    refid = node.get("refid")
    citation = node.astext()

    footnote = odf_create_note(note_id=refid, citation=citation)
    context["top"].append_element(footnote)

    context["footnotes"][refid] = footnote



def _convert_style_like(node, context, style_name):
    # Create the span
    span = odf_create_span(style=style_name)
    context["top"].append_element(span)

    # Save the current top
    old_top = context["top"]

    # Convert
    context["top"] = span
    for child in node:
        convert_node(child, context)

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
    _convert_style_like(node, context, emphasis.get_style_name())



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
    _convert_style_like(node, context, strong.get_style_name())



def convert_literal(node, context):
    # Convert
    _convert_style_like(node, context, "Example")



def convert_literal_block(node, context):
    paragraph = odf_create_paragraph(style="Preformatted_20_Text")
    context["top"].append_element(paragraph)

    # Convert
    for child in node:
        # Only text
        if child.tagname != "#text":
            warn('node "%s" not supported in literal block' % child.tagname)
            continue
        text = child.astext()

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
            warn('node "%s" not supported in definition_list' % item.tagname)
            continue

        for child in item:
            tagname = child.tagname
            if tagname == "term":
                paragraph = odf_create_paragraph(text=child.astext())
                context["top"].append_element(paragraph)
            elif tagname == "definition":
                for subchildren in child:
                    convert_node(subchildren, context)
            else:
                warn('node "%s" not supported in definition_list_item' %
                        item.tagname)



def convert_block_quote(node, context):
    # TODO Add the style
    for child in node:
        convert_node(child, context)



def _add_image(image, caption, context, width=None, height=None):
    # Load the image to find its size
    encoding = stdout.encoding if stdout.encoding is not None else "utf-8"
    try:
        image_file = vfs.open(image.encode(encoding))
        image_object = Image.open(image_file)
    except (Error, UnicodeEncodeError, IOError, OverflowError), e:
        warn('unable to insert the image "%s": %s' % (image, e))
        return
    size = image_object.size

    # Convert pixels to inches
    if width:
        try:
            width = int(width.replace('px', ''))
        except ValueError:
            raise NotImplementedError, 'only pixel units supported'
        if height:
            try:
                height = int(height)
            except ValueError:
                raise NotImplementedError, 'only pixel units supported'
        else:
            height = int(width / (float(size[0]) / float(size[1])))
        size = (width, height)
    elif height:
        try:
            height = int(height.replace('px', ''))
        except ValueError:
            raise NotImplementedError, 'only pixel units supported'
        width = int(height * (float(size[0]) / float(size[1])))
        size = (width, height)
    size = ("%sin" % (float(size[0]) / DPI), "%sin" % (float(size[1]) / DPI))

    # Add the image
    local_uri = context["doc"].add_file(image)

    # Frame style for the caption frame
    styles = context["styles"]
    caption_style = styles.get('caption_style')
    if caption_style is None:
        caption_style = odf_create_style("graphic", parent="Frame")
        caption_style.set_style_properties({'style:wrap': u"none",
            'style:vertical-pos': u"top",
            'style:vertical-rel': u"paragraph-content",
            'style:horizontal-pos': u"center",
            'style:horizontal-rel': u"paragraph-content",
            'fo:padding': u"0.25cm",
            'fo:border': u"0cm solid #000000"})
        context['doc'].insert_style(caption_style, automatic=True)
        styles['caption_style'] = caption_style

    # Frame style for the image frame
    image_style = styles.get('image_style')
    if image_style is None:
        image_style = odf_create_style('graphic', parent="Graphics")
        image_style.set_style_properties({'style:horizontal-pos': u"center",
            'style:horizontal-rel': u"paragraph"})
        context['doc'].insert_style(image_style, automatic=True)
        styles['image_style'] = image_style

    # In text application, image must be inserted in a paragraph
    if context["top"].get_tagname() == "office:text":
        container = odf_create_paragraph()
        context["top"].append_element(container)
    else:
        container = context["top"]

    if caption:
        paragraph = odf_create_paragraph()
        image_frame = odf_create_image_frame(local_uri, size=size,
                style=image_style.get_style_name())
        paragraph.append_element(image_frame)
        paragraph.append_element(caption)
        # A new frame, we fix only the width
        text_frame = odf_create_text_frame(paragraph, size=(size[0], None),
                style=caption_style.get_style_name())
        container.append_element(text_frame)
    else:
        image_frame = odf_create_image_frame(local_uri, size=size,
                style=image_style.get_style_name())
        container.append_element(image_frame)



def convert_image(node, context):
    image = node.get("uri")
    width = node.get('width')
    height = node.get('height')
    _add_image(image, None, context, width=width, height=height)



def convert_figure(node, context):
    image = None
    caption = None
    width = None
    height = None

    for child in node:
        tagname = child.tagname
        if tagname == "image":
            if image is not None:
                warn("unexpected image (just a image / figure) for a figure")
                continue
            image = child.get("uri")
            width = child.get('width')
            height = child.get('height')
        elif tagname == "caption":
            if caption is not None:
                warn("unexpected caption (just a caption / figure) for a "
                        "figure")
                continue
            caption = child.astext()

    _add_image(image, caption, context, width=width, height=height)



def _convert_table_rows(container, node, context):
    for row in node:
        if row.tagname != "row":
            warn('node "%s" not supported in thead/tbody' % row.tagname)
            continue

        odf_row = odf_create_row()
        container.append_element(odf_row)

        for entry in row:
            if entry.tagname != "entry":
                warn('node "%s" not supported in row' % entry.tagname)
                continue

            # Create a new odf_cell
            odf_cell = odf_create_cell(cell_type="string")
            odf_row.append_element(odf_cell)

            # XXX We don't add table:covered-table-cell !
            #     It's bad but OO can nevertheless load the file
            morecols = entry.get("morecols")
            if morecols is not None:
                morecols = int(morecols) + 1
                odf_cell.set_attribute('table:number-columns-spanned',
                                       str(morecols))
            morerows = entry.get("morerows")
            if morerows is not None:
                morerows = int(morerows) + 1
                odf_cell.set_attribute('table:number-rows-spanned',
                                       str(morerows))

            # Save the current top
            old_top = context["top"]

            # Convert
            context["top"] = odf_cell
            for child in entry:
                convert_node(child, context)

            # And restore the top
            context["top"] = old_top



def convert_table(node, context):
    for tgroup in node:
        if tgroup.tagname != "tgroup":
            warn('node "%s" not supported in table' % tgroup.tagname)
            continue

        columns_number = 0
        odf_table = None
        for child in tgroup:
            tagname = child.tagname

            if tagname == "thead" or tagname == "tbody":
                # Create a new table with the info columns_number
                if odf_table is None:
                    context["tables_number"] += 1
                    # TODO Make it possible directly with odf_create_table
                    odf_table = odf_create_table(name="table%d" %
                                                 context["tables_number"])
                    columns = odf_create_column(repeated=columns_number)
                    odf_table.append_element(columns)

                # Convert!
                if tagname == "thead":
                    header = odf_create_header_rows()
                    odf_table.append_element(header)

                    _convert_table_rows(header, child, context)
                else:
                    _convert_table_rows(odf_table, child, context)

            elif tagname == "colspec":
                columns_number += 1
            else:
                warn('node "%s" not supported in tgroup' % child.tagname)
                continue

        context["top"].append_element(odf_table)



convert_methods = {
        '#text': convert_text,
        'block_quote': convert_block_quote,
        'bullet_list': convert_list_bullet,
        'definition_list': convert_definition_list,
        'emphasis': convert_emphasis,
        'enumerated_list': convert_list_enumerated,
        'figure': convert_figure,
        'footnote': convert_footnote,
        'footnote_reference': convert_footnote_reference,
        'image': convert_image,
        'literal': convert_literal,
        'literal_block': convert_literal_block,
        'paragraph': convert_paragraph,
        'reference': convert_reference,
        'section': convert_section,
        'strong': convert_strong,
        'table': convert_table,
        'title': convert_title,
        'topic': convert_topic
}



def convert_node(node, context):
    tagname = node.tagname
    convert_method = convert_methods.get(tagname)
    if convert_method is not None:
        convert_method(node, context)
    else:
        warn("node not supported: %s" % tagname)



def convert(document, rst_body, heading_level=1, skip_toc=False):
    """Convert a reStructuredText source into an existing document.

    If the document contains its own TOC, you can ignore others with
    "skip_toc".

    Arguments:

        document -- odf_document

        rst_body -- str or docutils node

        heading_level -- int

        skip_toc -- bool

    Return: odf_document
    """
    # Init a context
    body = document.get_body()
    context = {"doc": document, "body": body, "top": body, "styles": {},
            "heading-level": heading_level, "toc": None,
            "skip_toc": skip_toc, "footnotes": {}, "tables_number": 0}

    # Go!
    if isinstance(rst_body, str):
        rst_body = publish_doctree(rst_body)
    for child in rst_body:
        convert_node(child, context)

    # Finish the work
    toc = context["toc"]
    if toc is not None:
        toc.toc_fill()

    return document



def rst2odt(rst_body, template=None):
    """Convert a reStructuredText source to a new document.

    The template is a document to reuse instead of the default lpOD template.

    Arguments:

        rst_body -- str or docutils node

        template -- odf_document

    Return: odf_document
    """
    # Use an existing document structure
    if template is not None:
        document = template.clone()
        # Clean the body
        document.get_body().clear()
    # Or create a new document
    else:
        document = odf_new_document_from_type("text")

    return convert(document, rst_body)
