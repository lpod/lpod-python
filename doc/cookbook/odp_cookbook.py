# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.paragraph import odf_create_paragraph
from lpod.frame import odf_create_text_frame, odf_create_image_frame
from lpod.draw_page import odf_create_draw_page

PPC = 72 * 2.54


# helper function
def get_thumbnail_file(filename):
    from PIL import Image
    from cStringIO import StringIO

    im = Image.open(filename)
    im.thumbnail((300, 400), Image.ANTIALIAS)
    filedescriptor = StringIO()
    im.save(filedescriptor, 'JPEG', quality=80)
    filedescriptor.seek(0)
    return filedescriptor, (im.size[0] / PPC), (im.size[1] / PPC)


# Creation of the document
document = odf_new_document_from_type('presentation')
body = document.get_body()

#
# Work on pages and add textframes
#
# The document already contains a page
page = body.get_draw_page_by_position(1)

# Add a frame with a text box
text_element = odf_create_paragraph(u'First Slide', style=u"Text_20_body")
draw_textframe1 = odf_create_text_frame(text_element,
                                        size=('5cm', '100mm'),
                                        position=('3.5cm', '30.6mm'))
page.append_element(draw_textframe1)

# If first arg is text a paragraph is created automatically
draw_textframe2 = odf_create_text_frame(u"Noël",
                                        size=('5cm', '100mm'),
                                        position=('20cm', '14cm'))
page.append_element(draw_textframe2)

#
# Add images frames
#
# Add an image frame from a file name
local_uri = document.add_file(u'images/zoé.jpg')
draw_imageframe1 = odf_create_image_frame(local_uri,
                                          size=('6cm', '24.2mm'),
                                          position=('1cm', '10cm'))
page.append_element(draw_imageframe1)

# Add an image frame from a file descriptor
filedescriptor, width, height = get_thumbnail_file(u'images/zoé.jpg')
local_uri = document.add_file(filedescriptor)
draw_imageframe2 = odf_create_image_frame(local_uri,
                                          size=('%scm' % width,
                                                '%scm' % height),
                                          position=('12cm', '2cm'))
page.append_element(draw_imageframe2)

# Add the page to the body
body.append_element(page)

#
# Get a new page, page2 copy of page1
#
page2 = page.clone()
page2.set_page_name(u'Page 2')
paragraph = page2.get_paragraph_by_content(u'First')
paragraph.set_text(u'Second Slide')

#
# Add transition for page2
#
#page2.add_transition('fade')
body.append_element(page2)

#
# Build a new page from scratch
#
page3 = odf_create_draw_page(u"Page 3")
frame = body.get_frame_by_content(u"Second").clone()
frame.set_size(('10cm', '100mm'))
frame.set_position(('100mm', '10cm'))
# A shortcut to hit embedded paragraph
frame.set_text_content(u"Third Slide")
page3.append_element(frame)
body.append_element(page3)

# Save
document.save('presentation.odp', pretty=True)
