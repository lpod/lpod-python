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

#$styles->createStyle
#	(
#	"Colour",
#	family		=> 'paragraph',
#	parent		=> 'Standard',
#	properties	=>
#			{
#			-area			=> 'paragraph',
#			'fo:color'		=> odfColor(0,0,128),
#			'fo:background-color'	=> odfColor("yellow"),
#			'fo:text-align'		=> 'justify'
#			}
#	);
#if ($doc->isOpenDocument)
#	{
#	$styles->styleProperties
#		("Colour", -area => 'text', 'fo:color' => '#000080');
#	}

# <style:style style:name="P1" style:family="paragraph" style:parent-style-name="Standard">
#  <style:text-properties fo:color="#0000ff" fo:background-color="#ff0000"/>
# </style:style>


paragraph = odf_create_paragraph('Standard', 'Hello world!')
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




vfs.make_folder('trash')
document.save('trash/use_case2.odt', pretty=True)


