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
from lpod.document import odf_create_note, odf_create_span
from lpod.styles import rgb2hex



document = odf_new_document_from_class('text')

content = document.get_xmlpart('content')
body = content.get_text_body()

styles = document.get_xmlpart('styles')
named_styles = styles.get_category_context('named')


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
content.insert_element(image, frame)
content.insert_element(frame, paragraph)
content.insert_element(paragraph, body)

# And store the data
container = document.container
container.set_part(internal_name, image_file.to_str())


# 2- a paragraph
# --------------
heading = odf_create_heading('Heading', 1, u'Congratulations !')
content.insert_element(heading, body)

# The style
style = odf_create_style('style1', 'paragraph')
style.set_attribute('style:parent-style-name', 'Standard')
properties = odf_create_style_text_properties()
properties.set_attribute('fo:color', rgb2hex('blue'))
properties.set_attribute('fo:background-color', rgb2hex('red'))

styles.insert_element(properties, style)
styles.insert_element(style, named_styles)

# The paragraph
paragraph = odf_create_paragraph('style1', u'A paragraph with a new style.')
content.insert_element(paragraph, body)


# 3- the table
# ------------
heading = odf_create_heading('Heading', 1, u'A table')
content.insert_element(heading, body)

table = odf_create_table('table1', 'Standard')

# A "float"
row = odf_create_row()

cell = odf_create_cell('A float')
content.insert_element(cell, row)

cell = odf_create_cell(3.14)
content.insert_element(cell, row)

content.insert_element(row, table)

# A "date"
row = odf_create_row()

cell = odf_create_cell('A date')
content.insert_element(cell, row)

cell = odf_create_cell(datetime.now())
content.insert_element(cell, row)

content.insert_element(row, table)

# Columns => Standard
for i in range(2):
    column = odf_create_column('Standard')
    content.insert_element(column, table, FIRST_CHILD)
content.insert_element(table, body)


# 4- A footnote
# -------------

heading = odf_create_heading('Heading', 1, u'A paragraph with a footnote')
content.insert_element(heading, body)

paragraph = odf_create_paragraph('Standard', u'An other paragraph.')
content.insert_element(paragraph, body)

note = odf_create_note(u'1', id='note1')
body =  odf_create_paragraph('Standard', u'a footnote')
content.insert_note_body(body, note)

content.insert_element(note, paragraph, offset=8)
content.insert_element(paragraph, body)


# 5- An other paragraph
# ---------------------

heading = odf_create_heading('Heading', 1, u'A paragraph with a colored word')
content.insert_element(heading, body)

# The style
style = odf_create_style('style2', 'text')
style.set_attribute('style:parent-style-name', 'Standard')
properties = odf_create_style_text_properties()
properties.set_attribute('fo:background-color', rgb2hex('yellow'))
styles.insert_element(properties, style)
styles.insert_element(style, named_styles)

# The paragraph
# XXX Use "length"
paragraph = odf_create_paragraph('Standard', u'And an  paragraph.')
span = odf_create_span('style2', u'other')
content.insert_element(span, paragraph, offset=len(u'And an '))
content.insert_element(paragraph, body)



# Save
# ----

vfs.make_folder('trash')
document.save('trash/use_case2.odt', pretty=True)


