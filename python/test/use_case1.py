# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from itools
from itools.csv import CSVFile
from itools.handlers import get_handler, Image

# Import from lpod
from lpod.xmlpart import FIRST_CHILD
from lpod.document import odf_new_document_from_class
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.vfs import vfs
from lpod.xmlpart import LAST_CHILD


document = odf_new_document_from_class('text')
content = document.get_xmlpart('content')
body = content.get_text_body()

samples = vfs.open('samples')
for numero, filename in enumerate(samples.get_names()):
    # Heading
    heading = odf_create_heading('Standard', 2, unicode(filename, 'utf-8'))
    body.insert_element(heading, LAST_CHILD)

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
        frame.insert_element(image, LAST_CHILD)
        paragraph.insert_element(frame, LAST_CHILD)
        body.insert_element(paragraph, LAST_CHILD)

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
                row.insert_element(cell, LAST_CHILD)
            table.insert_element(row, LAST_CHILD)
        for i in xrange(size):
            column = odf_create_column('Standard')
            table.insert_element(column, FIRST_CHILD)
        body.insert_element(table, LAST_CHILD)
    else:
        paragraph = odf_create_paragraph('Standard', u'Not image / csv')
        body.insert_element(paragraph, LAST_CHILD)

vfs.make_folder('trash')
document.save('trash/use_case1.odt', pretty=True)


