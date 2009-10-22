# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from glob import glob

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.table import import_from_csv

# Get elements
document = odf_new_document_from_type('spreadsheet')
body = document.get_body()

for id, filename in enumerate(glob('./files/*.csv')):
    table = import_from_csv(filename, u'Table %s' % (id + 1))
    # Table is represented as a matrix in memory,
    # so ask to reformat it to XML
    body.append_element(table.to_odf_element())

# Save
filename = 'spreadsheet.ods'
document.save(filename, pretty=True)
print 'Document "%s" generated.' % filename
