# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.paragraph import odf_create_paragraph
from lpod.heading import odf_create_heading

# Creation of the document
document = odf_new_document_from_type('text')
body = document.get_body()

# Add Heading
heading = odf_create_heading(1, text=u'Headings, Paragraph, Liste and Notes')
body.append_element(heading)

# Add Paragraph
paragraph = odf_create_paragraph(text=u'lpOD generated Document')
body.append_element(paragraph)

#
# A list
#
# Import from lpod
from lpod.document import odf_create_list, odf_create_list_item

my_list = odf_create_list([u'chocolat', u'café'])

item = odf_create_list_item(u'Du thé')
item.append_element(odf_create_list([u'thé vert', u'thé rouge']))
my_list.append_item(item)

# insert item by position
my_list.insert_item(u'Chicoré', position=1)

# insert item by relativ position
the = my_list.get_item_by_content(u'thé')
my_list.insert_item(u'Chicoré', before=the)
my_list.insert_item(u'Chicoré', after=the)

body.append_element(my_list)

#
# Footnote with odf_create_footnote and insert_note
#
# Import from lpod
from lpod.note import odf_create_footnote

paragraph = odf_create_paragraph(text=u'A paragraph with a footnote '
                                      u'about references in it.')

note = odf_create_footnote(note_id='note1', citation=u"1",
                           body=u'Author, A. (2007). "How to cite references", '
                                u'New York: McGraw-Hill.')
paragraph.insert_note(note, after=u"graphe")

body.append_element(paragraph)

# Save
document.save('text_cookbook.odt', pretty=True)
