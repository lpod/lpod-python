.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: Hervé Cauwelier <herve@itaapy.com>
            Luis Belmar-Letelier <luis@itaapy.com>
            David Versmisse <david.versmisse@itaapy.com>

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

########
Cookbook
########

.. contents::

Navigation
==========

- Open an existing document::

  >>> from lpod.document import odf_get_document
  >>> document = odf_get_document('http://example.com/odf/cookbook')

- Access the content of the document::

  >>> body = document.get_body()

- A list of all elements of a kind is accessible through "get_*_list"::

  >>> body.get_heading_list()
  [<lpod.heading.odf_heading object at 0x22a0090>, <lpod.heading.odf_head...
  >>> body.get_paragraph_list()
  [<lpod.paragraph.odf_paragraph object at 0x22a04d0>, <lpod.paragraph.od...
  >>> body.get_list_list()
  [<lpod.list.odf_list object at 0x7f2f6ce2c5d0>, <lpod.list.odf_list obj...
  >>> body.get_table_list()
  [<lpod.element.odf_element object at 0x7f2f6ce2c850>, <lpod.element.odf...
  >>> body.get_draw_page_list()
  [<lpod.element.odf_draw_page object at 0x7f23ba8e0c2f>, <lpod.element.od...

- The list can be more finely grained::

  >>> body.get_heading_list(level=1)
  [<lpod.heading.odf_heading object at 0x7f2f6ce2cb10>]
  >>> body.get_paragraph_list(regex=u"[Ll]ist")
  [<lpod.paragraph.odf_paragraph object at 0x7f2f6ce2c6d0>, <lpod.paragrap...

- No result returns an empty list::

  >>> body.get_table_list(style=u"Invoice")
  []

- To access a single element by name, position or a regular expression on the
  content, use "get_*_by_<criteria>"::

  >>> body.get_heading_by_position(1)
  <lpod.heading.odf_heading object at 0x7f2f6ce2cc50>
  >>> body.get_paragraph_by_content(u"highlight")
  <lpod.paragraph.odf_paragraph object at 0x7f2f6ce2cd90>
  >>> body.get_table_by_name(u"Feuille1")
  <lpod.element.odf_element object at 0x7f2f6ce2c850>

- No result returns None::

  >>> print body.get_draw_page_by_name(u"Page1")
  None

- Any element is a context for navigating inside it::

  >>> l = body.get_list_by_position(1)
  >>> print l
  <lpod.list.odf_list object at 0x7f2f6ce2c890> "text:list"
  >>> p = l.get_paragraph_by_position(1)
  >>> print p
  <lpod.paragraph.odf_paragraph object at 0x7f2f6ce2ca10> "text:p"
  >>> a = p.get_link_by_path(u"example.com")
  >>> print a
  <lpod.element.odf_element object at 0x7f2f6ce2cb10> "text:a"
  >>> a.serialize()
  <text:a xlink:href="http://example.com">Example</a>


Metadata
========

- Open an existing document::

  >>> from lpod.document import odf_get_document
  >>> document = odf_get_document('http://example.com/odf/cookbook')

- Access the metadata part::

  >>> meta = document.get_meta()

You then get the list of getters and setters.

- Most of them return unicode::

  >>> meta.get_title()
  Example Document for the Cookbook
  >>> meta.get_description()
  >>> meta.get_subject()
  >>> meta.get_language()
  >>> meta.get_initial_creator()
  >>> meta.get_keyword()
  >>> meta.get_generator()
  LpOD Project v0.7-67-g24c08f4

- They accept unicode in return::

  >>> meta.set_title(u"First Example of a Long Series")

- Some return int::

  >>> meta.get_editing_cycles()
  2

- They accept int in return::

  >>> meta.set_editing_cycles(3)

- Some return dict::

  >>> meta.get_statistic()
  {'meta:word-count': 63, 'meta:image-count': 0, 'meta:object-count': 0,
  'meta:page-count': 3, 'meta:character-count': 273, 'meta:paragraph-count':
  25, 'meta:table-count': 2}

- They accept dict of the same form::

  >>> stat = meta.get_statistic()
  # ... update stat
  >>> meta.set_statistic(stat)

- Some return datetime object::

  >>> meta.get_modification_date()
  datetime.datetime(2009, 8, 25, 15, 40, 28)
  >>> meta.get_creation_date()
  datetime.datetime(2009, 7, 11, 15, 21, 27)

- So they need datetime object in return::

  >>> from datetime import datetime
  >>> metadata.set_modification_date(datetime.now())

- There is an helper for manipulating dates::

  >>> from lpod.datatype import DateTime
  >>> metadata.set_modification_date(DateTime.decode('2009-11-17T12:02:49'))

- Other return timedelta object::

  >>> meta.get_editing_duration()
  >>> datetime.timedelta(0, 174)

- So they need timedelta object in return::
  >>> from datetime import timedelta
  >>> meta.set_editing_duration(timedelta(seconds=182))

- There is an helper for this too::

  >>> from lpod.datatype import Duration
  >>> meta.set_editing_duration(Duration.encode('PT00H03M02S')

- There are finally user-defined metadata (generally unused)::

  >>> meta.get_user_defined_metadata()::
  {}

- Free for you to store str, unicode, bool, int, float, Decimal, date,
  datetime, timedelta::

  >>> meta.set_user_defined_metadata('lpod-version', 'v0.7-67-g24c08f4')
  >>> meta.get_user_defined_metadata()
  {u'lpod-version': u'v0.7-67-g24c08f4'}

Strings are always decoded as unicode, numeric values are always decoded as
Decimal.


Basic text
==========

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

' And Auto fill the TOC::

    toc.auto_fill(document)

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

- Add a transition::

    page.set_transition("fade", "fadeOverColor")

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

Use **merge_styles_from** to copy default style from some document::

   doc_style = odf_get_document(u'my_ref_doc.odt')
   document.merge_styles_from(doc_style)

Automatic style to set the master page::

    style = odf_create_style('paragraph', master_page=u"First_20_Page")
    document.insert_style(style, automatic=True)

The first paragraph will set the page::

    paragraph = odf_create_paragraph(text=u"lpOD generated Document "
            u"with styled pages", style=style.get_style_name())
    body.append_element(paragraph)

To modify the footer and header we get the style::

   first_page_style = document.get_style(u'first page style')

Overwrite the footer::

   first_page_style.set_footer(u'lpOD project')

Complement the header::

   header = first_page_style.get_header()
   par = header.get_paragraph_by_content(u'Draft')
   par.set_text(u'Final Version')

Save::

    filename = 'styles.odt'
    document.save(filename, pretty=True)
    print 'Document "%s" generated.' % filename

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


