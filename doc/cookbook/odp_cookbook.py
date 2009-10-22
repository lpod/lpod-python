# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.draw_page import odf_create_draw_page
from lpod.frame import odf_create_text_frame, odf_create_image_frame
from lpod.list import odf_create_list
from lpod.shapes import odf_create_line, odf_create_connector
from lpod.shapes import odf_create_rectangle, odf_create_ellipse
from lpod.style import odf_create_style

PPC = 72 * 2.54


# Creation of the document
document = odf_new_document_from_type('presentation')
body = document.get_body()

# Change the default graphic fill color
standard = document.get_style('graphic', u"standard")
standard.set_style_properties({'draw:fill-color': '#ffffff'})

#
# Work on pages and add textframes
#
page = odf_create_draw_page('page1', name=u"Page 1")
body.append_element(page)

#
# Text Frame
#

# Set the frame color
colored = odf_create_style('graphic', name=u"colored",
                           display_name=u"Colored", parent="standard")
colored.set_style_properties({'draw:fill-color': "#ad7fa8"},
                                 area='graphic')
colored.set_style_properties(color="#ffffff", area='text')
document.insert_style(colored)

# A paragraph style with big font
big = odf_create_style('paragraph', u"big", area='paragraph', align="center")
big.set_style_properties(area='text', size="32pt")
document.insert_style(big, automatic=True)

# Set a text frame
text_frame = odf_create_text_frame([u"lpOD", u"Presentation", u"Cookbook"],
        size=('7cm', '5cm'), position=('11cm', '8cm'), style=u"colored",
        text_style=u"big")
page.append_element(text_frame)

#
# Image Frame
#

# Start a new page
page2 = odf_create_draw_page(u"page2")
body.append_element(page2)

# Embed an image from a file name
local_uri = document.add_file(u'images/zoé.jpg')

# Add image frame
image_frame = odf_create_image_frame(local_uri, size=('60mm', '45mm'),
                                     position=('4.5cm', '7cm'))
page2.append_element(image_frame)

# Some text side by side
list = odf_create_list([u"Item 1", u"Item 2", u"Item 3"])
text_frame = odf_create_text_frame(list, size=('7cm', '2.5cm'),
                                   position=('12.5cm', '7cm'),
                                   style=u"colored")
page2.append_element(text_frame)

#
# Shapes
#

# Last page
page3 = odf_create_draw_page(u"page3")
body.append_element(page3)

# Square
square = odf_create_rectangle(shape_id=u"square", size=('8cm', '8cm'),
                              position=('17cm', '2.5cm'),
                              style=u"colored")
page3.append_element(square)

# Circle
circle = odf_create_ellipse(shape_id=u"circle", size=('8cm', '8cm'),
                            position=('2cm', '10cm'), style=u"colored")
page3.append_element(circle)

# Line
line = odf_create_line(p1=('8cm', '5cm'), p2=('20cm', '17.5cm'))
page3.append_element(line)

# Connector
connector = odf_create_connector(connected_shapes=(square, circle),
                                 glue_points=('1', '3'))

# Save
filename = 'presentation.odp'
document.save(filename, pretty=True)
print 'Document "%s" generated.' % filename
