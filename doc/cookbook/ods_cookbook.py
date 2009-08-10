# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from glob import glob

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.table import create_table_from_csv

# Get elements
document = odf_new_document_from_type('spreadsheet')
body = document.get_body()

# Delete the 3 default sheets
body.clear()

for id, csv_name in enumerate(glob('./files/*.csv')):
    tab = create_table_from_csv(u'tab_%s' % id , csv_name)
    body.append_element(tab)

# Save
document.save('spreadsheet.ods', pretty=True)


