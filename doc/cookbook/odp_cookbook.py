# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.document import odf_create_paragraph, odf_create_heading

from lpod.document import odf_create_drawpage
from lpod.document import odf_create_textframe, odf_create_imageframe

# helper function
def get_thumbnail_file(filename):
    from PIL import Image
    from cStringIO import StringIO

    im = Image.open(filename)
    im.thumbnail((300, 400), Image.ANTIALIAS)
    filedescriptor = StringIO()
    im.save(filedescriptor, 'JPEG', quality=80)
    im.close()
    filedescriptor.seek(0)
    return filedescriptor

# Creation of the document
document = odf_new_document_from_type('presentation')
body = document.get_body()

# DrawPage 1
page = odf_create_drawpage('page1')

# Add a frame with a draw_text_box
text_element = odf_create_heading(1, text=u'First Slide')

draw_textframe1 = odf_create_textframe(text_elment,
                                       ('5cm', '100mm'), #size (width, height)
                                       position=('1cm', '0cm'))
page.append_element(draw_textframe1)

# if first arg is text a paragraph is created
draw_textframe2 = odf_create_textframe(u"Noël",
                                       size=('5cm', '100mm'),
                                       position=('1cm', '0cm'))
page.append_element(draw_textframe2)


# Add an image frame from a file name
local_uri = document.addfile('images/zoé.jpg')
draw_imageframe1 = odf_create_imageframe(local_uri,
                                         ('5cm', '100mm'), #size (width, height)
                                         link=1,
                                         position=('1cm', '0cm'))
page.append_element(draw_imageframe1)



# Add an image frame from a file descriptor
filedescriptor = get_thumbnail_file(u'images/zoé.jpg')
document.addfile(filedescriptor)

draw_imageframe2 = odf_create_imageframe(filedescriptor,
                                         ('5cm', '100mm'), #size (width, height)
                                         link=1,
                                         position=('1cm', '0cm'))

page.append_element(draw_imageframe2)


# Add the page to the body
body.append_element(page)

text_element = odf_create_heading(1, text=u'First Slide')

# Get a new page, page2 copy of page1
### Warning check if page name are unique
page2 = page.clone()
el = page2.get_heading_by_content(u'First')
el.set_text(u'Second Slide')
body.append_element(page2)

# Save
document.save('presentation.odp', pretty=True)
