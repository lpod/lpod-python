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

- create an ods from multiples csv files::

   # Import from the Standard Library
   from glob import glob

   # Import from lpod
   from lpod.document import odf_new_document_from_type
   from lpod.table import import_from_csv

   # Get elements
   document = odf_new_document_from_type('spreadsheet')
   body = document.get_body()

   # Delete the 3 default sheets
   body.clear()

   for id, filename in enumerate(glob('./files/*.csv')):
       table = import_from_csv(filename, u'Table %s' % (id + 1))
       # Table is represented as a matrix in memory,
       # so ask to reformat it to XML
       body.append_element(table.to_odf_element())

   # Save
   document.save('spreadsheet.ods', pretty=True)


Slide Show with ODP
=====================

- Create a presentation with slides::

   # Import from lpod
   from lpod.document import odf_new_document_from_type
   from lpod.paragraph import odf_create_paragraph
   from lpod.frame import odf_create_text_frame, odf_create_image_frame
   from lpod.draw_page import odf_create_draw_page

   # Creation of the document
   document = odf_new_document_from_type('presentation')
   content = document.get_xmlpart('content')
   body = content.get_body()

Work on pages and add textframes
---------------------------------
::

   # The document already contains a page
   page = content.get_draw_page_by_position(1)

   # Add a frame with a text box
   text_element = odf_create_paragraph(u'First Slide')
   draw_textframe1 = odf_create_text_frame(text_element,
                                           size=('5cm', '100mm'),
                                           position=('3.5cm', '30.6mm'))
   page.append_element(draw_textframe1)

   # If first arg is text a paragraph is created
   draw_textframe2 = odf_create_text_frame(u"Noël",
                                           size=('5cm', '100mm'),
                                           position=('20cm', '14cm'))

Save::

   page.append_element(draw_textframe2)
   document.save('presentation.odp', pretty=True)


Add images frames
------------------

Add an image frame from a file name::

   local_uri = document.add_file(u'images/zoé.jpg')
   draw_imageframe1 = odf_create_image_frame(local_uri,
                                             size=('6cm', '24.2mm'),
                                             position=('1cm', '10cm'))
   page.append_element(draw_imageframe1)

Add an image frame from a file descriptor::

   PPC = 72 * 2.54

   # helper function
   def get_thumbnail_file(filename):
       """ From a filename return a filedescriptor and an image size tuple"""
       from PIL import Image
       from cStringIO import StringIO

       im = Image.open(filename)
       im.thumbnail((300, 400), Image.ANTIALIAS)
       filedescriptor = StringIO()
       im.save(filedescriptor, 'JPEG', quality=80)
       filedescriptor.seek(0)
       return filedescriptor, (im.size[0] / PPC), (im.size[1] / PPC)

   # use
   filedescriptor, width, height = get_thumbnail_file(u'images/zoé.jpg')
   local_uri = document.add_file(filedescriptor)
   draw_imageframe2 = odf_create_image_frame(local_uri,
                                             size=('%scm' % width,
                                                   '%scm' % height),
                                             position=('12cm', '2cm'))

Save::

   page.append_element(draw_imageframe2)

   # Add the page to the body
   body.append_element(page)


Get a new page, page2 copy of page1::

   page2 = page.clone()
   page2.set_page_name(u'Page 2')
   paragraph = content.get_paragraph_by_content(u'First', context=page2)
   paragraph.set_text(u'Second Slide')


Build a new page from scratch::

   page3 = odf_create_draw_page(u"Page 3")
   frame = content.get_frame_by_content(u"Second").clone()
   frame.set_size(('10cm', '100mm'))
   frame.set_position(('100mm', '10cm'))

   # A shortcut to hit embedded paragraph
   frame.set_text_content(u"Third Slide")

   page3.append_element(frame)
   body.append_element(page3)

Slide transition
----------------
::

   page2.add_transition('fade')
   body.append_element(page2)

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


