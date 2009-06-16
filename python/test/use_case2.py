# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime

# Import from itools
from itools import vfs
from itools.datatypes import DateTime
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
document.insert_image(image, frame)
document.insert_frame(frame, paragraph)
document.insert_paragraph(paragraph)

# And store the data
container = document.container
container.set_part(internal_name, image_file.to_str())


# 2- a paragraph
# --------------
heading = odf_create_heading('Heading', 1, 'Congratulations !')
document.insert_heading(heading)

# The style
style = odf_create_style('style1', 'paragraph')
style.set_attribute('style:parent-style-name', 'Standard')
properties = odf_create_style_text_properties()
properties.set_attribute('fo:color', '#0000ff')
properties.set_attribute('fo:background-color', '#ff0000')
document.insert_style_properties(properties, style)
document.insert_style(style)

# The paragraph
paragraph = odf_create_paragraph('style1', 'A paragraph with a new style.')
document.insert_paragraph(paragraph)


# 3- the table
# ------------
heading = odf_create_heading('Heading', 1, 'A table')
document.insert_heading(heading)

table = odf_create_table('table1', 'Standard')

# A "float"
row = odf_create_row()

cell = odf_create_cell()
paragraph = odf_create_paragraph('Standard', 'A float')
document.insert_paragraph(paragraph, cell)
document.insert_cell(cell, row)


cell = odf_create_cell('float')
cell.set_attribute('office:value', '3.14')
paragraph = odf_create_paragraph('Standard', '3,14')
document.insert_paragraph(paragraph, cell)
document.insert_cell(cell, row)

document.insert_row(row, table)

# A "date"
row = odf_create_row()

cell = odf_create_cell()
paragraph = odf_create_paragraph('Standard', 'A date')
document.insert_paragraph(paragraph, cell)
document.insert_cell(cell, row)


cell = odf_create_cell('date')
now = datetime.now()
enc = DateTime.encode(now)
cell.set_attribute('office:date-value', enc)
paragraph = odf_create_paragraph('Standard', now.strftime('%c'))
document.insert_paragraph(paragraph, cell)
document.insert_cell(cell, row)

document.insert_row(row, table)

# Columns => Standard
for i in range(2):
    column = odf_create_column('Standard')
    document.insert_column(column, table, FIRST_CHILD)
document.insert_table(table)


# 4- A footnote
# -------------

heading = odf_create_heading('Heading', 1, 'A paragraph with a footnote')
document.insert_heading(heading)

paragraph = odf_create_paragraph('Standard', 'An other paragraph.')
document.insert_paragraph(paragraph)

note = odf_create_note('1', id='note1')
body =  odf_create_paragraph('Standard', 'a footnote')
document.insert_note_body(body, note)

document.insert_note(note, paragraph)
document.insert_paragraph(paragraph)


vfs.make_folder('trash')
document.save('trash/use_case2.odt', pretty=True)


