.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
   
   Authors: Hervé Cauwelier <herve@itaapy.com>
            Luis Belmar-Letelier <luis@itaapy.com>
   
   This file is part of Lpod (see: http://lpod-project.org).
   Lpod is free software; you can redistribute it and/or modify it under
   the terms of either:
   
   a) the GNU General Public License as published by the Free Software
      Foundation, either version 3 of the License, or (at your option)
      any later version.
      Lpod is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.
      You should have received a copy of the GNU General Public License
      along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
   
   b) the Apache License, Version 2.0 (the "License");
      you may not use this file except in compliance with the License.
      You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0

#########
Cookbook
#########

.. contents::

Basic text
=============

- Create a text document::

    # Import from lpod
    from lpod.document import odf_new_document_from_type
    from lpod.document import odf_create_paragraph, odf_create_heading

    document = odf_new_document_from_type('text')

- Contents go into the body::

    body = document.get_body()

- Add a table of content (TOC)::

    toc = odf_create_toc()
    body.append_element(toc)

- Add a paragraph::

    paragraph = odf_create_paragraph(u'lpOD generated Document')
    body.append_element(paragraph)

- Add an heading of level 1::

    heading = odf_create_heading(1, text=u'Lists')
    body.append_element(heading)

- Add a list::

    my_list = odf_create_list([u'chocolat', u'café'])

- Add an item with a sublist::

    item = odf_create_list_item(u'Du thé')
    item.append_element(odf_create_list([u'thé vert', u'thé rouge']))
    my_list.append_item(item)

- Insert item by position::

    my_list.insert_item(u'Chicorée', position=1)

- Insert item by relative position::

    the = my_list.get_item_by_content(u'thé')
    my_list.insert_item(u'Chicorée', before=the)
    my_list.insert_item(u'Chicorée', after=the)

    body.append_element(my_list)

- Add a footnote::

    body.append_element(odf_create_heading(1, u"Footnotes"))
    paragraph = odf_create_paragraph(u'A paragraph with a footnote '
                                          u'about references in it.')
    note = odf_create_note(note_id='note1', citation=u"1",
                           body=u'Author, A. (2007). "How to cite references", '
                                u'New York: McGraw-Hill.')
    paragraph.insert_note(note, after=u"graph")
    body.append_element(paragraph)

- Add an annotation::

    body.append_element(odf_create_heading(1, u"Annotations"))
    paragraph = odf_create_paragraph(u"A paragraph with an annotation "
                                     u"in the middle.")
    annotation = odf_create_annotation(u"It's so easy!", creator=u"Luis")
    paragraph.insert_annotation(annotation, after=u"annotation")
    body.append_element(paragraph)

- Add a table::

    body.append_element(odf_create_heading(1, u"Tables"))
    body.append_element(odf_create_paragraph(u"A table:"))
    table = odf_create_table(u"Table 1", width=3, height=3)
    body.append_element(table)

- Applying styles::

    body.append_element(odf_create_heading(1, u"Applying Styles"))

- Copying a style from another document::

    lpod_styles = odf_get_document('../../python/templates/lpod_styles.odt')
    highlight = lpod_styles.get_style('text', u"Yellow Highlight",
                                      display_name=True)
    assert highlight is not None
    document.insert_style(highlight)

- Apply this style to a pattern::

    paragraph = odf_create_paragraph(u'Highlighting the word "highlight".')
    paragraph.set_span(highlight, u"highlight")
    body.append_element(paragraph)

- Save::

    document.save('text.odt', pretty=True)


Create a ods from multiples csv files
=======================================

- Create a spreadsheet document::

   # Import from lpod
   from lpod.document import odf_new_document_from_type
   from lpod.table import import_from_csv

   document = odf_new_document_from_type('spreadsheet')
   body = document.get_body()

- Transform each CSV into a matrix in memory::

   for id, filename in enumerate(glob('./files/*.csv')):
       table = import_from_csv(filename, u'Table %s' % (id + 1))

- Serialize the matrix into ODF XML::

       body.append_element(table.to_odf_element())

- Save::

   document.save('spreadsheet.ods', pretty=True)


Slide Show with ODP
=====================

- Creation of the document::

    document = odf_new_document_from_type('presentation')
    body = document.get_body()

- Change the default graphic fill color::

    standard = document.get_style('graphic', u"standard")
    standard.set_style_properties({'draw:fill-color': '#ffffff'})

- Work on pages and add textframes::

    page = odf_create_draw_page('page1', name=u"Page 1")
    body.append_element(page)

- Text Frame

- Set the frame color::

    colored = odf_create_style('graphic', name=u"colored",
                               display_name=u"Colored", parent="standard")
    colored.set_style_properties({'draw:fill-color': "#ad7fa8"},
                                     area='graphic')
    colored.set_style_properties(color="#ffffff", area='text')
    document.insert_style(colored)

- A paragraph style with big font::

    big = odf_create_style('paragraph', u"big", area='paragraph',
        align="center")
    big.set_style_properties(area='text', size="32pt")
    document.insert_style(big, automatic=True)

- Set a text frame::

    text_frame = odf_create_text_frame([u"lpOD", u"Presentation",
        u"Cookbook"], size=('7cm', '5cm'), position=('11cm', '8cm'),
        style=u"colored", text_style=u"big")
    page.append_element(text_frame)

- Image Frame

- Start a new page::

    page2 = odf_create_draw_page(u"page2")
    body.append_element(page2)

- Embed an image from a file name::

    local_uri = document.add_file(u'images/zoé.jpg')

- Add image frame::

    image_frame = odf_create_image_frame(local_uri, size=('60mm', '45mm'),
                                         position=('4.5cm', '7cm'))
    page2.append_element(image_frame)

- Some text side by side::

    list = odf_create_list([u"Item 1", u"Item 2", u"Item 3"])
    text_frame = odf_create_text_frame(list, size=('7cm', '2.5cm'),
                                       position=('12.5cm', '7cm'),
                                       style=u"colored")
    page2.append_element(text_frame)

- Shapes::

- Add a last page::

    page3 = odf_create_draw_page(u"page3")
    body.append_element(page3)

- Square::

    square = odf_create_rectangle(shape_id=u"square", size=('8cm', '8cm'),
                                  position=('17cm', '2.5cm'),
                                  style=u"colored")
    page3.append_element(square)

- Circle::

    circle = odf_create_ellipse(shape_id=u"circle", size=('8cm', '8cm'),
                                position=('2cm', '10cm'), style=u"colored")
    page3.append_element(circle)

- Line::

    line = odf_create_line(p1=('8cm', '5cm'), p2=('20cm', '17.5cm'))
    page3.append_element(line)

- Connector::

    connector = odf_create_connector(connected_shapes=(square, circle),
                                     glue_points=('1', '3'))

- Save::

    document.save('presentation.odp', pretty=True)


Styles
=======

Import from lpod::

   from lpod.document import odf_get_document odf_new_document_from_type

Creation of the document::

   document = odf_new_document_from_type('text')
   body = document.get_body()
   paragraph = odf_create_paragraph(text=u'lpOD generated Document '
                                          'with styled pages')

- Use **merge_styles_from** to copy default style from some document::

   doc_style = odf_get_document(u'my_ref_doc.odt')
   document.merge_styles_from(doc_style)


- Pages, header and footer::

   # Apply a named style to a page e.g. here 'first page style'
   paragraph.set_master_page_style(u'first page style')

   # to modify the footer and header we get the style
   first_page_style = document.get_style(u'first page style')

   # and we set the content to modify footer or header
   # this orverwrite every footer elements by a paragraphe.
   first_page_style.set_footer(u'lpOD project')

   # instade of using set_header we can just modify a part of it
   header = first_page_style.get_header()
   par = header.get_paragraph_by_content(u'Draft')
   par.set_text(u'Final Version')

Save::

   body.append_element(paragraph)
   document.save('styles_cookbook.odt', pretty=True)

Styles instropection
---------------------

- Copy default style from some document::

   >>> doc_style = odf_get_document(u'my_ref_doc.odt')
   >>> doc_style.show_styles(type='default')
   xxxx
   xxxx
   xxxx
   >>> doc_style.show_styles(type='named')
   xxxx
   xxxx
   xxxx

Styles instropection cli
-------------------------

- **lpod-style** a command line interface to manipulate styles::

   $ lpod-style --show
   $ lpod-style --remove-all-styles a.odf
   $ lpod-style --remove-unused-styles a.odf
   $ lpod-style --apply-styles-from=s.odt a.odf


