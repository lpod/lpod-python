# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime

# Import from itools
from itools import vfs
from itools.handlers import get_handler


# Import from lpod
from lpod.xmlpart import FIRST_CHILD
from lpod.document import odf_new_document_from_class
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.document import odf_create_style, odf_create_style_text_properties
from lpod.document import odf_create_note



document = odf_new_document_from_class('text')

# 1- the image
# ------------
image_file = get_handler('samples/image.png')
width, height = image_file.get_size()
paragraph = odf_create_paragraph('Standard')
# 72 ppp
frame = odf_create_frame('frame1', 'Graphics',
                         str(width / 72.0) + 'in',
                         str(height / 72.0) + 'in')
internal_name = 'Pictures/image.png'
image = odf_create_image(internal_name)
document.insert_element(image, frame)
document.insert_element(frame, paragraph)
document.insert_element(paragraph)

# And store the data
container = document.container
container.set_part(internal_name, image_file.to_str())


# 2- a paragraph
# --------------
heading = odf_create_heading('Heading', 1, u'Congratulations !')
document.insert_element(heading)

# The style
style = odf_create_style('style1', 'paragraph')
style.set_attribute('style:parent-style-name', 'Standard')
properties = odf_create_style_text_properties()
properties.set_attribute('fo:color', '#0000ff')
properties.set_attribute('fo:background-color', '#ff0000')
document.insert_element(properties, style)
document.insert_element(style)

# The paragraph
paragraph = odf_create_paragraph('style1', u'A paragraph with a new style.')
document.insert_element(paragraph)


# 3- the table
# ------------
heading = odf_create_heading('Heading', 1, u'A table')
document.insert_element(heading)

table = odf_create_table('table1', 'Standard')

# A "float"
row = odf_create_row()

cell = odf_create_cell('A float')
document.insert_element(cell, row)

cell = odf_create_cell(3.14)
document.insert_element(cell, row)

document.insert_element(row, table)

# A "date"
row = odf_create_row()

cell = odf_create_cell('A date')
document.insert_element(cell, row)

cell = odf_create_cell(datetime.now())
document.insert_element(cell, row)

document.insert_element(row, table)

# Columns => Standard
for i in range(2):
    column = odf_create_column('Standard')
    document.insert_element(column, table, FIRST_CHILD)
document.insert_element(table)


# 4- A footnote
# -------------

heading = odf_create_heading('Heading', 1, u'A paragraph with a footnote')
document.insert_element(heading)

paragraph = odf_create_paragraph('Standard', u'An other paragraph.')
document.insert_element(paragraph)

note = odf_create_note(u'1', id='note1')
body =  odf_create_paragraph('Standard', u'a footnote')
document.insert_note_body(body, note)

document.insert_element(note, paragraph, offset=8)
document.insert_element(paragraph)


vfs.make_folder('trash')
document.save('trash/use_case2.odt', pretty=True)


