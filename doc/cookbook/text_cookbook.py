# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_list, odf_create_list_item

# Creation of the document
document = odf_new_document_from_type('text')
body = document.get_body()

# Add Heading
heading = odf_create_heading(1, text=u'Headings, Paragraph, Liste and Notes')
body.append_element(heading)

# Add Paragraph
paragraph = odf_create_paragraph(text=u'lpOD generated Document')
body.append_element(paragraph)

# A list
my_list = odf_create_list([u'chocolat', u'café'])

item = odf_create_list_item(u'Du thé')
item.append_element(odf_create_list([u'thé vert', u'thé rouge']))

my_list.append_item(item)

my_list.insert_item(u'Chicoré', position=1)

the = my_list.get_item_by_content('thé')
my_list.insert_item(u'Chicoré', before=the)
my_list.insert_item(u'Chicoré', after=the)


body.append_element(my_list)

# Footnote
paragraph = odf_create_paragraph(text=u'A paragraph with a footnote in it.')
note = u'Author, A. (2007). "How to cite references", New York: McGraw-Hill.'
paragraph.add_footnote(u'1', id='note1', place='footnote', body=note)
body.append_element(paragraph)

# Save
document.save('text_cookbook.odt', pretty=True)
