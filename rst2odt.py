#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from sys import stdout

# Import from docutils
from docutils import nodes
from docutils.core import publish_doctree

# Import from imaging
from PIL import Image

# Import from lpod
from document import odf_new_document
from frame import odf_create_image_frame, odf_create_text_frame
from heading import odf_create_heading
from link import odf_create_link
from list import odf_create_list, odf_create_list_item
from note import odf_create_note
from paragraph import odf_create_paragraph, odf_create_line_break
from paragraph import odf_create_spaces
from span import odf_create_span
from scriptutils import printwarn
from style import odf_create_style
from table import odf_create_cell, odf_create_table, odf_create_row
from table import odf_create_column, odf_create_header_rows
from toc import odf_create_toc
from utils import DPI




def push_convert_pop(node, element, context):
    old_top = context['top']
    context['top'] = element
    for child in node:
        convert_node(child, context)
    context['top'] = old_top


def convert_text(node, context):
    context['top'].append(node.astext())



def convert_section(node, context):
    # Inc the heading level
    context['heading_level'] += 1

    # Reset the top to body
    context['top'] = context['body']

    # Convert
    for child in node:
        convert_node(child, context)

    # Restore the heading level
    context['heading_level'] -= 1



def convert_title(node, context):
    level = context['heading_level']
    if level == 0:
        # The document did not start with a section
        level = 1
    heading = odf_create_heading(level, style='Heading_20_%s' % level)
    context['top'].append(heading)
    push_convert_pop(node, heading, context)



def convert_paragraph(node, context):
    # Search for a default style
    style = context['styles'].get('paragraph')
    paragraph = odf_create_paragraph(style=style)
    context['top'].append(paragraph)
    push_convert_pop(node, paragraph, context)



def convert_list(node, context, list_type):
    # Reuse template styles
    if list_type == "enumerated":
        style_name = "Numbering_20_1"
    else:
        style_name = "List_20_1"

    odf_list = odf_create_list(style=style_name)
    context['top'].append(odf_list)

    # Save the current top
    old_top = context['top']

    for item in node:
        if item.tagname != "list_item":
            printwarn("node not supported: %s" % item.tagname)
            continue
        # Create a new item
        odf_item = odf_create_list_item()
        odf_list.append(odf_item)
        # A new top
        context['top'] = odf_item
        for child in item:
            convert_node(child, context)

    # And restore the top
    context['top'] = old_top



def convert_list_enumerated(node, context):
    return convert_list(node, context, "enumerated")



def convert_list_bullet(node, context):
    return convert_list(node, context, "bullet")



def convert_topic(node, context):
    # Reset the top to body
    context['top'] = context['body']

    # Yet an other TOC ?
    if context['skip_toc']:
        return
    if context['toc'] is not None:
        printwarn("a TOC is already inserted")
        return
    title = node.next_node(condition=nodes.title).astext()
    toc = odf_create_toc(title=title)
    context['body'].append(toc)
    context['toc'] = toc



def convert_footnote(node, context):
    # XXX ids is a list ??
    refid = node.get("ids")[0]

    # Find the footnote
    footnotes = context['footnotes']
    if refid not in footnotes:
        printwarn('unknown footnote "%s"' % refid)
        return
    footnote_body = footnotes[refid].get_element("text:note-body")

    # Save the current top
    old_top = context['top']

    # Fill the note
    context['top'] = footnote_body
    for child in node:
        # We skip the label (already added)
        if child.tagname == "label":
            continue
        convert_node(child, context)

    # And restore the top
    context['top'] = old_top



def convert_footnote_reference(node, context):
    refid = node.get("refid")
    citation = node.astext()

    footnote = odf_create_note(note_id=refid, citation=citation)
    context['top'].append(footnote)

    context['footnotes'][refid] = footnote



def _convert_style_like(node, context, style_name):
    # Create the span
    span = odf_create_span(style=style_name)
    context['top'].append(span)
    push_convert_pop(node, span, context)



def _get_emphasis_style(context):
    styles = context['styles']
    emphasis_style = styles.get('emphasis')
    if emphasis_style is not None:
        return emphasis_style
    emphasis_style = odf_create_style("text", italic=True)
    context['doc'].insert_style(emphasis_style, automatic=True)
    styles['emphasis'] = emphasis_style
    return emphasis_style



def convert_emphasis(node, context):
    emphasis_style = _get_emphasis_style(context).get_name()
    # Convert
    _convert_style_like(node, context, emphasis_style)



def _get_strong_style(context):
    styles = context['styles']
    strong_style = styles.get('strong')
    if strong_style is not None:
        return strong_style
    strong_style = odf_create_style("text", bold=True)
    context['doc'].insert_style(strong_style, automatic=True)
    styles['strong'] = strong_style
    return strong_style



def convert_strong(node, context):
    strong_style = _get_strong_style(context).get_name()
    # Convert
    _convert_style_like(node, context, strong_style)



def convert_literal(node, context):
    # Convert
    _convert_style_like(node, context, "Example")



def convert_literal_block(node, context):
    paragraph = odf_create_paragraph(style="Preformatted_20_Text")
    context['top'].append(paragraph)

    # Convert
    for child in node:
        # Only text
        if child.tagname != "#text":
            printwarn('node "%s" not supported in literal block' % (
                child.tagname))
            continue
        text = child.astext()

        tmp = []
        spaces = 0
        for c in text:
            if c == '\n':
                if tmp:
                    tmp = u"".join(tmp)
                    paragraph.append(tmp)
                    tmp = []
                spaces = 0
                paragraph.append(odf_create_line_break())
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
                        paragraph.append(tmp)
                        tmp = []
                    paragraph.append(' ')
                    paragraph.append(
                              odf_create_spaces(spaces - 1))
                    spaces = 0
                elif spaces == 1:
                    tmp.append(' ')
                    spaces = 0
                tmp.append(c)
        if tmp:
            tmp = u"".join(tmp)
            paragraph.append(tmp)



def convert_reference(node, context):
    refuri = node.get("refuri")
    text = node.astext()

    link = odf_create_link(refuri)
    link.set_text(text)
    context['top'].append(link)



def _get_term_style(context):
    styles = context['styles']
    term_style = styles.get('term')
    if term_style is not None:
        return term_style
    # Reuse template style if any
    doc = context['doc']
    term_style = doc.get_style('paragraph',
            u"Definition_20_List_20_Term")
    if term_style is None:
        # Create default one
        term_style = odf_create_style('paragraph',
                name=u"Definition_20_List_20_Term",
                display_name=u"Definition List Term", parent="Standard",
                font_weight=u"bold", area='text')
        doc.insert_style(term_style, automatic=False)
    styles['term'] = term_style
    return term_style



def _get_definition_style(context):
    styles = context['styles']
    definition_style = styles.get('definition')
    if definition_style is not None:
        return definition_style
    # Reuse template style if any
    doc = context['doc']
    definition_style = doc.get_style('paragraph',
            u"Definition_20_List_20_Definition")
    if definition_style is None:
        # Create default one
        definition_style = odf_create_style('paragraph',
                name=u"Definition_20_List_20_Definition",
                display_name=u"Definition List Definition",
                parent="Standard", margin_left=u"0.5cm",
                margin_right=u"0cm", text_indent=u"0cm",
                **{'style:auto-text-indent': u"false"})
        doc.insert_style(definition_style, automatic=False)
    styles['definition'] = definition_style
    return definition_style



def convert_definition_list(node, context):
    """Convert a list of term/definition pairs to styled paragraphs.

    The "Definition List Term" style is looked for term paragraphs, and the
    "Definition List Definition" style is looked for definition paragraphs.
    """
    styles = context['styles']
    term_style = _get_term_style(context).get_name()
    definition_style = _get_definition_style(context).get_name()

    for item in node:
        if item.tagname != "definition_list_item":
            printwarn('node "%s" not supported in definition_list' % (
                item.tagname))
            continue
        for child in item:
            tagname = child.tagname
            if tagname == "term":
                paragraph = odf_create_paragraph(style=term_style)
                context['top'].append(paragraph)
                push_convert_pop(child, paragraph, context)
            elif tagname == "definition":
                # Push a style on the stack for next paragraphs to use
                styles['paragraph'] = definition_style
                for subchildren in child:
                    convert_node(subchildren, context)
                # Pop the paragraph style (may already be popped)
                styles.pop('paragraph', None)
            else:
                printwarn('node "%s" not supported in definition_list_item' %
                        tagname)



def convert_block_quote(node, context):
    # TODO Add the style
    for child in node:
        convert_node(child, context)



def _get_caption_style(context):
    styles = context['styles']
    caption_style = styles.get('caption')
    if caption_style is not None:
        return caption_style
    caption_style = odf_create_style('graphic', parent=u"Frame",
            **{'style:wrap': u"none", 'style:vertical-pos': u"top",
                'style:vertical-rel': u"paragraph-content",
                'style:horizontal-pos': u"center",
                'style:horizontal-rel': u"paragraph-content",
                'fo:padding': u"0.25cm", 'fo:border': u"0cm solid #000000"})
    context['doc'].insert_style(caption_style, automatic=True)
    styles['caption'] = caption_style
    return caption_style



def _get_image_style(context):
    styles = context['styles']
    image_style = styles.get('image')
    if image_style is not None:
        return image_style
    image_style = odf_create_style('graphic', parent="Graphics",
            **{'style:horizontal-pos': u"center",
                'style:horizontal-rel': u"paragraph"})
    context['doc'].insert_style(image_style, automatic=True)
    styles['image'] = image_style
    return image_style



def _add_image(image, caption, context, width=None, height=None):
    # Load the image to find its size
    encoding = stdout.encoding if stdout.encoding is not None else "utf-8"
    try:
        image_file = open(image.encode(encoding), 'rb')
        image_object = Image.open(image_file)
    except (UnicodeEncodeError, IOError, OverflowError), e:
        printwarn('unable to insert the image "%s": %s' % (image, e))
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
                height = int(height.replace('px', ''))
            except ValueError:
                raise NotImplementedError, 'only pixel units supported'
        else:
            height = int(width / (float(size[0]) / float(size[1])))
    elif height:
        try:
            height = int(height.replace('px', ''))
        except ValueError:
            raise NotImplementedError, 'only pixel units supported'
        width = int(height * (float(size[0]) / float(size[1])))
    else:
        # If the information is not present, we assume a width of 640 px
        width = 640
        height = int(width / (float(size[0]) / float(size[1])))
    size = ( "%sin" % (width / DPI),
             "%sin" % (height / DPI) )

    # Add the image
    local_uri = context['doc'].add_file(image)

    # Frame style for the caption frame
    caption_style = _get_caption_style(context).get_name()
    # Frame style for the image frame
    image_style = _get_image_style(context).get_name()

    # In text application, image must be inserted in a paragraph
    if context['top'].get_tag() == "office:text":
        container = odf_create_paragraph()
        context['top'].append(container)
    else:
        container = context['top']

    if caption:
        paragraph = odf_create_paragraph()
        image_frame = odf_create_image_frame(local_uri, size=size,
                style=image_style)
        paragraph.append(image_frame)
        paragraph.append(caption)
        # A new frame, we fix only the width
        text_frame = odf_create_text_frame(paragraph, size=(size[0], None),
                style=caption_style)
        container.append(text_frame)
    else:
        image_frame = odf_create_image_frame(local_uri, size=size,
                style=image_style)
        container.append(image_frame)



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
                printwarn("unexpected duplicate image in a figure")
                continue
            image = child.get("uri")
            width = child.get('width')
            height = child.get('height')
        elif tagname == "caption":
            if caption is not None:
                printwarn("unexpected duplicate caption in a figure")
                continue
            caption = child.astext()

    _add_image(image, caption, context, width=width, height=height)



def _convert_table_rows(container, node, context, cell_style=None):
    for row in node:
        if row.tagname != "row":
            printwarn('node "%s" not supported in thead/tbody' % row.tagname)
            continue

        odf_row = odf_create_row()
        container.append(odf_row)

        for entry in row:
            if entry.tagname != "entry":
                printwarn('node "%s" not supported in row' % entry.tagname)
                continue

            # Create a new odf_cell
            odf_cell = odf_create_cell(cell_type="string", style=cell_style)
            odf_row.append(odf_cell)

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

            push_convert_pop(entry, odf_cell, context)



def _get_cell_style(context):
    styles = context['styles']
    cell_style = styles.get('cell')
    if cell_style is not None:
        return cell_style
    # Give borders to cells
    cell_style = odf_create_style('table-cell', u"odf_table.A1",
            padding=u"0.049cm", border=u"0.002cm solid #000000")
    context['doc'].insert_style(cell_style, automatic=True)
    styles['cell'] = cell_style
    return cell_style



def convert_table(node, context):
    cell_style = _get_cell_style(context).get_name()

    for tgroup in node:
        if tgroup.tagname != "tgroup":
            printwarn('node "%s" not supported in table' % tgroup.tagname)
            continue
        columns_number = 0
        odf_table = None
        for child in tgroup:
            tagname = child.tagname
            if tagname == "thead" or tagname == "tbody":
                # Create a new table with the info columns_number
                if odf_table is None:
                    context['tables_number'] += 1
                    # TODO Make it possible directly with odf_create_table
                    odf_table = odf_create_table(name="table%d" %
                                                 context['tables_number'])
                    columns = odf_create_column(repeated=columns_number)
                    odf_table.append(columns)
                # Convert!
                if tagname == "thead":
                    header = odf_create_header_rows()
                    odf_table.append(header)

                    _convert_table_rows(header, child, context,
                            cell_style=cell_style)
                else:
                    _convert_table_rows(odf_table, child, context,
                            cell_style=cell_style)
            elif tagname == "colspec":
                columns_number += 1
            else:
                printwarn('node "%s" not supported in tgroup' % (
                    child.tagname))
                continue

        context['top'].append(odf_table)



__convert_methods = {
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
        'subtitle': convert_title,
        'topic': convert_topic
}

def register_convert_method(name, method):
    __convert_methods[name] = method



def convert_node(node, context):
    tagname = node.tagname
    # From the context
    convert_method = context.get('convert_' + tagname)
    if convert_method is None:
        # Default method
        convert_method = __convert_methods.get(tagname)
    if convert_method is not None:
        return convert_method(node, context)
    message = "node not supported: %s" % tagname
    if context['strict']:
        raise ValueError, message
    printwarn(message)



def make_context(document, body=None, top=None, **kwargs):
    if body is None:
        body = document.get_body()
    if top is None:
        top = body
    context = {
        'doc': document,
        'body': body,
        'top': body,
        'styles': {},
        'heading_level': 1,
        'toc': None,
        'skip_toc': False,
        'footnotes': {},
        'tables_number': 0,
        'strict': False}
    context.update(kwargs)
    return context



def convert(document, doctree, context=None):
    """Convert a reStructuredText source into an existing document.

    If the document contains its own TOC, you can ignore others with
    "skip_toc".

    Arguments:

        document -- odf_document

        doctree -- docutils node (reST str accepted)

        heading_level -- int

        skip_toc -- bool

    Return: odf_document
    """
    # Init a context
    if context is None:
        context = make_context(document)

    # Go!
    if isinstance(doctree, str):
        doctree = publish_doctree(doctree)
    for child in doctree:
        convert_node(child, context)

    # Finish the work
    toc = context['toc']
    if toc is not None:
        toc.fill()

    return document



def rst2odt(rst_body, template=None, heading_level=1):
    """Convert a reStructuredText source to a new document.

    The template is a document to reuse instead of the default lpOD template.

    Arguments:

        rst_body -- reST str (docutils node accepted)

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
        document = odf_new_document("text")

    context = make_context(document, heading_level=heading_level)
    return convert(document, rst_body, context=context)
