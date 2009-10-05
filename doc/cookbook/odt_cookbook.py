# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type, odf_get_document
from lpod.heading import odf_create_heading
from lpod.list import odf_create_list, odf_create_list_item
from lpod.note import odf_create_note, odf_create_annotation
from lpod.paragraph import odf_create_paragraph
from lpod.table import odf_create_table
from lpod.toc import odf_create_toc

# Creation of the document
document = odf_new_document_from_type('text')
body = document.get_body()

# Add (empty) Table of content
toc = odf_create_toc()
body.append_element(toc)

# Add Paragraph
paragraph = odf_create_paragraph(u'lpOD generated Document')
body.append_element(paragraph)

# Add Heading
heading = odf_create_heading(1, text=u'Lists')
body.append_element(heading)

#
# A list
#
my_list = odf_create_list([u'chocolat', u'café'])

item = odf_create_list_item(u'Du thé')
item.append_element(odf_create_list([u'thé vert', u'thé rouge']))
my_list.append_item(item)

# insert item by position
my_list.insert_item(u'Chicorée', position=1)

# insert item by relative position
the = my_list.get_item_by_content(u'thé')
my_list.insert_item(u'Chicorée', before=the)
my_list.insert_item(u'Chicorée', after=the)

body.append_element(my_list)

#
# Footnote with odf_create_note of class "footnote" and insert_note
#
body.append_element(odf_create_heading(1, u"Footnotes"))
paragraph = odf_create_paragraph(u'A paragraph with a footnote '
                                      u'about references in it.')
note = odf_create_note(note_id='note1', citation=u"1",
                       body=u'Author, A. (2007). "How to cite references", '
                            u'New York: McGraw-Hill.')
paragraph.insert_note(note, after=u"graph")
body.append_element(paragraph)

#
# Annotations
#
body.append_element(odf_create_heading(1, u"Annotations"))
paragraph = odf_create_paragraph(u"A paragraph with an annotation "
                                 u"in the middle.")
annotation = odf_create_annotation(u"It's so easy!", creator=u"Luis")
paragraph.insert_annotation(annotation, after=u"annotation")
body.append_element(paragraph)

#
# Tables
#
body.append_element(odf_create_heading(1, u"Tables"))
body.append_element(odf_create_paragraph(u"A table:"))
table = odf_create_table(u"Table 1", width=3, height=3)
body.append_element(table)

#
# Applying styles
#
body.append_element(odf_create_heading(1, u"Applying Styles"))

# Copying a style from another document
lpod_styles = odf_get_document('../../python/templates/lpod_styles.odt')
highlight = lpod_styles.get_style('text', u"Yellow Highlight",
                                  display_name=True)
assert highlight is not None
document.insert_style(highlight)

# Apply this style to a pattern
paragraph = odf_create_paragraph(u'Highlighting the word "highlight".')
paragraph.set_span(highlight, u"highlight")
body.append_element(paragraph)

# Save
document.save('text.odt', pretty=True)
