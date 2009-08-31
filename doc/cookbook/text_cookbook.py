# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.heading import odf_create_heading
from lpod.list import odf_create_list, odf_create_list_item
from lpod.note import odf_create_note
from lpod.paragraph import odf_create_paragraph
from lpod.toc import odf_create_toc

# Creation of the document
document = odf_new_document_from_type('text')
body = document.get_body()

# The document already contains an empty paragraph, like when you open a
# new document in your office application.
# Let's replace it
body.clear()

# Add (empty) Table of content
toc = odf_create_toc()
body.append_element(toc)

# Add Heading
heading = odf_create_heading(1, text=u'Headings, Paragraphs, Lists and Notes')
body.append_element(heading)

# Add Paragraph
paragraph = odf_create_paragraph(text=u'lpOD generated Document')
body.append_element(paragraph)

#
# A list
#
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
# Footnote with odf_create_note of class "footnote" and insert_note
#
paragraph = odf_create_paragraph(text=u'A paragraph with a footnote '
                                      u'about references in it.')
note = odf_create_note(note_id='note1', citation=u"1",
                       body=u'Author, A. (2007). "How to cite references", '
                            u'New York: McGraw-Hill.')
paragraph.insert_note(note, after=u"graph")

body.append_element(paragraph)

# Save
document.save('text_cookbook.odt', pretty=True)
