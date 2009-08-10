#########
Cookbook
#########

Basic text
=============

- Create a text document with paragraph style field and metadata::

   # Import from lpod
   from lpod.document import odf_new_document_from_type
   from lpod.document import odf_create_paragraph, odf_create_heading

   # Creation of the document
   document = odf_new_document_from_type('text')
   body = document.get_body()

   # Add Heading
   heading = odf_create_heading(1, text=u'Headings, Paragraph, Liste and Notes')
   body.append_element(heading)

   # Add Paragraph
   paragraph = odf_create_paragraph(text=u'lpOD generated Document')
   body.append_element(paragraph)

   # Save
   document.save('text_cookbook.odt', pretty=True)

- To add a list::

   # Import from lpod
   from lpod.document import odf_create_list, odf_create_list_item
   my_list = odf_create_list([u'chocolat', u'café'])
   
   item = odf_create_list_item(u'Du thé')
   item.append_element(odf_create_list([u'thé vert', u'thé rouge']))
   my_list.append_item(item)
   
   # insert item by position 
   my_list.insert_item(u'Chicoré', position=1)
   
   # insert item by relativ position 
   the = my_list.get_item_by_content('thé')
   my_list.insert_item(u'Chicoré', before=the)
   my_list.insert_item(u'Chicoré', after=the)

   body.append_element(my_list)

- And footnote::

   # Footnote
   paragraph = odf_create_paragraph(text=u'A paragraph with a footnote '
                                         u'about references in it.')
   note = u'Author, A. (2007). "How to cite references", New York: McGraw-Hill.'

   paragraph.add_footnote(u'1', id='note1', place='references', body=note)
   body.append_element(paragraph)

Pages
=======

- Create a text with multiples pages and their own style.
- footer, header

create a ods from multiples csv files
=======================================

- create a ods from multiples csv files::

   # Import from the Standard Library
   from glob import glob

   # Import from lpod
   from lpod.document import odf_new_document_from_type
   from lpod.table import create_table_from_csv

   # Get elements
   document = odf_new_document_from_type('spreadsheet')
   body = document.get_body()

   # Delete the 3 default sheets
   body.clear()

   for id, csv_name in enumerate(glob('./files/*.csv')):
       tab = create_table_from_csv(u'tab_%s' % id , csv_name)
       body.append_element(tab)

   # Save
   document.save('spreadsheet.ods', pretty=True)


Slide Show with ODP
=====================

- Create a presentation with slides::

   # Import from lpod
   from lpod.document import odf_create_drawpage
   from lpod.document import odf_create_textframe, odf_create_imageframe

   # Creation of the document
   document = odf_new_document_from_type('presentation')
   body = document.get_body()

   # DrawPage 1
   page = odf_create_drawpage('page1')

   # Add a frame with a draw_text_box
   text_element = odf_create_heading(1, text=u'First Slide')

   draw_textframe1 = odf_create_textframe(text_elment,
                                          ('5cm', '100mm'), #(width_size, height_size)
                                          position=('1cm', '2cm'))
   page.append_element(draw_textframe1)

   # Add the page to the body
   body.append_element(page)

   # Save
   document.save('presentation.odp', pretty=True)

- If first arg is text a paragraph is created::

   draw_textframe2 = odf_create_textframe(u"Noël", size=('3cm', '1cm'),
                                          position=('1cm', '3cm'))
   page.append_element(draw_textframe2)


- Add a slide with image

  - Add an image frame from a file name::

     local_uri = document.addfile('images/zoé.jpg')
     draw_imageframe1 = odf_create_imageframe(local_uri, ('5cm', '100mm'), link=1,
                                              position=('1cm', '0cm'))
     page.append_element(draw_imageframe1)

  - Add an image frame from a file descriptor::

     def get_thumbnail_file(filename):
         """ helper function """

         from PIL import Image
         from cStringIO import StringIO

         im = Image.open(filename)
         im.thumbnail((300, 400), Image.ANTIALIAS)
         filedescriptor = StringIO()
         im.save(filedescriptor, 'JPEG', quality=80)
         im.close()
         filedescriptor.seek(0)
         return filedescriptor

     filedescriptor = get_thumbnail_file(u'images/zoé.jpg')
     document.addfile(filedescriptor)

     draw_imageframe2 = odf_create_imageframe(filedescriptor, ('5cm', '100mm'), link=1,
                                              position=('1cm', '0cm'))

     page.append_element(draw_imageframe2)

- Clone a slide and change it, we get a new page, page2 copy of page1::

   ### Warning check if page name are unique
   page2 = page.clone()

   el = page2.get_heading_by_content(u'First')
   el.set_text(u'Second Slide')
   body.append_element(page2)

- Slide transition

