# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.document import odf_get_document, odf_new_document_from_type
from lpod.paragraph import odf_create_paragraph

# Creation of the document
document = odf_new_document_from_type('text')
body = document.get_body()

#
# use merge_styles_from to copy default style from some document
#
doc_style = odf_get_document('../../python/templates/lpod_styles.odt')
document.merge_styles_from(doc_style)

#
# Pages, header and footer
#

paragraph = odf_create_paragraph(text=u'lpOD generated Document '
                                       'with styled pages')

# Apply a named style to a page e.g. here 'first page style'
paragraph.set_master_page_style(u'first page style')

# to modify the footer and header we get the style
first_page_style = document.get_style(u'first page style')

# and we set the content to modify footer or header
# this orverwrite every footer elements by a paragraphe.
first_page_style.set_footer(u'lpOD project')

# instead of using set_header we can just modify a part of it
header = first_page_style.get_header()
par = header.get_paragraph_by_content(u'Draft')
par.set_text(u'Final Version')


# Save
body.append_element(paragraph)
document.save('styles_cookbook.odt', pretty=True)
