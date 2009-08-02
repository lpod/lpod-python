# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_list, odf_create_list_item
from lpod.document import odf_create_note, odf_create_annotation

# Creation of the document
document = odf_new_document_from_type('presentation')
body = document.get_body()

# DrawPage 1
page = odf_create_drawpage('page1')

# Add a frame with a draw_text-box
text-element = odf_create_heading(1, text=u'First Slide')
draw_text-box = odf_create_frame-text(text-elment,
                                      frame_size=('5cm', '100mm'),
                                      frame_position=('1cm', '0cm'),
                                      style=xxx)
page.append_element(draw_text-box)

# Add an image frame
draw_image = odf_create_frame-image(image_uri="toto.jpg",
                                    link=yes,
                                    frame_size=('5cm', '100mm'),
                                    frame_position=('1cm', '0cm'),
                                    image_style=xxx)
page.append_element(draw_image)

# Add the page to the body
body.append_element(page)


# Get a new page, page2 copy of page1
page2 = page.clone('page2')
#page2 = body.get_clone('page2', page)
#page2 = body.get_copy('page2', page)

frame = page2.get_frame()




# Save
document.save('presentation.odp', pretty=True)
