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
heading = odf_create_heading(1, text=u'Headings, Paragraph, Liste and Notes')
body.append_element(heading)
text-element = odf_create_paragraph(text = u'First SlideShow')

draw_text-box1 = odf_create_text-box(text-elment, height, width=, x=, y=, image_style=)

draw_text-box1 = odf_create_text-box(text-elment, frame=frame)

draw_text-box1 = odf_create_text-box(text-elment, 
                                     frame_size=('5cm', '100mm'), 
                                     frame_position=('1cm', '0cm'),
                                     image_style=xxx)


page.append_element(draw_text-box)

# fill draw_text-box with a paragraph
text-element = odf_create_list([u'thé', u'café'])
text-frame = odf_create_text_frame(text-elment, height, width=, x=, y=)
page.append_element(text-frame)


#existe en mémoir n'a pas été sérialisé
image = odf_create_image(image_uri="toto.jpg", image_style=xxx, link=yes)

draw_image = odf_create_image_frame(image_uri="toto.jpg", 
                                    frame_size=('5cm', '100mm'), 
                                    frame_position=('1cm', '0cm'),
                                    image_style=xxx,
                                    link=yes)





draw_image = odf_create_image(uri, height, width=, x=, y=, image_style=)
page.append(draw_image)

# introspection
page.get_frames()

# DrawPage 2
page = body.()

# Add Heading
heading = odf_create_heading(level=1, u'Headings, Paragraph, Liste and Notes')
body.append_element(heading)

# Add Paragraph 
paragraph = odf_create_paragraph(text = u'lpOD generated Document')
body.append_element(paragraph)

# A list
my_list = odf_create_list([u'thé', u'café'])
item = odf_create_list_item(u'chocolat')
my_list.append_element(item)

# Save
document.save('presentation.odp', pretty=True)
