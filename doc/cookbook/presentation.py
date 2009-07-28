# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_list, odf_create_list_item
from lpod.document import odf_create_note, odf_create_annotation

# Creation of the document
document = odf_new_document_from_type('text')
body = document.get_body()

# Add Heading
heading = odf_create_heading(level=1, u'Headings, Paragraph, Liste and Notes')
body.append_element(heading)

# Add Paragraph 
paragraph = odf_create_paragraph(text = u'lpOD generated Document')
body.append_element(paragraph)

# A list
my_list = odf_create_list([u'thé', u'café'])
item = odf_create_list_item(u'chocolat')
my_list.append_element(item)

# Footnote, endnote, annotations
footnote = odf_create_note(u'1', id='note1', body=u'A footnote')
paragraph = odf_create_paragraph(u'A paragraph with a footnote.')

##offset = len(u'A paragraph')
##paragraph.wrap_text(footnote, offset=offset)
##body.append_element(paragraph)

paragraph.add_footnote(footnote, place="xxx")
paragraph.add_endnote(footnote, place=34)
paragraph.add_annotation(footnote, place='')
paragraph.add_note(footnote, type="footnote", place="")

# Save
document.save('basic-text.odt', pretty=True)
