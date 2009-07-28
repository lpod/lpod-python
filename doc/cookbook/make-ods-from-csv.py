# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from glob import glob
from csv import reader

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.table import odf_table



def get_python_value(data):
    # Nothing ?
    if data == '':
        return None

    # An integer ?
    try:
        return int(data)
    except ValueError:
        pass

    # A float ?
    try:
        return float(data)
    except ValueError:
        pass

    # So => a string
    return data



# Get elements
document = odf_new_document_from_type('spreadsheet')
body = document.get_body()

# Delete the 3 default sheets
body.clear()

# Read the files, make the tables
csv_filenames = glob('*.csv')
csv_filenames.sort()
for csv_name in csv_filenames:
    csv_file = reader(open(csv_name), delimiter=';', lineterminator='\n')

    data = [ [ get_python_value(value) for value in line ]
             for line in csv_file ]
    table = odf_table(name=csv_name[:-4], style='Standard', data=data)
    body.append_element(table.get_odf_element())



# Save
document.save('make-ods-from-csv.ods', pretty=True)


