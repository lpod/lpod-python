# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from itools
from itools.csv import CSVFile
from itools.handlers import get_handler, Image

# Import from lpod
from lpod.xmlpart import FIRST_CHILD
from lpod.document import odf_new_document_from_type
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.vfs import vfs
from lpod import __version__, __installation_path__


# Hello messages
print 'lpod installation test'
print ' Version           : %s' %  __version__
print ' Installation path : %s' % __installation_path__
print
print 'Generating test_output/use_case1.odt ...'


# Go
document = odf_new_document_from_type('text')
body = document.get_body()

samples = vfs.open('samples')
for numero, filename in enumerate(samples.get_names()):
    # Heading
    heading = odf_create_heading(2, text=unicode(filename, 'utf-8'))
    body.append_element(heading)

    uri = samples.get_uri(filename)
    handler = get_handler(uri)
    if isinstance(handler, Image):
        # Add the image
        internal_name = 'Pictures/' + filename
        width, height = handler.get_size()
        paragraph = odf_create_paragraph('Standard')
        # 72 ppp
        frame = odf_create_frame('frame_%d' % numero, 'Graphics',
                                 str(width / 72.0) + 'in',
                                 str(height / 72.0) + 'in')
        image = odf_create_image(internal_name)
        frame.append_element(image)
        paragraph.append_element(frame)
        body.append_element(paragraph)

        # And store the data
        container = document.container
        container.set_part(internal_name,
                           samples.open(filename).read())
    elif isinstance(handler, CSVFile):
        table = odf_create_table('table_%d' % numero, 'Standard')
        for csv_row in handler.get_rows():
            size = len(csv_row)
            row = odf_create_row()
            for value in csv_row:
                cell = odf_create_cell(value)
                row.append_element(cell)
            table.append_element(row)
        for i in xrange(size):
            column = odf_create_column('Standard')
            table.insert_element(column, FIRST_CHILD)
        body.append_element(table)
    else:
        paragraph = odf_create_paragraph('Standard', u'Not image / csv')
        body.append_element(paragraph)

vfs.make_folder('test_output')
document.save('test_output/use_case1.odt', pretty=True)


