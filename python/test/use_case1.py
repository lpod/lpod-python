# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from itools
from itools import vfs
from itools.csv import CSVFile
from itools.handlers import get_handler, Image

# Import from lpod
from lpod.xmlpart import FIRST_CHILD
from lpod.document import odf_new_document_from_class
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table



document = odf_new_document_from_class('text')

samples = vfs.open('samples')
for numero, filename in enumerate(samples.get_names()):
    # Heading
    heading = odf_create_heading('Standard', 2, filename)
    document.insert_heading(heading)

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
        document.insert_image(image, frame)
        document.insert_frame(frame, paragraph)
        document.insert_paragraph(paragraph)

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
                cell = odf_create_cell()
                paragraph = odf_create_paragraph('Standard', value)
                document.insert_paragraph(paragraph, cell)
                document.insert_cell(cell, row)
            document.insert_row(row, table)
        for i in xrange(size):
            column = odf_create_column('Standard')
            document.insert_column(column, table, FIRST_CHILD)
        document.insert_table(table)
    else:
        paragraph = odf_create_paragraph('Standard', 'Not image / csv')
        document.insert_paragraph(paragraph)

vfs.make_folder('trash')
document.save('trash/use_case1.odt', pretty=True)


