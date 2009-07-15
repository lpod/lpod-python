# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime

# Import from itools
from itools import vfs
from itools.handlers import get_handler


# Import from lpod
from lpod.document import odf_new_document_from_class
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.document import odf_create_style, odf_create_style_text_properties
from lpod.document import odf_create_note, odf_create_span
from lpod.styles import rgb2hex
from lpod.xmlpart import FIRST_CHILD, LAST_CHILD



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
frame.insert_element(image, LAST_CHILD)
paragraph.insert_element(frame, LAST_CHILD)
body.insert_element(paragraph, LAST_CHILD)

# And store the data
container = document.container
container.set_part(internal_name, image_file.to_str())

# 2- a paragraph
# --------------
heading = odf_create_heading('Heading', 1, u'Congratulations !')
body.insert_element(heading, LAST_CHILD)

# The style
style = odf_create_style('style1', 'paragraph')
style.set_attribute('style:parent-style-name', 'Standard')
properties = odf_create_style_text_properties()
properties.set_attribute('fo:color', rgb2hex('blue'))
properties.set_attribute('fo:background-color', rgb2hex('red'))

style.insert_element(properties, LAST_CHILD)
named_styles.insert_element(style, LAST_CHILD)

# The paragraph
paragraph = odf_create_paragraph('style1', u'A paragraph with a new style.')
body.insert_element(paragraph, LAST_CHILD)


# 3- the table
# ------------
heading = odf_create_heading('Heading', 1, u'A table')
body.insert_element(heading, LAST_CHILD)

table = odf_create_table('table1', 'Standard')

# A "float"
row = odf_create_row()

cell = odf_create_cell('A float')
row.insert_element(cell, LAST_CHILD)

cell = odf_create_cell(3.14)
row.insert_element(cell, LAST_CHILD)

table.insert_element(row, LAST_CHILD)

# A "date"
row = odf_create_row()

cell = odf_create_cell('A date')
row.insert_element(cell, LAST_CHILD)

now = datetime.now()
representation = unicode(now.strftime('%c'))
cell = odf_create_cell(now, representation=representation)
row.insert_element(cell, LAST_CHILD)

table.insert_element(row, LAST_CHILD)

# Columns => Standard
for i in range(2):
    column = odf_create_column('Standard')
    table.insert_element(column, FIRST_CHILD)
body.insert_element(table, LAST_CHILD)


# 4- A footnote
# -------------

heading = odf_create_heading('Heading', 1, u'A paragraph with a footnote')
body.insert_element(heading, LAST_CHILD)

note_body = odf_create_paragraph('Standard', u'a footnote')
note = odf_create_note(u'1', id='note1', body=note_body)

paragraph = odf_create_paragraph('Standard', u'Another paragraph.')
offset = len(u'Another')
paragraph.wrap_text(note, offset=offset)
body.insert_element(paragraph, LAST_CHILD)


# 5- Another paragraph
# ---------------------

heading = odf_create_heading('Heading', 1, u'A paragraph with a colored word')
body.insert_element(heading, LAST_CHILD)

# The style
style = odf_create_style('style2', 'text')
style.set_attribute('style:parent-style-name', 'Standard')
properties = odf_create_style_text_properties()
properties.set_attribute('fo:background-color', rgb2hex('yellow'))
style.insert_element(properties, LAST_CHILD)
named_styles.insert_element(style, LAST_CHILD)

# The paragraph
text = u'And another paragraph.'
paragraph = odf_create_paragraph('Standard', text)
span = odf_create_span('style2')
offset = text.index(u'another')
length = len(u'another')
paragraph.wrap_text(span, offset=offset, length=length)
body.insert_element(paragraph, LAST_CHILD)



# Save
# ----

vfs.make_folder('trash')
document.save('trash/use_case2.odt', pretty=True)


