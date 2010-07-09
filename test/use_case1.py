# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from the Standard Library
from csv import reader
from os import listdir, mkdir
from os.path import join, exists
from mimetypes import guess_type

# Import from PIL
from PIL import Image

# Import from lpod
from lpod import __version__, __installation_path__
from lpod.document import odf_new_document_from_type
from lpod.element import FIRST_CHILD
from lpod.frame import odf_create_frame
from lpod.heading import odf_create_heading
from lpod.image import odf_create_image
from lpod.paragraph import odf_create_paragraph
from lpod.table import odf_create_cell, odf_create_row
from lpod.table import odf_create_column, odf_create_table


# Hello messages
print 'lpod installation test'
print ' Version           : %s' %  __version__
print ' Installation path : %s' % __installation_path__
print
print 'Generating test_output/use_case1.odt ...'


# Go
document = odf_new_document_from_type('text')
body = document.get_body()

for numero, filename in enumerate(listdir('samples')):
    # Heading
    heading = odf_create_heading(1, text=unicode(filename, 'utf-8'))
    body.append(heading)
    path = join('samples', filename)
    mimetype, _ = guess_type(path)
    if mimetype is None:
        mimetype = 'application/octet-stream'
    if mimetype.startswith('image/'):
        # Add the image
        internal_name = 'Pictures/' + filename
        image = Image.open(path)
        width, height = image.size
        paragraph = odf_create_paragraph('Standard')
        # 72 ppp
        frame = odf_create_frame('frame_%d' % numero, 'Graphics',
                                 str(width / 72.0) + 'in',
                                 str(height / 72.0) + 'in')
        image = odf_create_image(internal_name)
        frame.append(image)
        paragraph.append(frame)
        body.append(paragraph)

        # And store the data
        container = document.container
        container.set_part(internal_name, open(path).read())
    elif mimetype in ('text/csv', 'text/comma-separated-values'):
        table = odf_create_table(u"table %d" % numero, style=u"Standard")
        csv = reader(open(path))
        for line in csv:
            size = len(line)
            row = odf_create_row()
            for value in line:
                cell = odf_create_cell(value)
                row.append(cell)
            table.append(row)
        for i in xrange(size):
            column = odf_create_column(style=u"Standard")
            table.insert(column, FIRST_CHILD)
        body.append(table)
    else:
        paragraph = odf_create_paragraph(u"Not image / csv",
                style=u"Standard")
        body.append(paragraph)

if not exists('test_output'):
    mkdir('test_output')
document.save('test_output/use_case1.odt', pretty=True)
