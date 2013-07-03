# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
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
from os import mkdir
from os.path import join, exists

# Import from lpod
from lpod import __version__, __installation_path__
from lpod.document import odf_new_document
from lpod.table import odf_create_cell, odf_create_row
from lpod.table import odf_create_table
from lpod.style import odf_create_table_cell_style
from lpod.style import make_table_cell_border_string
from lpod.style import odf_create_style, rgb2hex

# Hello messages
print 'lpod installation test'
print ' Version           : %s' %  __version__
print ' Installation path : %s' % __installation_path__
print
print 'Generating test_output/use_case3.ods ...'


document = odf_new_document('spreadsheet')
body = document.get_body()
table = odf_create_table(u'use_case3')

for y in xrange(0, 256, 8):
    row = odf_create_row()
    for x in xrange(0, 256, 32):
        cell_value = (x, y, (x+y) % 256 )
        border_rl = make_table_cell_border_string(
                                thick = '0.20cm',
                                color = 'white'
                                )
        border_bt = make_table_cell_border_string(
                                thick = '0.80cm',
                                color = 'white',
                                )
        style = odf_create_table_cell_style(
                                color = 'grey' ,
                                background_color = cell_value,
                                border_right = border_rl,
                                border_left = border_rl,
                                border_bottom = border_bt,
                                border_top = border_bt,
                                )
        name = document.insert_style(style=style, automatic=True)
        cell = odf_create_cell(value=rgb2hex(cell_value), style=name)
        row.append_cell(cell)
    table.append_row(row)

    row_style = odf_create_style('table-row', height='1.80cm')
    name_style_row = document.insert_style(style=row_style, automatic=True)
    for row in table.get_rows():
        row.set_style(name_style_row)
        table.set_row(row.y, row)

    col_style = odf_create_style('table-column', width='3.6cm')
    name = document.insert_style(style=col_style, automatic=True)
    for column in table.get_columns():
        column.set_style(col_style)
        table.set_column(column.x, column)

body.append(table)

if not exists('test_output'):
    mkdir('test_output')
document.save(join('test_output','use_case3.ods'), pretty=True)
