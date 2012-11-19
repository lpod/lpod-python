# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
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
from datetime import date, datetime, timedelta
from decimal import Decimal as dec
from cStringIO import StringIO
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.table import _alpha_to_digit, _digit_to_alpha
from lpod.table import _convert_coordinates, odf_cell, odf_row
from lpod.table import odf_create_cell, odf_create_row, odf_create_column
from lpod.table import odf_create_table, import_from_csv, odf_column
from lpod.table import odf_create_named_range, import_from_csv, odf_column


csv_data = '"A float","3.14"\n"A date","1975-05-07"\n'



class TestCoordinates(TestCase):

    def test_digit_to_alpha_to_digit(self):
        for i in range(1024):
            self.assertEqual(_alpha_to_digit(_digit_to_alpha(i)), i)


    def test_alpha_to_digit_digit(self):
        self.assertEqual(_alpha_to_digit(730), 730)


    def test_alpha_to_digit_digit_alphanum(self):
        self.assertRaises(ValueError, _alpha_to_digit, '730')


    def test_digit_to_alpha_digit(self):
        self.assertEqual(_digit_to_alpha('ABC'), 'ABC')


    def test_digit_to_alpha_alphanum(self):
        self.assertRaises(ValueError, _digit_to_alpha, '730')


    def test_convert_coordinates_tuple(self):
        x1, y1 = (12, 34)
        x2, y2 = _convert_coordinates((x1, y1))
        self.assertEqual((x1, y1), (x2, y2))


    def test_convert_coordinates_tuple4(self):
        coord = (12, 34, 15, 60)
        converted = _convert_coordinates(coord)
        self.assertEqual(converted, coord)


    def test_convert_coordinates_alphanum(self):
        x, y = _convert_coordinates('ABC123')
        self.assertEqual((x, y), (730, 122))


    def test_convert_coordinates_alphanum4(self):
        converted = _convert_coordinates('F7:ABC123')
        self.assertEqual(converted, (5, 6, 730, 122))


    def test_convert_coordinates_alphanum4_2(self):
        converted = _convert_coordinates('f7:ABc123')
        self.assertEqual(converted, (5, 6, 730, 122))


    def test_convert_coordinates_alphanum4_3(self):
        converted = _convert_coordinates('f7 : ABc 123 ')
        self.assertEqual(converted, (5, 6, 730, 122))


    def test_convert_coordinates_alphanum4_4(self):
        converted = _convert_coordinates('ABC 123: F7 ')
        self.assertEqual(converted, (730, 122, 5, 6))

    def test_convert_coordinates_bad(self):
        self.assertRaises(ValueError, _convert_coordinates, None)
        self.assertEqual(_convert_coordinates( (None,) ), (None,) )
        self.assertEqual(_convert_coordinates( (None, None) ), (None, None) )
        self.assertEqual(_convert_coordinates( (1, 'bad' ) ), (1, 'bad') )

    def test_convert_coordinates_bad_string(self):
        self.assertEqual(_convert_coordinates( "2B" ),      (None, None) )
        self.assertEqual(_convert_coordinates( "$$$" ),     (None, None) )
        self.assertEqual(_convert_coordinates( "" ),        (None, None) )

    def test_convert_coordinates_std(self):
        self.assertEqual(_convert_coordinates( "A1" ), (0, 0) )
        self.assertEqual(_convert_coordinates( " a 1 " ), (0, 0) )
        self.assertEqual(_convert_coordinates( " aa 1 " ), (26, 0) )

    def test_convert_coordinates_assert(self):
        self.assertRaises(ValueError, _convert_coordinates, "A0" )
        self.assertRaises(ValueError, _convert_coordinates, "A-5" )

    def test_convert_coordinates_big(self):
        self.assertEqual(_convert_coordinates( "AAA200001" ), (26*26+26, 200000) )

    def test_convert_coordinates_partial(self):
        self.assertEqual(_convert_coordinates( "B" ),       (1, None) )
        self.assertEqual(_convert_coordinates( "2" ),       (None, 1) )

    def test_convert_coordinates_partial_4(self):
        self.assertEqual(_convert_coordinates( "B3:D5" ),   (1, 2, 3, 4) )
        self.assertEqual(_convert_coordinates( "B3:" ),     (1, 2, None, None) )
        self.assertEqual(_convert_coordinates( " B  3  :  " ), (1, 2, None, None) )
        self.assertEqual(_convert_coordinates( ":D5" ),     (None, None, 3, 4) )
        self.assertEqual(_convert_coordinates( "  :  D 5  " ), (None, None, 3, 4) )
        self.assertEqual(_convert_coordinates( "C:D" ),     (2, None, 3, None) )
        self.assertEqual(_convert_coordinates( " : D " ),   (None, None, 3, None) )
        self.assertEqual(_convert_coordinates( " C :  " ),  (2, None, None, None) )
        self.assertEqual(_convert_coordinates( "2 : 3 " ),  (None, 1, None, 2) )
        self.assertEqual(_convert_coordinates( "2 :  " ),   (None, 1, None, None) )
        self.assertEqual(_convert_coordinates( " :3  " ),   (None, None, None, 2) )
        self.assertEqual(_convert_coordinates( " :  " ),    (None, None, None, None) )

    def test_convert_coordinates_partial_bad_4(self):
        self.assertEqual(_convert_coordinates( " : $$$ " ), (None, None, None, None) )
        self.assertEqual(_convert_coordinates( " B 3: $$$ " ), (1, 2, None, None) )



class TestCreateCell(TestCase):

    def test_bool(self):
        cell = odf_create_cell(True)
        expected = ('<table:table-cell office:value-type="boolean" '
                      'office:boolean-value="true">'
                      '<text:p>true</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_bool_repr(self):
        cell = odf_create_cell(True, text=u"VRAI")
        expected = ('<table:table-cell office:value-type="boolean" '
                      'office:boolean-value="true">'
                      '<text:p>VRAI</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_int(self):
        cell = odf_create_cell(23)
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="23">'
                      '<text:p>23</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_int_repr(self):
        cell = odf_create_cell(23, text=u"00023")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="23">'
                      '<text:p>00023</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_float(self):
        cell = odf_create_cell(3.141592654)
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="3.141592654">'
                      '<text:p>3.141592654</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_float_repr(self):
        cell = odf_create_cell(3.141592654, text=u"3,14")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="3.141592654">'
                      '<text:p>3,14</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_decimal(self):
        cell = odf_create_cell(dec('2.718281828'))
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="2.718281828">'
                      '<text:p>2.718281828</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_decimal_repr(self):
        cell = odf_create_cell(dec('2.718281828'), text=u"2,72")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="2.718281828">'
                      '<text:p>2,72</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_date(self):
        cell = odf_create_cell(date(2009, 6, 30))
        expected = ('<table:table-cell office:value-type="date" '
                      'office:date-value="2009-06-30">'
                      '<text:p>2009-06-30</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_date_repr(self):
        cell = odf_create_cell(date(2009, 6, 30), text=u"30/6/2009")
        expected = ('<table:table-cell office:value-type="date" '
                      'office:date-value="2009-06-30">'
                      '<text:p>30/6/2009</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_datetime(self):
        cell = odf_create_cell(datetime(2009, 6, 30, 17, 33, 18))
        expected = ('<table:table-cell office:value-type="date" '
                'office:date-value="2009-06-30T17:33:18">'
                      '<text:p>2009-06-30T17:33:18</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_datetime_repr(self):
        cell = odf_create_cell(datetime(2009, 6, 30, 17, 33, 18),
                text=u"30/6/2009 17:33")
        expected = ('<table:table-cell office:value-type="date" '
                'office:date-value="2009-06-30T17:33:18">'
                      '<text:p>30/6/2009 17:33</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_str(self):
        cell = odf_create_cell('red')
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="red">'
                      '<text:p>red</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_str_repr(self):
        cell = odf_create_cell('red', text=u"Red")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="red">'
                      '<text:p>Red</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_unicode(self):
        cell = odf_create_cell(u"Plato")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="Plato">'
                      '<text:p>Plato</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_unicode_repr(self):
        cell = odf_create_cell(u"Plato", text=u"P.")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="Plato">'
                      '<text:p>P.</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_timedelta(self):
        cell = odf_create_cell(timedelta(0, 8))
        expected = ('<table:table-cell office:value-type="time" '
                      'office:time-value="PT00H00M08S">'
                      '<text:p>PT00H00M08S</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_timedelta_repr(self):
        cell = odf_create_cell(timedelta(0, 8), text=u"00:00:08")
        expected = ('<table:table-cell office:value-type="time" '
                      'office:time-value="PT00H00M08S">'
                      '<text:p>00:00:08</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_percentage(self):
        cell = odf_create_cell(90, cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>9000 %</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_percentage_repr(self):
        cell = odf_create_cell(90, text=u"9000 %", cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>9000 %</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_currency(self):
        cell = odf_create_cell(1.54, cell_type='currency', currency='EUR')
        expected = ('<table:table-cell office:value-type="currency" '
                      'office:value="1.54" office:currency="EUR">'
                      '<text:p>1.54</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_currency_repr(self):
        cell = odf_create_cell(1.54, text=u"1,54 €", cell_type='currency',
                currency='EUR')
        expected = ('<table:table-cell office:value-type="currency" '
                      'office:value="1.54" office:currency="EUR">'
                      '<text:p>1,54 &#8364;</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_style(self):
        cell = odf_create_cell(style=u"Monétaire")
        expected = '<table:table-cell table:style-name="Mon&#233;taire"/>'
        self.assertEqual(cell.serialize(), expected)


    def test_bad(self):
        self.assertRaises(TypeError, odf_create_cell, [])



class TestCreateRow(TestCase):

    def test_default(self):
        row = odf_create_row()
        expected = '<table:table-row/>'
        self.assertEqual(row.serialize(), expected)


    def test_width(self):
        row = odf_create_row(1)
        expected = '<table:table-row><table:table-cell/></table:table-row>'
        self.assertEqual(row.serialize(), expected)


    def test_repeated(self):
        row = odf_create_row(repeated=3)
        expected = '<table:table-row table:number-rows-repeated="3"/>'
        self.assertEqual(row.serialize(), expected)


    def test_style(self):
        row = odf_create_row(style=u"ro1")
        expected = '<table:table-row table:style-name="ro1"/>'
        self.assertEqual(row.serialize(), expected)


    def test_all(self):
        row = odf_create_row(1, repeated=3, style=u"ro1")
        expected = ('<table:table-row table:number-rows-repeated="3" '
                      'table:style-name="ro1">'
                      '<table:table-cell/>'
                    '</table:table-row>')
        self.assertEqual(row.serialize(), expected)



class TestCreateColumn(TestCase):

    def test_default(self):
        column = odf_create_column()
        expected = '<table:table-column/>'
        self.assertEqual(column.serialize(), expected)


    def test_default_cell_style(self):
        column = odf_create_column(default_cell_style=u"A Style")
        expected = ('<table:table-column '
                      'table:default-cell-style-name="A Style"/>')
        self.assertEqual(column.serialize(), expected)


    def test_style(self):
        column = odf_create_column(style=u"A Style")
        expected = '<table:table-column table:style-name="A Style"/>'
        self.assertEqual(column.serialize(), expected)


    def test_all(self):
        column =  odf_create_column(style=u"co1",
                default_cell_style="Standard", repeated=3)
        expected = ('<table:table-column '
                      'table:default-cell-style-name="Standard" '
                      'table:number-columns-repeated="3" '
                      'table:style-name="co1"/>')
        self.assertEqual(column.serialize(), expected)



class TestCreateTable(TestCase):

    def test_default(self):
        table = odf_create_table(u"A Table")
        expected = '<table:table table:name="A Table"/>'
        self.assertEqual(table.serialize(), expected)


    def test_bad_name_1(self):
        self.assertRaises(ValueError, odf_create_table, ' ')


    def test_bad_name_2(self):
        self.assertRaises(ValueError, odf_create_table, "ee'ee")


    def test_bad_name_3(self):
        self.assertRaises(ValueError, odf_create_table, 'ee/ee')


    def test_bad_name_4(self):
        self.assertRaises(ValueError, odf_create_table, 'ee\nee')


    def test_width_height(self):
        table = odf_create_table(u"A Table", width=1, height=2)
        expected = ('<table:table table:name="A Table">'
                    '<table:table-column/>'
                    '<table:table-row>'
                      '<table:table-cell/>'
                    '</table:table-row>'
                    '<table:table-row>'
                      '<table:table-cell/>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)


    def test_protected_no_key(self):
        self.assertRaises(ValueError, odf_create_table, u"Protected",
                protected=True)


    def test_protected(self):
        # TODO
        self.assertRaises(NotImplementedError, odf_create_table,
                u"Protected", protected=True, protection_key='1234')


    def test_display(self):
        table = odf_create_table(u"Displayed")
        expected = '<table:table table:name="Displayed"/>'
        self.assertEqual(table.serialize(), expected)


    def test_display_false(self):
        table = odf_create_table(u"Hidden", display=False)
        expected = '<table:table table:name="Hidden" table:display="false"/>'
        self.assertEqual(table.serialize(), expected)


    def test_print(self):
        table = odf_create_table(u"Printable")
        expected = '<table:table table:name="Printable"/>'
        self.assertEqual(table.serialize(), expected)


    def test_print_false(self):
        table = odf_create_table(u"Hidden", printable=False)
        expected = '<table:table table:name="Hidden" table:print="false"/>'
        self.assertEqual(table.serialize(), expected)


    def test_print_ranges_str(self):
        table = odf_create_table(u"Ranges", print_ranges='E6:K12 P6:R12')
        expected = ('<table:table table:name="Ranges" '
                      'table:print-ranges="E6:K12 P6:R12"/>')
        self.assertEqual(table.serialize(), expected)


    def test_print_ranges_list(self):
        table = odf_create_table(u"Ranges",
                print_ranges=['E6:K12', 'P6:R12'])
        expected = ('<table:table table:name="Ranges" '
                      'table:print-ranges="E6:K12 P6:R12"/>')
        self.assertEqual(table.serialize(), expected)


    def test_style(self):
        table = odf_create_table(u"A Table", style=u"A Style")
        expected = ('<table:table table:name="A Table" '
                      'table:style-name="A Style"/>')
        self.assertEqual(table.serialize(), expected)



class TestCell(TestCase):

    def setUp(self):
        self.cell = odf_create_cell(1, repeated=3, style=u"ce1")


    def test_get_cell_value(self):
        self.assertEqual(self.cell.get_value(), 1)
        self.assertEqual(self.cell.get_value(get_type=True), (1, 'float') )


    def test_set_cell_value(self):
        cell = self.cell.clone()
        cell.set_value(u"€")
        self.assertEqual(cell.get_value(), u"€")
        self.assertEqual(cell.get_type(), 'string')
        self.assertEqual(cell.get_value(get_type=True), (u"€", 'string') )


    def test_get_cell_type(self):
        cell = self.cell.clone()
        self.assertEqual(cell.get_type(), 'float')
        cell.set_value(u"€")
        self.assertEqual(cell.get_type(), 'string')


    def test_get_cell_type_percentage(self):
        cell = odf_create_cell(90, cell_type='percentage')
        self.assertEqual(cell.get_type(), 'percentage')
        self.assertEqual(cell.get_value(get_type=True), (90, 'percentage') )
        cell = self.cell.clone()
        cell.set_type('percentage')
        self.assertEqual(cell.get_type(), 'percentage')
        self.assertEqual(cell.get_value(get_type=True), (1, 'percentage') )


    def test_set_cell_type(self):
        cell = self.cell.clone()
        cell.set_type('time')
        self.assertEqual(cell.get_type(), 'time')


    def test_set_cell_type_date(self):
        cell = self.cell.clone()
        cell.set_type('date')
        self.assertEqual(cell.get_type(), 'date')


    def test_get_cell_currency(self):
        cell = odf_create_cell(123, cell_type='currency', currency='EUR')
        self.assertEqual(cell.get_currency(), 'EUR')
        self.assertEqual(cell.get_type(), 'currency')
        self.assertEqual(cell.get_value(get_type=True), (123, 'currency') )


    def test_set_cell_currency(self):
        cell = odf_create_cell(123, cell_type='currency', currency='EUR')
        cell.set_currency('CHF')
        self.assertEqual(cell.get_currency(), 'CHF')


    def test_get_cell_repeated(self):
        self.assertEqual(self.cell.get_repeated(), 3)


    def test_set_cell_repeated(self):
        cell = self.cell.clone()
        cell.set_repeated(99)
        self.assertEqual(cell.get_repeated(), 99)
        cell.set_repeated(1)
        self.assertEqual(cell.get_repeated(), None)
        cell.set_repeated(2)
        self.assertEqual(cell.get_repeated(), 2)
        cell.set_repeated(None)
        self.assertEqual(cell.get_repeated(), None)


    def test_get_cell_style(self):
        self.assertEqual(self.cell.get_style(), u"ce1")


    def test_set_cell_style(self):
        cell = self.cell.clone()
        cell.set_style(u"ce2")
        self.assertEqual(cell.get_style(), u"ce2")
        cell.set_style(None)
        self.assertEqual(cell.get_style(), None)



class TestRow(TestCase):

    def setUp(self):
        row = odf_create_row(width=2, repeated=3, style=u"ro1")
        # Add repeated cell
        row.append(odf_create_cell(1, repeated=2))
        # Add regular cell
        row.append(odf_create_cell(style=u"ce1"))
        self.row = row


    def test_get_row_repeated(self):
        self.assertEqual(self.row.get_repeated(), 3)


    def test_set_row_repeated(self):
        row = self.row.clone()
        row.set_repeated(99)
        self.assertEqual(row.get_repeated(), 99)
        row.set_repeated(1)
        self.assertEqual(row.get_repeated(), None)
        row.set_repeated(2)
        self.assertEqual(row.get_repeated(), 2)
        row.set_repeated(None)
        self.assertEqual(row.get_repeated(), None)


    def test_get_row_style(self):
        self.assertEqual(self.row.get_style(), u"ro1")


    def test_get_row_width(self):
        self.assertEqual(self.row.get_width(), 5)


    def test_traverse_cells(self):
        self.assertEqual(len(list(self.row.traverse())), 5)


    def test_get_cell_values(self):
        self.assertEqual(self.row.get_values(),
                [None, None, 1, 1, None])


    def test_is_empty(self):
        row = odf_create_row(width=100)
        self.assertEqual(row.is_empty(), True)


    def test_is_empty_no(self):
        row = odf_create_row(width=100)
        row.set_value(50, 1)
        self.assertEqual(row.is_empty(), False)


    def test_rstrip(self):
        row = odf_create_row(width=100)
        row.set_value(0, 1)
        row.set_value(1, 2)
        row.set_value(2, 3)
        row.set_cell(3, odf_create_cell(style=u"ce1"))
        row.rstrip()
        self.assertEqual(row.get_width(), 4)



class TestRowCell(TestCase):

#    simpletable :
#      1	1	1	2	3	3	3
#      1	1	1	2	3	3	3       self.row
#      1	1	1	2	3	3	3
#      1    2	3	4	5	6	7

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        table = body.get_table(name=u"Example1").clone()
        self.row_repeats = table.get_row(0)
        self.row = table.get_row(1)


    def test_traverse(self):
        self.assertEqual(len(list(self.row.traverse())), 7)


    def test_traverse_coord(self):
        self.assertEqual(len(list(self.row.traverse(2, None))), 5)
        self.assertEqual(len(list(self.row.traverse(2, 4))), 3)
        self.assertEqual(len(list(self.row.traverse(0, 3))), 4)
        self.assertEqual(len(list(self.row.traverse(0, 55))), 7)
        self.assertEqual(len(list(self.row.traverse(100, 55))), 0)
        self.assertEqual(len(list(self.row.traverse(100, None))), 0)
        self.assertEqual(len(list(self.row.traverse(None, 1))), 2)
        self.assertEqual(len(list(self.row.traverse(-5, 1))), 2)
        self.assertEqual(len(list(self.row.traverse(2, -1))), 0)
        self.assertEqual(len(list(self.row.traverse(-5, -1))), 0)


    def test_get_cells(self):
        self.assertEqual(len(list(self.row.get_cells())), 7)


    def test_get_cells_on_emty_row(self):
        row = odf_create_row()
        self.assertEqual(len(row.get_cells()), 0)
        self.assertEqual(len(row.get_cells((1, 2))), 0)
        self.assertEqual(len(row.get_cells((-2, -3))), 0)
        self.assertEqual(len(row.get_cells((0, 10))), 0)


    def test_get_cells_coord(self):
        coord = (0,8)
        self.assertEqual(len(self.row.get_cells(coord)), 7)
        coord = 'a1:c2'
        self.assertEqual(len(self.row.get_cells(coord)), 3)
        coord = 'a1:a2'
        self.assertEqual(len(self.row.get_cells(coord)), 1)
        coord = 'a1:EE2'
        self.assertEqual(len(self.row.get_cells(coord)), 7)
        coord = 'D1'
        self.assertEqual(len(self.row.get_cells(coord)), 0)
        coord = 'c5:a1'
        self.assertEqual(len(self.row.get_cells(coord)), 0)
        coord = (5,6)
        self.assertEqual(len(self.row.get_cells(coord)), 2)
        coord = (-5, 6)
        self.assertEqual(len(self.row.get_cells(coord)), 5)
        coord = (0, -1)
        self.assertEqual(len(self.row.get_cells(coord)), 7)
        coord = (0, -2)
        self.assertEqual(len(self.row.get_cells(coord)), 6)
        coord = (-1,-1)
        self.assertEqual(len(self.row.get_cells(coord)), 1)
        coord = (1,0)
        self.assertEqual(len(self.row.get_cells(coord)), 0)


    def test_get_cells_regex(self):
        coordinates = [cell.x for cell in self.row.get_cells(content=ur'3')]
        expected = [4, 5, 6]
        self.assertEqual(coordinates, expected)


    def test_get_cells_style(self):
        coordinates = [cell.x
            for cell in self.row.get_cells(style=ur"ce1")]
        expected = [1, 5]
        self.assertEqual(coordinates, expected)


    def test_get_cells_cell_type(self):
        row = self.row.clone()
        cells = row.get_cells(cell_type='all')
        self.assertEqual(len(cells), 7)
        cells = row.get_cells(cell_type='float')
        self.assertEqual(len(cells), 7)
        cells = row.get_cells(cell_type='percentage')
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(cell_type='string')
        self.assertEqual(len(cells), 0)


    def test_get_cells_cell_type2(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        cells = row.get_cells(cell_type='all')
        self.assertEqual(len(cells), 7 + 3 )
        cells = row.get_cells(cell_type='float')
        self.assertEqual(len(cells), 7)
        cells = row.get_cells(cell_type='percentage')
        self.assertEqual(len(cells), 1)
        cells = row.get_cells(cell_type='string')
        self.assertEqual(len(cells), 2)


    def test_get_cells_cell_type_and_coord(self):
        row = self.row.clone()
        cells = row.get_cells(coord=(0, 5), cell_type='all')
        self.assertEqual(len(cells), 6)
        cells = row.get_cells(coord=(0, 5), cell_type='float')
        self.assertEqual(len(cells), 6)
        cells = row.get_cells(coord=(0, 5), cell_type='percentage')
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(coord=(2, 5), cell_type='string')
        self.assertEqual(len(cells), 0)


    def test_get_cells_cell_type_and_coord2(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        cells = row.get_cells(coord=(2, 9), cell_type='all')
        self.assertEqual(len(cells), 8)
        cells = row.get_cells(coord=(3, 9), cell_type='float')
        self.assertEqual(len(cells), 4)
        cells = row.get_cells(coord=(0, 5), cell_type='percentage')
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(coord=(0, 5), cell_type='string')
        self.assertEqual(len(cells), 0)
        cells = row.get_cells(coord=(5, 9), cell_type='percentage')
        self.assertEqual(len(cells), 1)
        cells = row.get_cells(coord=(5, 9), cell_type='string')
        self.assertEqual(len(cells), 2)
        cells = row.get_cells(coord=(8, 9), cell_type='string')
        self.assertEqual(len(cells), 1)


    def test_get_cell_alpha(self):
        row = self.row
        cell_5 = row.get_cell('F')
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.get_text_content(), u"3")
        self.assertEqual(cell_5.get_type(), 'float')
        self.assertEqual(cell_5.get_style(), u"ce1")
        self.assertEqual(cell_5.x, 5)
        self.assertEqual(cell_5.y, 1)


    def test_get_cell_int(self):
        row = self.row
        cell_5 = row.get_cell(5)
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.get_text_content(), u"3")
        self.assertEqual(cell_5.get_type(), 'float')
        self.assertEqual(cell_5.get_style(), u"ce1")


    def test_get_cell_coord(self):
        row = self.row.clone()
        cell = row.get_cell(-1)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(-1 - 7)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3 - 56)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4 - 560)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5 - 7000)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(8)
        self.assertEqual(cell.get_value(), None)
        cell = row.get_cell(1000)
        self.assertEqual(cell.get_value(), None)


    def test_get_value_coord(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell("Appended"))
        value = row.get_value(-1)
        self.assertEqual(value, u'Appended')
        value = row.get_value(-3)
        self.assertEqual(value, 3)
        value = row.get_value(-4)
        self.assertEqual(value, 3)
        value = row.get_value(-5)
        self.assertEqual(value, 2)
        value = row.get_value(-1 - 8)
        self.assertEqual(value, u'Appended')
        value = row.get_value(7)
        self.assertEqual(value, u'Appended')
        value = row.get_value(8)
        self.assertEqual(value, None)
        value = row.get_value(1000)
        self.assertEqual(value, None)


    def test_get_value_coord_with_get_type(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell("Appended"))
        value = row.get_value(-1, get_type=True)
        self.assertEqual(value, (u'Appended', u'string'))
        value = row.get_value(-3, get_type=True)
        self.assertEqual(value, (3, u'float'))
        value = row.get_value(-4, get_type=True)
        self.assertEqual(value, (3, u'float'))
        value = row.get_value(-5, get_type=True)
        self.assertEqual(value, (2, u'float'))
        value = row.get_value(-1 - 8, get_type=True)
        self.assertEqual(value, (u'Appended', u'string'))
        value = row.get_value(7, get_type=True)
        self.assertEqual(value, (u'Appended', u'string'))
        value = row.get_value(8, get_type=True)
        self.assertEqual(value, (None, None))
        value = row.get_value(1000, get_type=True)
        self.assertEqual(value, (None, None))


    def test_set_cell(self):
        row = self.row.clone()
        row.set_value(1, 3.14)
        self.assertEqual(row.get_values(),
                [1, dec('3.14'), 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cell_far_away(self):
        row = self.row.clone()
        row.set_value(7 + 3, 3.14)
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, 3, None, None, None, dec('3.14')])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 11)


    def test_set_cell_repeat(self):
        row = self.row_repeats.clone()
        row.set_value(1, 3.14)
        self.assertEqual(row.get_values(),
                [1, dec('3.14'), 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cell_repeat_repeat(self):
        row = self.row_repeats.clone()
        cell = odf_create_cell(value=20, repeated=2)
        row.set_cell(1, cell)
        self.assertEqual(row.get_values(),
                [1, 20, 20, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_insert(self):
        row = self.row.clone()
        cell = row.insert_cell(3)
        self.assert_(type(cell) is odf_cell)
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 1)


    def test_insert_cell(self):
        row = self.row.clone()
        cell = row.insert_cell(3, odf_create_cell(u"Inserted"))
        self.assertEqual(row.get_width(), 8)
        self.assertEqual(row.get_values(),
                [1, 1, 1, u"Inserted", 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 1)


    def test_insert_cell_repeat(self):
        row = self.row_repeats.clone()
        cell = row.insert_cell(6, odf_create_cell(u"Inserted"))
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, u"Inserted", 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)
        self.assertEqual(cell.x, 6)
        self.assertEqual(cell.y, 0)


    def test_insert_cell_repeat_repeat(self):
        row = self.row_repeats.clone()
        cell = row.insert_cell(6, odf_create_cell(u"Inserted", repeated=3))
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, u"Inserted", u"Inserted", u"Inserted", 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 10)
        self.assertEqual(cell.x, 6)
        self.assertEqual(cell.y, 0)


    def test_insert_cell_repeat_repeat_bis(self):
        row = self.row_repeats.clone()
        cell = row.insert_cell(1, odf_create_cell(u"Inserted", repeated=2))
        self.assertEqual(row.get_values(),
                [1, u"Inserted", u"Inserted", 1, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 9)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 0)


    def test_append_cell(self):
        row = self.row.clone()
        cell = row.append_cell()
        self.assert_(type(cell) is odf_cell)
        self.assertEqual(cell.x, self.row.get_width() )
        self.assertEqual(cell.y, 1)


    def test_append_cell2(self):
        row = self.row.clone()
        cell = row.append_cell(odf_create_cell(u"Appended"))
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, 3, u"Appended"])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)
        self.assertEqual(cell.x, self.row.get_width() )
        self.assertEqual(cell.y, 1)


    def test_delete_cell(self):
        row = self.row.clone()
        row.delete_cell(3)
        self.assertEqual(row.get_values(), [1, 1, 1, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 6)


    def test_delete_cell_repeat(self):
        row = self.row_repeats.clone()
        row.delete_cell(-1)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 6)


    def test_set_cells_1(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10)]
        row.set_cells(cells)
        self.assertEqual(row.get_values(),
                [10, 1, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_2(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10),
                    odf_create_cell(value=20)]
        row.set_cells(cells)
        self.assertEqual(row.get_values(),
                [10, 20, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_many(self):
        row = self.row.clone()
        cells = []
        for i in range(10):
            cells.append(odf_create_cell(value=10*i))
        row.set_cells(cells)
        self.assertEqual(row.get_values(),
                [0, 10, 20,  30, 40, 50, 60, 70, 80, 90])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 10)


    def test_set_cells_1_start_1(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(),
                [1, 10, 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_1_start_m_2(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10)]
        row.set_cells(cells, -2)
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 10, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_1_start_m_6(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10)]
        row.set_cells(cells, 6)
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, 10])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_1_start_m_9(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10)]
        row.set_cells(cells, 9)
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, 3, None, None, 10])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 10)


    def test_set_cells_2_start_1(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10),
                    odf_create_cell(value=20)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(),
                [1, 10, 20, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_many_start_5(self):
        row = self.row.clone()
        cells = []
        for i in range(5):
            cells.append(odf_create_cell(value=10*i))
        row.set_cells(cells, 5)
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 0, 10, 20, 30, 40])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 10)


    def test_set_cells_many_start_far(self):
        row = self.row.clone()
        cells = []
        for i in range(5):
            cells.append(odf_create_cell(value=10*i))
        row.set_cells(cells, 9)
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, 3, None, None, 0, 10, 20, 30, 40])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 14)


    def test_set_cells_3_start_1_repeats(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10, repeated = 2)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(),
                [1, 10, 10, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_3_start_1_repeats_2(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10, repeated = 2),
                    odf_create_cell(value=20)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(),
                [1, 10, 10, 20, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_3_start_1_repeats_3(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10, repeated = 2),
                    odf_create_cell(value=20),
                    odf_create_cell(value=30, repeated = 2)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(),
                [1, 10, 10, 20, 30, 30, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cells_3_start_1_repeats_4(self):
        row = self.row.clone()
        cells = [odf_create_cell(value=10, repeated = 2),
                    odf_create_cell(value=20),
                    odf_create_cell(value=30, repeated = 4)]
        row.set_cells(cells, 1)
        self.assertEqual(row.get_values(),
                [1, 10, 10, 20, 30, 30, 30, 30])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)


    def test_set_values_empty(self):
        row = odf_create_row()
        row.set_values([1, 2, 3, 4])
        self.assertEqual(row.get_width(), 4)
        self.assertEqual(row.get_values(), [1, 2, 3, 4])


    def test_set_values_on_row(self):
        row = self.row.clone()
        row.set_values([10, 20, 30, u'4'])
        self.assertEqual(row.get_width(), 7)
        self.assertEqual(row.get_values(), [10, 20, 30, u'4', 3, 3, 3])


    def test_set_values_on_row2(self):
        row = self.row.clone()
        row.set_values([10, 20, 30, u'4'], start = 2)
        self.assertEqual(row.get_width(), 7)
        self.assertEqual(row.get_values(), [1, 1, 10, 20, 30, u'4', 3])


    def test_set_values_on_row3(self):
        row = self.row.clone()
        row.set_values([10, 20, 30, u'4'], start = 2)
        self.assertEqual(row.get_width(), 7)
        self.assertEqual(row.get_values(), [1, 1, 10, 20, 30, u'4', 3])


    def test_set_values_on_row4(self):
        row = self.row.clone()
        row.set_values([10, 20, 30, u'4'], start = -2)
        self.assertEqual(row.get_width(), 9)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 10, 20, 30, u'4'])


    def test_set_values_on_row5(self):
        row = self.row.clone()
        row.set_values([10, 20, 30, u'4'], start = 8)
        self.assertEqual(row.get_width(), 7 + 1 + 4)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 3, 3, 3, None,
                                            10, 20, 30, u'4'])

    def test_set_values_on_row6(self):
        row = self.row.clone()
        row.set_values([10, 20, 30, 40, 50, 60, 70, 80], start = 0)
        self.assertEqual(row.get_width(), 8)
        self.assertEqual(row.get_values(), [10, 20, 30, 40, 50, 60, 70, 80])


    def test_set_values_on_row_percentage(self):
        row = self.row.clone()
        row.set_values([10, 20], start=4, cell_type='percentage')
        self.assertEqual(row.get_width(), 7)
        self.assertEqual(row.get_values(), [1, 1, 1, 2, 10, 20, 3])
        self.assertEqual(row.get_values(get_type=True, cell_type='percentage'),
                         [(10, u'percentage'), (20, u'percentage')])


    def test_set_values_on_row_style(self):
        row = self.row.clone()
        row.set_values([10, 20], start=3, style='bold')
        self.assertEqual(row.get_width(), 7)
        self.assertEqual(row.get_values(), [1, 1, 1, 10, 20, 3, 3])
        self.assertEqual(row.get_cell(4).get_style(), u'bold')


    def test_set_values_on_row_curency(self):
        row = self.row.clone()
        row.set_values([10, 20], start=3,
                cell_type=u'currency', currency=u'EUR')
        self.assertEqual(row.get_width(), 7)
        self.assertEqual(row.get_values(), [1, 1, 1, 10, 20, 3, 3])
        self.assertEqual(row.get_cell(4).get_value(get_type=True), (20, u'currency'))
        self.assertEqual(row.get_cell(4).get_currency(), 'EUR')



class TestRowCellGetValues(TestCase):

#    simpletable :
#      1	1	1	2	3	3	3
#      1	1	1	2	3	3	3       self.row
#      1	1	1	2	3	3	3
#      1    2	3	4	5	6	7

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        table = body.get_table(name=u"Example1").clone()
        self.row_repeats = table.get_row(0)
        self.row = table.get_row(1)


    def test_on_empty_row(self):
        row = odf_create_row()
        self.assertEqual(row.get_values(), [])
        self.assertEqual(row.get_values(complete=True), [])
        self.assertEqual(row.get_values(complete=True, get_type=True), [])
        self.assertEqual(row.get_values((0,10)), [])
        self.assertEqual(row.get_values(cell_type='all'), [])
        self.assertEqual(row.get_values(cell_type='All'), [])
        self.assertEqual(row.get_values((2,3), complete=True), [])


    def test_get_values_count(self):
        self.assertEqual(len(self.row.get_values()), 7)


    def test_get_values_coord(self):
        coord = (0,8)
        self.assertEqual(len(self.row.get_values(coord)), 7)
        coord = 'a1:c2'
        self.assertEqual(len(self.row.get_values(coord)), 3)
        coord = 'a1:a2'
        self.assertEqual(len(self.row.get_values(coord)), 1)
        coord = 'a1:EE2'
        self.assertEqual(len(self.row.get_values(coord)), 7)
        coord = 'D1'
        self.assertEqual(len(self.row.get_values(coord)), 0)
        coord = 'c5:a1'
        self.assertEqual(len(self.row.get_values(coord)), 0)
        coord = (5,6)
        self.assertEqual(len(self.row.get_values(coord)), 2)
        coord = (-5, 6)
        self.assertEqual(len(self.row.get_values(coord)), 5)
        coord = (0, -1)
        self.assertEqual(len(self.row.get_values(coord)), 7)
        coord = (0, -2)
        self.assertEqual(len(self.row.get_values(coord)), 6)
        coord = (-1,-1)
        self.assertEqual(len(self.row.get_values(coord)), 1)
        coord = (1,0)
        self.assertEqual(len(self.row.get_values(coord)), 0)


    def test_get_values_cell_type(self):
        row = self.row.clone()
        values = row.get_values(cell_type='all')
        self.assertEqual(len(values), 7)
        values = row.get_values(cell_type='float')
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type='percentage')
        self.assertEqual(len(values), 0)
        values = row.get_values(cell_type='string')
        self.assertEqual(len(values), 0)


    def test_get_values_cell_type2(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        values = row.get_values(cell_type='all')
        self.assertEqual(len(values), 7 + 3 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2"])
        values = row.get_values(cell_type='float')
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type='percentage')
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type='string')
        self.assertEqual(len(values), 2)
        self.assertEqual(values, [u"bob", u"bob2"])


    def test_get_values_cell_type2_with_hole(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        values = row.get_values(cell_type='all') # aka all non empty
        self.assertEqual(len(values), 11 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  u"far"])
        values = row.get_values() # difference when requestion everything
        self.assertEqual(len(values), 13 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(cell_type='float')
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type='percentage')
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type='string')
        self.assertEqual(len(values), 3)
        self.assertEqual(values, [u"bob", u"bob2", u"far"])
        values = row.get_values(":") # requesting everything
        self.assertEqual(len(values), 13 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(cell_type='float')
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type='percentage')
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type='string')
        self.assertEqual(len(values), 3)
        self.assertEqual(values, [u"bob", u"bob2", u"far"])
        values = row.get_values(":") # requesting everything
        self.assertEqual(len(values), 13 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(cell_type='float')
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type='percentage')
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type='string')
        self.assertEqual(len(values), 3)
        self.assertEqual(values, [u"bob", u"bob2", u"far"])
        values = row.get_values("") # requesting everything 2
        self.assertEqual(len(values), 13 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(cell_type='float')
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = row.get_values(cell_type='percentage')
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [14])
        values = row.get_values(cell_type='string')
        self.assertEqual(len(values), 3)
        self.assertEqual(values, [u"bob", u"bob2", u"far"])

    def test_get_values_cell_type2_with_hole_and_get_type(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        values = row.get_values(cell_type='all',  # aka all non empty
                                get_type=True)
        self.assertEqual(len(values), 11 )
        self.assertEqual(values, [(1, u"float"), (1, u"float"), (1, u"float"),
                                (2, u"float"), (3, u"float"),
                                (3, u"float"), (3, u"float"),
                                (u"bob", u"string"), (14, u"percentage"),
                                (u"bob2", u"string"),
                                (u"far", u"string")])
        values = row.get_values(get_type=True) # difference when  everything
        self.assertEqual(len(values), 13 )
        self.assertEqual(values, [(1, u"float"), (1, u"float"), (1, u"float"),
                                (2, u"float"), (3, u"float"),
                                (3, u"float"), (3, u"float"),
                                (u"bob", u"string"), (14, u"percentage"),
                                (u"bob2", u"string"),
                                (None, None), (None,None),
                                (u"far", u"string")])
        values = row.get_values(cell_type='float' ,get_type=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [(1, u"float"), (1, u"float"), (1, u"float"),
                                (2, u"float"), (3, u"float"),
                                (3, u"float"), (3, u"float")])
        values = row.get_values(cell_type='percentage', get_type=True)
        self.assertEqual(len(values), 1)
        self.assertEqual(values, [(14, u"percentage")])
        values = row.get_values(cell_type='string', get_type=True)
        self.assertEqual(len(values), 3)
        self.assertEqual(values, [(u"bob", u"string"),
                                (u"bob2", u"string"),
                                (u"far", u"string")])


    def test_get_values_cell_type2_complete(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        values = row.get_values(cell_type='ALL', complete=True)
        self.assertEqual(len(values), 13 )
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(cell_type='FLOAT', complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3, None, None, None,
                                  None, None, None])
        values = row.get_values(cell_type='percentage', complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(values, [None, None, None, None, None, None, None,
                                  None, 14, None, None, None, None])
        values = row.get_values(cell_type='string', complete=True)
        self.assertEqual(len(values), 13)
        self.assertEqual(values, [None, None, None, None, None, None, None,
                                  u"bob", None, u"bob2", None, None, u"far"])


    def test_get_values_cell_type_and_coord(self):
        row = self.row.clone()
        values = row.get_values(coord=(0, 5), cell_type='all')
        self.assertEqual(len(values), 6)
        values = row.get_values(coord=(0, 5), cell_type='float')
        self.assertEqual(len(values), 6)
        values = row.get_values(coord=(0, 5), cell_type='percentage')
        self.assertEqual(len(values), 0)
        values = row.get_values(coord=(2, 5), cell_type='string')
        self.assertEqual(len(values), 0)



    def test_get_values_cell_type_and_coord_strange(self):
        row = self.row.clone()
        values = row.get_values(coord='A:F', cell_type='all')
        self.assertEqual(len(values), 6)
        values = row.get_values(coord='C:', cell_type='all')
        self.assertEqual(len(values), 5)
        values = row.get_values(coord='A : f', cell_type='float')
        self.assertEqual(len(values), 6)
        values = row.get_values(coord='A:F', cell_type='percentage')
        self.assertEqual(len(values), 0)
        values = row.get_values(coord='C:F', cell_type='string')
        self.assertEqual(len(values), 0)


    def test_get_values_cell_type_and_coord_strange_long(self):
        row = self.row.clone()
        values = row.get_values(coord='A8:F2', cell_type='all')
        self.assertEqual(len(values), 6)
        values = row.get_values(coord='C5:', cell_type='all')
        self.assertEqual(len(values), 5)
        values = row.get_values(coord='C5:99', cell_type='all')
        self.assertEqual(len(values), 5)
        values = row.get_values(coord='A2 : f', cell_type='float')
        self.assertEqual(len(values), 6)
        values = row.get_values(coord='A:F5', cell_type='percentage')
        self.assertEqual(len(values), 0)
        values = row.get_values(coord='C:F4', cell_type='string')
        self.assertEqual(len(values), 0)


    def test_get_values_cell_type_and_coord_and_get_type(self):
        row = self.row.clone()
        values = row.get_values(coord=(0, 5), cell_type='all',
                                get_type=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [(1, u"float"), (1, u"float"),
                                (1, u"float"), (2, u"float"),
                                (3, u"float"), (3, u"float")])
        values = row.get_values(coord=(0, 5), cell_type='float',
                                get_type=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [(1, u"float"), (1, u"float"),
                                (1, u"float"), (2, u"float"),
                                (3, u"float"), (3, u"float")])
        values = row.get_values(coord=(0, 5), cell_type='percentage',
                                get_type=True)
        self.assertEqual(len(values), 0)
        values = row.get_values(coord=(2, 5), cell_type='string',
                                get_type=True)
        self.assertEqual(len(values), 0)


    def test_get_values_cell_type_and_coord_and_complete(self):
        row = self.row.clone()
        values = row.get_values(coord=(0, 5), cell_type='all',
                                complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3])
        values = row.get_values(coord=(0, 5), cell_type='float',
                                complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3])
        values = row.get_values(coord=(0, 5), cell_type='percentage',
                                complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [None, None, None, None, None, None])
        values = row.get_values(coord=(2, 5), cell_type='string',
                                complete=True)
        self.assertEqual(len(values), 4)
        self.assertEqual(values, [None, None, None, None])


    def test_get_values_cell_type_and_coord2_and_complete(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False )
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        values = row.get_values(coord=(2, 20), cell_type='all',
                                complete=True)
        self.assertEqual(len(values), 11)
        self.assertEqual(values, [1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(coord=(2, 11), cell_type='all',
                                complete=True)
        self.assertEqual(len(values), 10)
        self.assertEqual(values, [1, 2, 3, 3, 3, u"bob", 14, u"bob2",
                                  None, None])
        values = row.get_values(coord=(3, 12), cell_type='float',
                                complete=True)
        self.assertEqual(len(values), 10)
        self.assertEqual(values, [2, 3, 3, 3, None, None, None,
                                  None, None, None])
        values = row.get_values(coord=(0, 5), cell_type='percentage',
                                complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [None, None, None, None, None, None])
        values = row.get_values(coord=(0, 5), cell_type='string',
                                complete=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [None, None, None, None, None, None])
        values = row.get_values(coord=(5, 11), cell_type='percentage',
                                complete=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [None, None, None, 14, None, None, None])
        values = row.get_values(coord=(6, 12), cell_type='string',
                                complete=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [None, u"bob", None, u"bob2",
                                  None, None, u"far"])
        values = row.get_values(coord=(8, 20), cell_type='string',
                                complete=True)
        self.assertEqual(len(values), 5)
        self.assertEqual(values, [None, u"bob2",
                                  None, None, u"far"])


    def test_get_values_cell_type_and_coord2_and_complete_and_get_type(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False )
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        values = row.get_values(coord=(2, 20), cell_type='all',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 11)
        self.assertEqual(values, [(1, u"float"), (2, u"float"), (3, u"float"),
                                (3, u"float"), (3, u"float"),
                                (u"bob", u"string"), (14, u"percentage"),
                                (u"bob2", u"string"),
                                (None, None), (None,None),
                                (u"far", u"string")])
        values = row.get_values(coord=(2, 11), cell_type='all',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 10)
        self.assertEqual(values, [(1, u"float"), (2, u"float"), (3, u"float"),
                                (3, u"float"), (3, u"float"),
                                (u"bob", u"string"), (14, u"percentage"),
                                (u"bob2", u"string"),
                                (None, None), (None,None)])
        values = row.get_values(coord=(3, 12), cell_type='float',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 10)
        self.assertEqual(values, [(2, u"float"), (3, u"float"),
                                (3, u"float"), (3, u"float"),
                                (None, None), (None,None),
                                (None, None), (None,None),
                                (None, None), (None,None)])
        values = row.get_values(coord=(0, 5), cell_type='percentage',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [(None, None), (None,None),
                                (None, None), (None,None),
                                (None, None), (None,None)])
        values = row.get_values(coord=(0, 5), cell_type='string',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 6)
        self.assertEqual(values, [(None, None), (None,None),
                                (None, None), (None,None),
                                (None, None), (None,None)])
        values = row.get_values(coord=(5, 11), cell_type='percentage',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [(None, None), (None,None),
                                (None, None), (14, u"percentage"), (None,None),
                                (None, None), (None,None)])
        values = row.get_values(coord=(6, 12), cell_type='string',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 7)
        self.assertEqual(values, [(None, None), (u"bob", u"string"),
                                (None, None), (u"bob2", u"string"),
                                (None, None), (None, None),
                                (u"far", u"string")])
        values = row.get_values(coord=(8, 20), cell_type='string',
                                complete=True, get_type=True)
        self.assertEqual(len(values), 5)
        self.assertEqual(values, [(None, None), (u"bob2", u"string"),
                                  (None, None), (None, None),
                                  (u"far", u"string")])


    def test_get_cell_alpha(self):
        row = self.row
        cell_5 = row.get_cell('F')
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.get_text_content(), u"3")
        self.assertEqual(cell_5.get_type(), 'float')
        self.assertEqual(cell_5.get_style(), u"ce1")
        self.assertEqual(cell_5.x, 5)
        self.assertEqual(cell_5.y, 1)


    def test_get_cell_int(self):
        row = self.row
        cell_5 = row.get_cell(5)
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.get_text_content(), u"3")
        self.assertEqual(cell_5.get_type(), 'float')
        self.assertEqual(cell_5.get_style(), u"ce1")


    def test_get_cell_coord(self):
        row = self.row.clone()
        cell = row.get_cell(-1)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(-1 - 7)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-3 - 56)
        self.assertEqual(cell.get_value(), 3)
        cell = row.get_cell(-4 - 560)
        self.assertEqual(cell.get_value(), 2)
        cell = row.get_cell(-5 - 7000)
        self.assertEqual(cell.get_value(), 1)
        cell = row.get_cell(8)
        self.assertEqual(cell.get_value(), None)
        cell = row.get_cell(1000)
        self.assertEqual(cell.get_value(), None)


    def test_get_value_coord(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell("Appended"))
        value = row.get_value(-1)
        self.assertEqual(value, u'Appended')
        value = row.get_value(-3)
        self.assertEqual(value, 3)
        value = row.get_value(-4)
        self.assertEqual(value, 3)
        value = row.get_value(-5)
        self.assertEqual(value, 2)
        value = row.get_value(-1 - 8)
        self.assertEqual(value, u'Appended')
        value = row.get_value(7)
        self.assertEqual(value, u'Appended')
        value = row.get_value(8)
        self.assertEqual(value, None)
        value = row.get_value(1000)
        self.assertEqual(value, None)


    def test_get_value_coord_with_get_type(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell("Appended"))
        value = row.get_value(-1, get_type=True)
        self.assertEqual(value, (u'Appended', u'string'))
        value = row.get_value(-3, get_type=True)
        self.assertEqual(value, (3, u'float'))
        value = row.get_value(-4, get_type=True)
        self.assertEqual(value, (3, u'float'))
        value = row.get_value(-5, get_type=True)
        self.assertEqual(value, (2, u'float'))
        value = row.get_value(-1 - 8, get_type=True)
        self.assertEqual(value, (u'Appended', u'string'))
        value = row.get_value(7, get_type=True)
        self.assertEqual(value, (u'Appended', u'string'))
        value = row.get_value(8, get_type=True)
        self.assertEqual(value, (None, None))
        value = row.get_value(1000, get_type=True)
        self.assertEqual(value, (None, None))



class TestColumn(TestCase):

    def setUp(self):
        self.column = odf_create_column(default_cell_style=u"ce1",
                repeated=7, style=u"co1")


    def test_get_column_default_cell_style(self):
        self.assertEqual(self.column.get_default_cell_style(), u"ce1")


    def test_set_column_default_cell_style(self):
        column = self.column.clone()
        column.set_default_cell_style(u"ce2")
        self.assertEqual(column.get_default_cell_style(), u"ce2")
        column.set_default_cell_style(None)
        self.assertEqual(column.get_default_cell_style(), None)


    def test_get_column_repeated(self):
        self.assertEqual(self.column.get_repeated(), 7)


    def test_set_column_repeated(self):
        column = self.column.clone()
        column.set_repeated(99)
        self.assertEqual(column.get_repeated(), 99)
        column.set_repeated(1)
        self.assertEqual(column.get_repeated(), None)
        column.set_repeated(2)
        self.assertEqual(column.get_repeated(), 2)
        column.set_repeated(None)
        self.assertEqual(column.get_repeated(), None)


    def test_get_column_style(self):
        self.assertEqual(self.column.get_style(), u"co1")


    def test_set_column_style(self):
        column = self.column.clone()
        column.set_style(u"co2")
        self.assertEqual(column.get_style(), u"co2")
        column.set_style(None)
        self.assertEqual(column.get_style(), None)



class TestTable(TestCase):
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        self.body = body = document.get_body()
        self.table = body.get_table(name=u"Example1")


    def test_get_table_list(self):
        body = self.body
        self.assertEqual(len(body.get_tables()), 3)


    def test_get_table_list_style(self):
        body = self.body
        self.assertEqual(len(body.get_tables(style=u"ta1")), 3)


    def test_get_table_by_name(self):
        body = self.body.clone()
        name = u"New Table"
        body.append(odf_create_table(name))
        table = body.get_table(name=name)
        self.assertEqual(table.get_name(), name)


    def test_get_table_by_position(self):
        body = self.body.clone()
        body.append(odf_create_table(u"New Table"))
        table = body.get_table(position=3)
        self.assertEqual(table.get_name(), u"New Table")


    def test_get_table_style(self):
        self.assertEqual(self.table.get_style(), u"ta1")


    def test_get_table_printable(self):
        self.assertEqual(self.table.get_printable(), False)


    def test_get_table_width(self):
        self.assertEqual(self.table.get_width(), 7)


    def test_get_table_height(self):
        self.assertEqual(self.table.get_height(), 4)


    def test_get_table_size(self):
        self.assertEqual(self.table.get_size(), (7, 4))


    def test_get_table_size_empty(self):
        table = odf_create_table(u"Empty")
        self.assertEqual(table.get_size(), (0, 0))


    def test_get_table_width_after(self):
        table = odf_create_table(u"Empty")
        self.assertEqual(table.get_width(), 0)
        self.assertEqual(table.get_height(), 0)
        # The first row creates the columns
        table.append_row(odf_create_row(width=5))
        self.assertEqual(table.get_width(), 5)
        self.assertEqual(table.get_height(), 1)
        # The subsequent ones don't
        table.append_row(odf_create_row(width=5))
        self.assertEqual(table.get_width(), 5)
        self.assertEqual(table.get_height(), 2)


    def test_get_values(self):
        self.assertEqual(self.table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])


    def test_set_table_values_with_clear(self):
        table = self.table.clone()
        values = [[u"a", u"b", u"c", u"d", u"e", u"f", u"g"],
                  [u"h", u"i", u"j", u"k", u"l", u"m", u"n"],
                  [u"o", u"p", u"q", u"r", u"s", u"t", u"u"],
                  [u"v", u"w", u"x", u"y", u"z", u"aa", u"ab"]]
        table.clear()
        table.set_values(values)
        self.assertEqual(table.get_values(), values)


    def test_set_table_values_big(self):
        table = self.table.clone()
        values = [[u"a", u"b", u"c", u"d", u"e", u"f", u"g"],
                  [u"h", u"i", u"j", u"k", u"l", u"m", u"n"],
                  [u"o", u"p", u"q", u"r", u"s", u"t", u"u"],
                  [u"o", u"p", u"q", u"r", u"s", u"t", u"u"],
                  [u"o", u"p", u"q", u"r", u"s", u"t", u"u"],
                  [u"o", u"p", u"q", u"r", u"s", u"t", u"u"],
                  [u"v", u"w", u"x", u"y", u"z", u"aa", u"ab"],
                  [u"v", u"w", u"x", u"y", u"z", u"aa", u"ab"]]
        table.set_values(values)
        self.assertEqual(table.get_values(), values)
        self.assertEqual(table.get_size(), (7, 8))


    def test_set_table_values_small(self):
        table = self.table.clone()
        values = [[u"a", u"b", u"c"],
                  [u"h", u"i", u"j", u"k", u"l", u"m", u"n"],
                  [u"o", u"p", None, None, u"s", u"t", u"u"]]
        table.set_values(values)
        self.assertEqual(table.get_size(), (7, 4))
        self.assertEqual(table.get_values(),
                    [[u'a', u'b', u'c', 2, 3, 3, 3],
                    [u'h', u'i', u'j', u'k', u'l', u'm', u'n'],
                    [u'o', u'p', None, None, u's', u't', u'u'],
                    [1, 2, 3, 4, 5, 6, 7]])


    def test_set_table_values_small_coord(self):
        table = self.table.clone()
        values = [[u"a", u"b", u"c"],
                  [u"h", u"i", u"j", u"k", u"l", u"m", u"n"],
                  [u"o", u"p", None, None, u"s", u"t", u"u"]]
        table.set_values(values, coord=("c2"))
        self.assertEqual(table.get_size(), (9, 4))
        self.assertEqual(table.get_values(),
                    [[1, 1, 1, 2, 3, 3, 3, None, None],
                    [1, 1, u'a', u'b', u'c', 3, 3, None, None],
                    [1, 1, u'h', u'i', u'j', u'k', u'l', u'm', u'n'],
                    [1, 2, u'o', u'p', None, None, u's', u't', u'u']])


    def test_set_table_values_small_coord_far(self):
        table = self.table.clone()
        values = [[u"a", u"b", u"c"],
                  [u"h", None ],
                  [u"o" ]]
        table.set_values(values, coord=("J6"))
        self.assertEqual(table.get_size(), (12, 8))
        self.assertEqual(table.get_values(),
                    [[1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                    [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                    [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                    [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None,
                     None, None, None],
                    [None, None, None, None, None, None, None, None, None,
                     u'a', u'b', u'c'],
                    [None, None, None, None, None, None, None, None, None,
                     u'h', None, None],
                    [None, None, None, None, None, None, None, None, None,
                     u'o', None, None]])


    def test_set_table_values_small_type(self):
        table = self.table.clone()
        values = [[10, None, 30],
                  [None, 40 ]]
        table.set_values(values, coord=("C4"), cell_type = 'percentage')
        self.assertEqual(table.get_size(), (7, 5))
        self.assertEqual(table.get_values(),
                    [[1, 1, 1, 2, 3, 3, 3],
                    [1, 1, 1, 2, 3, 3, 3],
                    [1, 1, 1, 2, 3, 3, 3],
                    [1, 2, 10, None, 30, 6, 7],
                    [None, None, None, 40, None, None, None]])
        self.assertEqual(table.get_values(coord='4:', get_type=True),
                    [[(1, u'float'), (2, u'float'),
                    (10, u'percentage'), (None, None), (30, u'percentage'),
                        (6, u'float'), (7, u'float')],
                    [(None, None), (None, None), (None, None),
                        (40, u'percentage'), (None, None), (None, None),
                        (None, None)]])


    def test_rstrip_table(self):
        document = odf_get_document('samples/styled_table.ods')
        table = document.get_body().get_table(name=u'Feuille1').clone()
        table.rstrip()
        self.assertEqual(table.get_size(), (5, 9))

# simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7

    def test_table_transpose(self):
        table = self.table.clone()
        table.transpose()
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 1],
                 [1, 1, 1, 2],
                 [1, 1, 1, 3],
                 [2, 2, 2, 4],
                 [3, 3, 3, 5],
                 [3, 3, 3, 6],
                 [3, 3, 3, 7]])


    def test_table_transpose_2(self):
        table = self.table.clone()
        table.transpose("A1:G1")
        self.assertEqual(table.get_values(),
               [[1, None, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3],
                [1, 1, 1, 2, 3, 3, 3],
                [2, 2, 3, 4, 5, 6, 7],
                [3, None, None, None, None, None, None],
                [3, None, None, None, None, None, None],
                [3, None, None, None, None, None, None]])


    def test_table_transpose_3(self):
        table = self.table.clone()
        table.delete_row(3)
        table.delete_row(2)
        table.delete_row(1)
        table.transpose()
        self.assertEqual(table.get_values(),
               [[1], [1], [1], [2], [3], [3], [3]])


    def test_table_transpose_4(self):
        table = self.table.clone()
        table.transpose("F2:F4")
        self.assertEqual(table.get_values(),
               [[1, 1, 1, 2, 3, 3,    3,   None],
                [1, 1, 1, 2, 3, 3,    3,   6],
                [1, 1, 1, 2, 3, None, 3,   None],
                [1, 2, 3, 4, 5, None, 7,   None]])



class TestTableCellSpan(TestCase):
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        self.body = body = document.get_body()
        self.table = body.get_table(name=u"Example1")
        self.table2 = self.table.clone()
        self.table2.set_value('a1', 'a')
        self.table2.set_value('b1', 'b')
        self.table2.set_value('d1', 'd')
        self.table2.set_value('b2', '')
        self.table2.set_value('c2', 'C')
        self.table2.set_value('d2', '')


    def test_span_bad1(self):
        table = self.table.clone()
        self.assertEqual(table.set_span('a1:a1'), False)


    def test_span_sp1(self):
        table = self.table.clone()
        table.set_span('a1:a2')
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        for coord in ('a1', 'a2'):
            self.assertEqual(table.get_cell(coord)._is_spanned(), True)
        for coord in ('b1', 'b2', 'a3'):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)
        self.assertEqual(table.set_span('a1:a2'), False)
        self.assertEqual(table.del_span('a1:a2'), True)
        self.assertEqual(table.del_span('a1:a2'), False)
        for coord in ('a1', 'a2'):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)


    def test_span_sp1_merge(self):
        table = self.table2.clone()
        table.set_span('a1:a2', merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[u'a 1', u'b', 1, u'd', 3, 3, 3],
                 [None, u'', u'C', u'', 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        for coord in ('a1', 'a2'):
            self.assertEqual(table.get_cell(coord)._is_spanned(), True)
        for coord in ('b1', 'b2', 'a3'):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)
        self.assertEqual(table.set_span('a1:a2'), False)
        self.assertEqual(table.del_span('a1:a2'), True)
        self.assertEqual(table.del_span('a1:a2'), False)
        for coord in ('a1', 'a2'):
            self.assertEqual(table.get_cell(coord)._is_spanned(), False)


    def test_span_sp2(self):
        table = self.table.clone()
        zone = 'a1:b3'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[True,  True,  False, False, False, False, False],
                 [True,  True,  False, False, False, False, False],
                 [True,  True,  False, False, False, False, False],
                 [False, False, False, False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp2_merge(self):
        table = self.table2.clone()
        zone = 'a1:b3'
        table.set_span(zone, merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[u'a b 1 1 1' , None, 1, u'd', 3, 3, 3],
                 [None, None, u'C', u'', 3, 3, 3],
                 [None, None, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[True,  True,  False, False, False, False, False],
                 [True,  True,  False, False, False, False, False],
                 [True,  True,  False, False, False, False, False],
                 [False, False, False, False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp3(self):
        table = self.table.clone()
        zone = 'c1:c3'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  True, False, False, False, False],
                 [False,  False,  True, False, False, False, False],
                 [False,  False,  True, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])

    # table 2
    #[[u'a', u'b', 1, u'd', 3, 3, 3],
    # [1, u'', u'C', u'', 3, 3, 3],
    # [1, 1, 1, 2, 3, 3, 3],
    # [1, 2, 3, 4, 5, 6, 7]])

    def test_span_sp3_merge(self):
        table = self.table2.clone()
        zone = 'c1:c3'
        table.set_span(zone, merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[u'a', u'b', u'1 C 1', u'd', 3, 3, 3],
                 [1, u'', None, u'', 3, 3, 3],
                 [1, 1, None, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  True, False, False, False, False],
                 [False,  False,  True, False, False, False, False],
                 [False,  False,  True, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp4(self):
        table = self.table.clone()
        zone = 'g1:g4'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, True],
                 [False,  False,  False, False, False, False, True],
                 [False,  False,  False, False, False, False, True],
                 [False,  False,  False, False, False, False, True]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp4(self):
        table = self.table2.clone()
        zone = 'g1:g4'
        table.set_span(zone, merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[u'a', u'b', 1, u'd', 3, 3, u'3 3 3 7'],
                 [1, u'', u'C', u'', 3, 3, None],
                 [1, 1, 1, 2, 3, 3, None],
                 [1, 2, 3, 4, 5, 6, None]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, True],
                 [False,  False,  False, False, False, False, True],
                 [False,  False,  False, False, False, False, True],
                 [False,  False,  False, False, False, False, True]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp5(self):
        table = self.table.clone()
        zone = 'a3:c4'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [True,   True,   True,  False, False, False, False],
                 [True,   True,   True,  False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp5_merge(self):
        table = self.table2.clone()
        zone = 'a3:c4'
        table.set_span(zone, merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[u'a', u'b', 1, u'd', 3, 3, 3],
                 [1, u'', u'C', u'', 3, 3, 3],
                 [u'1 1 1 1 2 3', None, None, 2, 3, 3, 3],
                 [None, None, None, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [True,   True,   True,  False, False, False, False],
                 [True,   True,   True,  False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp6(self):
        table = self.table.clone()
        zone = 'b3:f3'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  True,   True,  True,  True,  True,  False],
                 [False,  False,  False, False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_sp6_2zone(self):
        table = self.table.clone()
        zone = 'b3:f3'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  True,   True,  True,  True,  True,  False],
                 [False,  False,  False, False, False, False, False]])
        zone2 = 'a2:a4'
        table.set_span(zone2)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [True,  False,  False, False, False, False, False],
                 [True,  True,   True,  True,  True,  True,  False],
                 [True,  False,  False, False, False, False, False]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [True,  False,  False, False, False, False, False],
                 [True,  False,   False,  False,  False,  False,  False],
                 [True,  False,  False, False, False, False, False]])
        self.assertEqual(table.del_span(zone2), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False]])


    def test_span_bigger(self):
        table = self.table.clone()
        zone = 'e2:i4'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 2, 3, 4, 5, 6, 7, None, None]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False,  True,  True, True, True, True],
                 [False,  False,  False, False,  True,  True, True, True, True],
                 [False,  False,  False, False,  True,  True, True, True, True]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False, False, False],
                 [False,  False,  False, False, False, False, False, False, False],
                 [False,  False,  False, False, False, False, False, False, False]])


    def test_span_bigger_merge(self):
        table = self.table.clone()
        zone = 'f4:f5'
        table.set_span(zone, merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7],
                 [None, None, None, None, None, None, None]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, True, False],
                 [False,  False,  False, False, False, True]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False]])


    def test_span_bigger_outside(self):
        table = self.table.clone()
        zone = 'g6:i7'
        table.set_span(zone)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 2, 3, 4, 5, 6, 7, None, None],
                 [None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False,   False,  False,  False],
                 [False,  False,  False, False,   False,  False,  False],
                 [False,  False,  False, False,   False,  False,  False],
                 [False,  False,  False, False,   False,  False,  False],
                 [],
                 [False,  False,  False, False,   False,  False,  True, True, True],
                 [False,  False,  False, False,   False,  False,  True, True, True]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [],
                 [False,  False,  False, False, False, False, False, False, False],
                 [False,  False,  False, False, False, False, False, False, False]])


    def test_span_bigger_outside_merge(self):
        table = self.table.clone()
        zone = 'g6:i7'
        table.set_span(zone, merge = True)
        # span change only display
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 1, 1, 2, 3, 3, 3, None, None],
                 [1, 2, 3, 4, 5, 6, 7, None, None],
                 [None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None, None, None]])
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False,   False,  False,  False],
                 [False,  False,  False, False,   False,  False,  False],
                 [False,  False,  False, False,   False,  False,  False],
                 [False,  False,  False, False,   False,  False,  False],
                 [],
                 [False,  False,  False, False,   False,  False,  True, True, True],
                 [False,  False,  False, False,   False,  False,  True, True, True]])
        self.assertEqual(table.del_span(zone), True)
        res = []
        for r in table.get_cells():
            test_row = []
            for cell in r:
                test_row.append(cell._is_spanned())
            res.append(test_row)
        self.assertEqual(res,
                [[False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [False,  False,  False, False, False, False, False],
                 [],
                 [False,  False,  False, False, False, False, False, False, False],
                 [False,  False,  False, False, False, False, False, False, False]])



class TestTableGetValues(TestCase):

#    simpletable :
#      1	1	1	2	3	3	3
#      1	1	1	2	3	3	3       self.row
#      1	1	1	2	3	3	3
#      1    2	3	4	5	6	7

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table(name=u"Example1").clone()
        self.row_repeats = self.table.get_row(0)
        self.row = self.table.get_row(1)


    def test_on_empty_table(self):
        table = odf_create_table('Table')
        self.assertEqual(table.get_values(), [])
        self.assertEqual(table.get_values(complete=True), [])
        self.assertEqual(table.get_values(complete=True, get_type=True), [])
        self.assertEqual(table.get_values((0, 10)), [])
        self.assertEqual(table.get_values(cell_type='all'), [])
        self.assertEqual(table.get_values(cell_type='All'), [])
        self.assertEqual(table.get_values((2, 3), complete=True), [])


    def test_get_values_count(self):
        self.assertEqual(len(self.table.get_values()), 4) # 4 rows
        self.assertEqual(len(self.table.get_values(
                    cell_type = 'All', complete = False)), 4) # same
        self.assertEqual(len(self.table.get_values(
                    cell_type = 'All', complete = True)), 4) # 4 lines result
        self.assertEqual(len(self.table.get_values(
                    cell_type = 'All', flat = True)), 28) # flat
        self.assertEqual(len(self.table.get_values(
                                     flat = True)), 28) # flat


    def test_get_values_coord_1(self):
        table = self.table
        result = [  [1, 1, 1, 2, 3, 3, 3],
                    [1, 1, 1, 2, 3, 3, 3],
                    [1, 1, 1, 2, 3, 3, 3],
                    [1, 2, 3, 4, 5, 6, 7]]
        self.assertEqual(table.get_values(), result)
        self.assertEqual(table.get_values( (0, 0, 6, 3) ), result)
        self.assertEqual(table.get_values( (0, 3) ), result)
        self.assertEqual(table.get_values( (0, None, 6, None) ), result)
        self.assertEqual(table.get_values( (None, None, 6, 20) ), result)
        self.assertEqual(table.get_values( (0, 0, None, None) ), result)
        self.assertEqual(table.get_values( (None, 0, 10, None) ), result)
        self.assertEqual(table.get_values(""), result)
        self.assertEqual(table.get_values(":"), result)
        self.assertEqual(table.get_values("A1:G4"), result)
        self.assertEqual(table.get_values("A1:"), result)
        self.assertEqual(table.get_values("1:4"), result)
        self.assertEqual(table.get_values("1:4"), result)
        self.assertEqual(table.get_values("1:"), result)
        self.assertEqual(table.get_values("1:10"), result)
        self.assertEqual(table.get_values(":10"), result)
        self.assertEqual(table.get_values("A:"), result)
        self.assertEqual(table.get_values(":G"), result)
        self.assertEqual(table.get_values("1:H"), result)


    def test_get_values_coord_2(self):
        table = self.table
        result = [  [1, 1, 1, 2, 3, 3, 3],
                    [1, 2, 3, 4, 5, 6, 7]]
        self.assertEqual(table.get_values( (0, 2, 7, 3) ), result)
        self.assertEqual(table.get_values( (2, 3) ), result)
        self.assertEqual(table.get_values( (0, 2, 6, None) ), result)
        self.assertEqual(table.get_values( (None, 2, None, 20) ), result)
        self.assertEqual(table.get_values( (None, 2, None, None) ), result)
        self.assertEqual(table.get_values( (None, 2, 10, None) ), result)
        self.assertEqual(table.get_values("A3:G4"), result)
        self.assertEqual(table.get_values("A3:"), result)
        self.assertEqual(table.get_values("3:4"), result)
        self.assertEqual(table.get_values("3:"), result)
        self.assertEqual(table.get_values("3:10"), result)
        self.assertEqual(table.get_values("A3:"), result)
        self.assertEqual(table.get_values("3:G"), result)
        self.assertEqual(table.get_values("3:H"), result)


    def test_get_values_coord_3(self):
        table = self.table
        result = [  [1, 1 ],
                    [1, 1 ]]
        self.assertEqual(table.get_values( (0, 0, 1, 1) ), result)
        self.assertEqual(table.get_values( (None, 0, 1, 1) ), result)
        self.assertEqual(table.get_values( (None, None, 1, 1) ), result)
        self.assertEqual(table.get_values("A1:B2"), result)
        self.assertEqual(table.get_values(":B2"), result)


    def test_get_values_coord_4(self):
        table = self.table
        result = [  [3, 3 ],
                    [6, 7 ]]
        self.assertEqual(table.get_values('F3:G4'), result)
        self.assertEqual(table.get_values("F3:"), result)
        self.assertEqual(table.get_values("F3:RR555"), result)


    def test_get_values_coord_5(self):
        table = self.table
        result = [  [2, 3],
                    [2, 3],
                    [2, 3],
                    [4, 5]]
        self.assertEqual(table.get_values('D1:E4'), result)
        self.assertEqual(table.get_values("D:E"), result)
        self.assertEqual(table.get_values("D1:E555"), result)


    def test_get_values_coord_5_flat(self):
        table = self.table
        result = [  2, 3,
                    2, 3,
                    2, 3,
                    4, 5]
        self.assertEqual(table.get_values('D1:E4', flat = True), result)


    def test_get_values_coord_6(self):
        table = self.table
        result = [[5]]
        self.assertEqual(table.get_values('E4'), result)
        self.assertEqual(table.get_values("E4:E4"), result)


    def test_get_values_coord_6_flat(self):
        table = self.table
        result = [5]
        self.assertEqual(table.get_values('E4', flat=True), result)


    def test_get_values_coord_7(self):
        table = self.table
        result = []
        self.assertEqual(table.get_values('E5'), result)
        self.assertEqual(table.get_values("B3:A1"), result)


    def test_get_values_cell_type(self):
        table = self.table
        result = [  [1, 1, 1, 2, 3, 3, 3],
                    [1, 1, 1, 2, 3, 3, 3],
                    [1, 1, 1, 2, 3, 3, 3],
                    [1, 2, 3, 4, 5, 6, 7]]
        values = table.get_values(cell_type='all')
        self.assertEqual(values, result)
        values = table.get_values(cell_type='float')
        self.assertEqual(values, result)


    def test_get_values_cell_type_no_comp(self):
        table = self.table
        result = [  1, 1, 1, 2, 3, 3, 3,
                    1, 1, 1, 2, 3, 3, 3,
                    1, 1, 1, 2, 3, 3, 3,
                    1, 2, 3, 4, 5, 6, 7]
        values = table.get_values(cell_type='all', complete=True,
                                  flat=True)
        self.assertEqual(values, result)
        values = table.get_values(cell_type='float', complete=False,
                                  flat=True)
        self.assertEqual(values, result)


    def test_get_values_cell_type_1(self):
        table = self.table
        result = [  [None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None]]
        values = table.get_values(cell_type='percentage')
        self.assertEqual(values, result)


    def test_get_values_cell_type_1_flat(self):
        table = self.table
        result = [  None, None, None, None, None, None, None,
                    None, None, None, None, None, None, None,
                    None, None, None, None, None, None, None,
                    None, None, None, None, None, None, None]
        values = table.get_values(cell_type='percentage', flat = True)
        self.assertEqual(values, result)


    def test_get_values_cell_type_1_no_comp_flat(self):
        table = self.table
        result = [ ]
        values = table.get_values(cell_type='percentage', complete = False,
                                  flat=True)
        self.assertEqual(values, result)


    def test_get_values_cell_type_1_no_comp(self):
        table = self.table
        result = [[], [], [], []]
        values = table.get_values(cell_type='percentage', complete = False)
        self.assertEqual(values, result)


    def test_get_values_cell_type2_with_hole(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        table = self.table.clone()
        table.append_row(row)
        result = [[1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
                  [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
                  [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None],
                  [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3, u'bob', 14, u'bob2', None, None, u'far']]
        self.assertEqual(table.get_values(), result )
        self.assertEqual(table.get_values('A4:z4'), [result[3]] )
        self.assertEqual(table.get_values('5:5'), [result[4]] )


    def test_get_values_cell_type2_with_hole_no_comp(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        table = self.table.clone()
        table.append_row(row)
        result = [[1, 1, 1, 2, 3, 3, 3],
                  [1, 1, 1, 2, 3, 3, 3],
                  [1, 1, 1, 2, 3, 3, 3],
                  [1, 2, 3, 4, 5, 6, 7],
                [1, 1, 1, 2, 3, 3, 3, u'bob', 14, u'bob2', None, None, u'far']]
        self.assertEqual(table.get_values(complete=False), result )
        self.assertEqual(table.get_values('A4:z4',
                                          complete=False), [result[3]] )
        self.assertEqual(table.get_values('5:5',
                                          complete=False), [result[4]] )


    def test_get_values_cell_type2_with_hole_no_comp_flat(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        table = self.table.clone()
        table.append_row(row)
        result = [1, 1, 1, 2, 3, 3, 3,
                  1, 1, 1, 2, 3, 3, 3,
                  1, 1, 1, 2, 3, 3, 3,
                  1, 2, 3, 4, 5, 6, 7,
                1, 1, 1, 2, 3, 3, 3, u'bob', 14, u'bob2', None, None, u'far']
        result2 = [1, 2, 3, 4, 5, 6, 7]
        result3 = [ 1, 1, 1, 2, 3, 3, 3, u'bob', 14, u'bob2', None, None,
                   u'far']
        self.assertEqual(table.get_values(complete=False, flat=True,),result)
        self.assertEqual(table.get_values('A4:z4', flat=True,
                                          complete=False), result2 )
        self.assertEqual(table.get_values('5:5',flat=True,
                                          complete=False), result3 )


    def test_get_values_cell_type2_with_hole_get_type(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(value="bob"), clone=False)
        row.append_cell(odf_create_cell(value=14, cell_type = 'percentage'))
        row.append_cell(odf_create_cell(value="bob2"), clone=False)
        row.set_cell(12, odf_create_cell(value="far"), clone=False)
        table = self.table.clone()
        table.append_row(row)
        result1 = [[1, 1, 1, 2, 3, 3, 3, None, None, None, None, None, None]]
        result2 = [[None, None, None, None, None, None, None, u'bob', None,
                    u'bob2', None, None, u'far']]

        self.assertEqual(table.get_values('5:5', cell_type='string'),
                         result2 )

        self.assertEqual(table.get_values('5:5', cell_type='string',
                                          complete=False, flat=True),
                          [u'bob',
                           u'bob2',
                           u'far'] )

        self.assertEqual(table.get_values('5:5', cell_type='string',
                                complete=False, flat=True, get_type=True),
                          [(u'bob', 'string'),
                            (u'bob2', 'string'),
                            (u'far', 'string')] )

        self.assertEqual(table.get_values(
            coord='4:5', cell_type='All', get_type=True),
        [[ (1, u'float'), (2, u'float'), (3, u'float'), (4, u'float'),
            (5, u'float'),  (6, u'float'), (7, u'float'),(None, None),
            (None, None), (None, None), (None, None), (None, None),
            (None, None)],
            [(1, u'float'), (1, u'float'), (1, u'float'), (2, u'float'),
            (3, u'float'), (3, u'float'), (3, u'float'), (u'bob', u'string'),
            (14, u'percentage'), (u'bob2', u'string'), (None, None), (None, None),
            (u'far', u'string')]] )

        self.assertEqual(table.get_values(
            coord='4:5', cell_type='All', get_type=True, complete=False),
        [[ (1, u'float'), (2, u'float'), (3, u'float'), (4, u'float'),
            (5, u'float'),  (6, u'float'), (7, u'float') ],
            [(1, u'float'), (1, u'float'), (1, u'float'), (2, u'float'),
            (3, u'float'), (3, u'float'), (3, u'float'), (u'bob', u'string'),
            (14, u'percentage'), (u'bob2', u'string'),
            (u'far', u'string')]] )

        self.assertEqual(table.get_values(
            coord='4:5', cell_type='string', get_type=True),
        [[ (None, None), (None, None), (None, None),(None, None),
            (None, None),  (None, None), (None, None),(None, None),
            (None, None), (None, None), (None, None), (None, None),
            (None, None)],
            [(None, None), (None, None), (None, None), (None, None),
            (None, None), (None, None), (None, None),(u'bob', u'string'),
             (None, None), (u'bob2', u'string'), (None, None), (None, None),
            (u'far', u'string')]] )

        self.assertEqual(table.get_values(
            coord='4:5', cell_type='string', get_type=True,
            complete=False),
       [ [ ], [(u'bob', u'string'), (u'bob2', u'string'), (u'far', u'string')]] )

        self.assertEqual(table.get_values(
            coord='4:J5', cell_type='string', get_type=True,
            complete=False),
       [ [ ], [(u'bob', u'string'), (u'bob2', u'string'), ]] )



class TestTableCache(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        self.body = body = document.get_body()
        self.table = body.get_table(name=u"Example1")


    def test_empty_row_repeat(self):
        row = odf_create_row(repeated=5)
        table = self.table.clone()
        table.insert_row(2, row)
        value = table.get_value((3,3))
        self.assertEqual(value, None)
        cell = table.get_cell((4,5))
        self.assertEqual(cell.x, 4)
        self.assertEqual(cell.y, 5)
        values = table.get_row_values(1)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        values = table.get_row_values(2)
        self.assertEqual(values, [None, None, None, None, None, None, None])
        values = table.get_row_values(6)
        self.assertEqual(values, [None, None, None, None, None, None, None])
        values = table.get_row_values(7)
        self.assertEqual(values, [1, 1, 1, 2, 3, 3, 3])
        self.assertEqual(table.get_height(), 9)


    def test_row_repeat_twice(self):
        row = odf_create_row(repeated=6)
        table = self.table.clone()
        table.insert_row(2, row)
        cell = odf_create_cell(value=333, repeated=2)
        self.assertEqual(cell.x, None)
        self.assertEqual(cell.y, None)
        row = odf_create_row()
        row.insert_cell(4, cell)
        self.assertEqual(row.get_values(), [None, None, None, None, 333, 333])
        self.assertEqual(row.get_width(), 6)
        row.set_repeated(3)
        table.set_row(4, row)
        self.assertEqual(table.get_height(), 4      # initial height
                                            + 6     # *insert* row with repeated 5
                                            + 3 -3) # *set* row with repeated 3
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [None, None, None, None, None, None, None],
                 [None, None, None, None, None, None, None],
                 [None, None, None, None, 333, 333, None],
                 [None, None, None, None, 333, 333, None],
                 [None, None, None, None, 333, 333, None],
                 [None, None, None, None, None, None, None],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        row = table.get_row(6)
        self.assertEqual(row.get_values(), [None, None, None, None, 333, 333])
        self.assertEqual(row.get_width(), 6)
        cell = row.get_cell(5)
        self.assertEqual(cell.x, 5)
        self.assertEqual(cell.y, 6)
        self.assertEqual(cell.get_value(), 333)


    def test_cell_repeat(self):
        cell = odf_create_cell(value=55, repeated=5)
        table = self.table.clone()
        table.insert_cell((2,2), cell)
        self.assertEqual(table.get_values(),
               [[1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 1, 1, 2, 3, 3, 3, None, None, None, None, None],
                [1, 1, 55, 55, 55, 55, 55, 1, 2, 3, 3, 3],
                [1, 2, 3, 4, 5, 6, 7, None, None, None, None, None]])
        self.assertEqual(table.get_width(), 12)


    def test_clear_cache(self):
        table = self.table.clone()
        table.clear()
        self.assertEqual(table.get_width(), 0)
        self.assertEqual(table.get_height(), 0)


    def test_lonely_cell_add_cache(self):
        table = self.table.clone()
        table.clear()
        table.set_value((6,7), 1)
        self.assertEqual(table.get_width(), 7)
        self.assertEqual(table.get_height(), 8)
        cell = table.get_cell((6,7))
        self.assertEqual(cell.x, 6)
        self.assertEqual(cell.y, 7)
        self.assertEqual(cell.get_value(), 1)

    def test_basic_spreadsheet_case(self):
        table = odf_create_table(u"Table", width = 20, height = 3)
        for r in range(2):
            table.append_row()
        self.assertEqual(len(table.get_rows()), 5)
        vals = []
        for row in table.get_rows():
            vals.append(len(row.get_cells()))
        self.assertEqual(vals, [20, 20, 20, 0, 0])
        last_row = table.get_row(-1)
        for r in range(3):
            for c in range(10):
                table.set_value((c, r), u"cell %s %s"%(c, r))
        for r in range(3, 5):
            for c in range(10):
                table.set_value((c, r), c * 100 + r)
        self.assertEqual(table.get_size(), (20, 5) )
        table.rstrip()
        self.assertEqual(table.get_size(), (10, 5) )
        self.assertEqual(len(table.get_row(-1).get_cells()), 10)



class TestTableRow(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        self.table = document.get_body().get_table(name=u"Example1")


    def test_traverse_rows(self):
        self.assertEqual(len(list(self.table.traverse())), 4)


    def test_get_row_values(self):
        self.assertEqual(self.table.get_row_values(3), [1, 2, 3, 4, 5, 6, 7])


    def test_get_row_list(self):
        self.assertEqual(len(list(self.table.get_rows())), 4)
        self.assertEqual(len(list(self.table.get_rows("2:3"))), 2)


    def test_get_row_list_regex(self):
        coordinates = [row.y for row in self.table.get_rows(content=ur'4')]
        self.assertEqual(coordinates, [3])


    def test_get_row_list_style(self):
        table = self.table.clone()
        # Set a different style manually
        row = table.get_elements('table:table-row')[2]
        row.set_style(u"A Style")
        coordinates = [row.y for row in table.get_rows(style=ur'A Style')]
        self.assertEqual(coordinates, [2])


    def test_get_row(self):
        row = self.table.get_row(3)
        self.assertEqual(row.get_values(), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(row.y, 3)


    def test_get_row_repeat(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_elements('table:table-row')[1].set_repeated(2)
        row = table.get_row(4)
        self.assertEqual(row.get_values(), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(row.y, 4)


    def test_set_row(self):
        table = self.table.clone()
        row = table.get_row(3)
        row.set_value(3, u"Changed")
        row_back = table.set_row(1, row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1,          2, 3, 3, 3],
                 [1, 2, 3, u"Changed", 5, 6, 7],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 2, 3,          4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)
        self.assertEqual(row_back.y, 1)


    def test_set_row_repeat(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_elements('table:table-row')[2].set_repeated(3)
        row = table.get_row(5)
        row.set_value(3, u"Changed")
        table.set_row(2, row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1,          2, 3, 3, 3],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 2, 3, u"Changed", 5, 6, 7],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 2, 3,          4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)


    def test_set_row_smaller(self):
        table = self.table.clone()
        table.set_row(0, odf_create_row(width=table.get_width() - 1))
        self.assertEqual(table.get_height(), 4)


    def test_set_row_bigger(self):
        table = self.table.clone()
        table.set_row(0, odf_create_row(width=table.get_width() + 1))
        self.assertEqual(table.get_height(), 4)


    def test_insert(self):
        table = self.table.clone()
        row = table.insert_row(2)
        self.assert_(type(row) is odf_row)
        self.assertEqual(row.y, 2)


    def test_insert_row(self):
        table = self.table.clone()
        row = table.get_row(3)
        row_back = table.insert_row(2, row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)
        self.assertEqual(row_back.y, 2)


    def test_insert_row_repeated(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_elements('table:table-row')[2].set_repeated(3)
        row = table.get_row(5)
        table.insert_row(2, row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)


    def test_insert_row_smaller(self):
        table = self.table.clone()
        small_row = odf_create_row(width=table.get_width() - 1)
        table.insert_row(0, small_row)
        self.assertEqual(table.get_height(), 5)


    def test_insert_row_bigger(self):
        table = self.table.clone()
        big_row = odf_create_row(width=table.get_width() + 1)
        table.insert_row(0, big_row)
        self.assertEqual(table.get_height(), 5)


    def test_append(self):
        table = self.table.clone()
        row = table.append_row()
        self.assert_(type(row) is odf_row)


    def test_append_row(self):
        table = self.table.clone()
        row = table.get_row(0)
        row_back = table.append_row(row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7],
                 [1, 1, 1, 2, 3, 3, 3]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)
        self.assertEqual(row_back.y, table.get_height() - 1)


    def test_append_row_smaller(self):
        table = self.table.clone()
        table.append_row(odf_create_row(width=table.get_width() - 1))
        self.assertEqual(table.get_height(), 5)


    def test_append_row_bigger(self):
        table = self.table.clone()
        table.append_row(odf_create_row(width=table.get_width() + 1))
        self.assertEqual(table.get_height(), 5)


    def test_delete_row(self):
        table = self.table.clone()
        table.delete_row(2)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)


    def test_delete_row_repeat(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_elements('table:table-row')[2].set_repeated(3)
        table.delete_row(2)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        # Test columns are synchronized
        self.assertEqual(table.get_width(), 7)


    def test_is_row_empty(self):
        table = odf_create_table(u"Empty", width=10, height=20)
        for y in xrange(20):
            self.assertEqual(table.is_row_empty(y), True)


    def test_is_row_empty_no(self):
        table = odf_create_table(u"Not Empty", width=10, height=20)
        table.set_value((4, 9), u"Bouh !")
        self.assertEqual(table.is_row_empty(9), False)



class TestTableCell(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table(name=u"Example1").clone()


    def test_get_cell_alpha(self):
        table = self.table
        cell = table.get_cell('D3')
        self.assertEqual(cell.get_value(), 2)
        self.assertEqual(cell.get_text_content(), u"2")
        self.assertEqual(cell.get_type(), 'float')
        self.assertEqual(cell.get_style(), u"ce1")
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 2)


    def test_get_cell_tuple(self):
        table = self.table
        cell = table.get_cell((3, 2))
        self.assertEqual(cell.get_value(), 2)
        self.assertEqual(cell.get_text_content(), u"2")
        self.assertEqual(cell.get_type(), 'float')
        self.assertEqual(cell.get_style(), u"ce1")
        self.assertEqual(cell.x, 3)
        self.assertEqual(cell.y, 2)


    def test_set_cell_value(self):
        table = self.table.clone()
        table.set_value('D3', u"Changed")
        self.assertEqual(table.get_values(),
                [[1, 1, 1,          2, 3, 3, 3],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 1, 1, u"Changed", 3, 3, 3],
                 [1, 2, 3,          4, 5, 6, 7]])


    def test_get_cell_list(self):
        self.assertEqual(len(list(self.table.get_cells(flat=True))), 28)


    def test_get_cell_list_regex(self):
        table = self.table
        coordinates = [(cell.x, cell.y)
            for cell in table.get_cells(content=ur'3', flat=True)]
        expected = [(4, 0), (5, 0), (6, 0), (4, 1), (5, 1), (6, 1), (4, 2),
                (5, 2), (6, 2), (2, 3)]
        self.assertEqual(coordinates, expected)


    def test_get_cell_list_style(self):
        table = self.table
        coordinates = [(cell.x, cell.y)
            for cell in table.get_cells(style=ur"ce1", flat=True)]
        expected = [(1, 1), (5, 1), (3, 2)]
        self.assertEqual(coordinates, expected)


    def test_insert(self):
        table = self.table.clone()
        cell = table.insert_cell('B3')
        self.assert_(type(cell) is odf_cell)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 2)


    def test_insert_cell(self):
        table = self.table.clone()
        cell = table.insert_cell('B3', odf_create_cell(u"Inserted"))
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None],
                 [1, 1, 1, 2, 3, 3, 3, None],
                 [1, u"Inserted", 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7, None]])
        # Test columns are synchronized
        self.assertEqual(table.get_width(), 8)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 2)


    def test_append(self):
        table = self.table.clone()
        cell = table.append_cell(1)
        self.assert_(type(cell) is odf_cell)
        self.assertEqual(cell.x, table.get_width() -1)


    def test_append_cell(self):
        table = self.table.clone()
        cell = table.append_cell(1, odf_create_cell(u"Appended"))
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None],
                 [1, 1, 1, 2, 3, 3, 3, u"Appended"],
                 [1, 1, 1, 2, 3, 3, 3, None],
                 [1, 2, 3, 4, 5, 6, 7, None]])
        # Test columns are synchronized
        self.assertEqual(table.get_width(), 8)
        self.assertEqual(cell.x, table.get_width() -1)


    def test_delete_cell(self):
        table = self.table.clone()
        table.delete_cell('F3')
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3,    3],
                 [1, 1, 1, 2, 3, 3,    3],
                 [1, 1, 1, 2, 3, 3, None],
                 [1, 2, 3, 4, 5, 6,    7]])
        # Test columns are synchronized
        self.assertEqual(table.get_width(), 7)



class TestTableNamedRange(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        document2 = odf_get_document('samples/simple_table_named_range.ods')
        self.body = document.get_body()
        # no clones !
        self.table = self.body.get_table(name=u"Example1")
        self.body2 = document2.get_body()
        self.table2 = self.body2.get_table(name=u"Example1")


    def test_create_bad_nr(self):
        self.assertRaises(TypeError, odf_create_named_range)


    def test_create_bad_nr_2(self):
        self.assertRaises(ValueError, odf_create_named_range, ' ', 'A1',
                                                            'tname')


    def test_create_bad_nr_3(self):
        self.assertRaises(ValueError, odf_create_named_range, 'A1', 'A1',
                                                            'tname')


    def test_create_bad_nr_4(self):
        self.assertRaises(ValueError, odf_create_named_range, 'a space', 'A1',
                                                            'tname')


    def test_create_bad_nr_5(self):
        self.assertRaises(ValueError, odf_create_named_range, '===', 'A1',
                                                            'tname')


    def test_create_bad_nr_6(self):
        self.assertRaises(ValueError, odf_create_named_range, 'ok', 'A1',
                                                            '/ ')


    def test_create_bad_nr_7(self):
        self.assertRaises(ValueError, odf_create_named_range, 'ok', 'A1',
                                                            ' ')


    def test_create_bad_nr_8(self):
        self.assertRaises(ValueError, odf_create_named_range, 'ok', 'A1',
                                                            '\\')


    def test_create_bad_nr_9(self):
        self.assertRaises(ValueError, odf_create_named_range, 'ok', 'A1',
                                                            'tname\nsecond line')


    def test_create_bad_nr_10(self):
        self.assertRaises(ValueError, odf_create_named_range, 'ok', 'A1',
                                                            42)


    def test_create_nr(self):
        nr = odf_create_named_range(u'nr_name_ù', 'A1:C2', u'table name é',
                                    usage = 'filter')
        result="""<table:named-range table:name="nr_name_&#249;" table:base-cell-address="$'table name &#233;'.$A$1" table:cell-range-address="$'table name &#233;'.$A$1:.$C$2" table:range-usable-as="filter"/>"""
        self.assertEqual(nr.serialize(), result)


    def test_usage_1(self):
        nr = odf_create_named_range(u'a123a', 'A1:C2', u'tablename')
        self.assertEqual(nr.usage, None)
        nr.set_usage('blob')
        self.assertEqual(nr.usage, None)


    def test_usage_2(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_usage('filter')
        self.assertEqual(nr.usage, 'filter')
        nr.set_usage('blob')
        self.assertEqual(nr.usage, None)


    def test_usage_3(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_usage('Print-Range')
        self.assertEqual(nr.usage, 'print-range')
        nr.set_usage(None)
        self.assertEqual(nr.usage, None)


    def test_usage_4(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_usage(u'repeat-column')
        self.assertEqual(nr.usage, 'repeat-column')


    def test_usage_5(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_usage('repeat-row')
        self.assertEqual(nr.usage, 'repeat-row')


    def test_name_1(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertEqual(nr.name, 'nr_name')


    def test_name_2(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_name(u'  New_Name_ô ')
        self.assertEqual(nr.name, u'New_Name_ô')


    def test_name_3(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.set_name, '   ')


    def test_table_name_1(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertEqual(nr.table_name, 'tablename')


    def test_table_name_2(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_table_name('  new name ')
        self.assertEqual(nr.table_name, 'new name')


    def test_table_name_3(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.set_table_name, '   ')


    def test_range_1(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.set_range, '   ')


    def test_range_2(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertEqual(nr.crange, (0, 0, 2, 1))
        self.assertEqual(nr.start, (0, 0))
        self.assertEqual(nr.end, (2, 1))


    def test_range_3(self):
        nr = odf_create_named_range(u'nr_name', 'A1', u'tablename')
        self.assertEqual(nr.crange, (0, 0, 0, 0))
        self.assertEqual(nr.start, (0, 0))
        self.assertEqual(nr.end, (0, 0))


    def test_range_4(self):
        nr = odf_create_named_range(u'nr_name', (1, 2, 3, 4), u'tablename')
        self.assertEqual(nr.crange, (1, 2, 3, 4))
        self.assertEqual(nr.start, (1, 2))
        self.assertEqual(nr.end, (3, 4))


    def test_range_5(self):
        nr = odf_create_named_range(u'nr_name', (5, 6), u'tablename')
        self.assertEqual(nr.crange, (5, 6, 5, 6))
        self.assertEqual(nr.start, (5, 6))
        self.assertEqual(nr.end, (5, 6))


    def test_range_6(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_range('B3')
        self.assertEqual(nr.crange, (1, 2, 1, 2))
        self.assertEqual(nr.start, (1, 2))
        self.assertEqual(nr.end, (1, 2))


    def test_range_7(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_range('B3:b10')
        self.assertEqual(nr.crange, (1, 2, 1, 9))
        self.assertEqual(nr.start, (1, 2))
        self.assertEqual(nr.end, (1, 9))


    def test_range_8(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_range((1,5,0,9))
        self.assertEqual(nr.crange, (1, 5, 0, 9))
        self.assertEqual(nr.start, (1, 5))
        self.assertEqual(nr.end, (0, 9))


    def test_range_9(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        nr.set_range((0,9))
        self.assertEqual(nr.crange, (0, 9, 0, 9))
        self.assertEqual(nr.start, (0, 9))
        self.assertEqual(nr.end, (0, 9))


    def test_value_bad_1(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.get_values)


    def test_value_bad_2(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.get_value)


    def test_value_bad_3(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.set_values, [[1, 2]])


    def test_value_bad_4(self):
        nr = odf_create_named_range(u'nr_name', 'A1:C2', u'tablename')
        self.assertRaises(ValueError, nr.set_value, 42)


    def test_body_table_get_1(self):
        self.assertEqual(self.table.get_named_ranges(), [])


    def test_body_table_get_2(self):
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_1', 'nr_6'])


    def test_body_table_get_3(self):
        table2 = self.table2.clone()
        self.assertEqual(table2.get_named_ranges(), [])


    def test_body_table_get_4(self):
        table = self.table2
        back_nr = table.get_named_range('nr_1')
        self.assertEqual(back_nr.name, 'nr_1')


    def test_body_table_get_4_1(self):
        table = self.table2
        back_nr = table.get_named_range('nr_1xxx')
        self.assertEqual(back_nr, None)


    def test_body_table_get_4_2(self):
        table = self.table2
        back_nr = table.get_named_range('nr_6')
        self.assertEqual(back_nr.name, 'nr_6')
        self.assertEqual(back_nr.table_name, 'Example1')
        self.assertEqual(back_nr.start, (3, 2))
        self.assertEqual(back_nr.end, (5, 3))
        self.assertEqual(back_nr.crange, (3, 2, 5, 3))
        self.assertEqual(back_nr.usage, 'print-range')


    def test_body_table_get_5(self):
        table = self.table
        back_nr = table.get_named_range('nr_1')
        self.assertEqual(back_nr, None)


    def test_body_table_set_0(self):
        self.assertRaises(ValueError, self.table2.set_named_range, '   ', 'A1:C2')


    def test_body_table_set_1(self):
        self.table2.set_named_range("new", "A1:B1")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_1', 'nr_6', 'new'])


    def test_body_table_set_3(self):
        self.table2.set_named_range("new", "A1:B1")
        back_nr = self.table2.get_named_range('new')
        self.assertEqual(back_nr.usage, None)
        self.assertEqual(back_nr.crange, (0, 0, 1, 0))
        self.assertEqual(back_nr.start, (0, 0))
        self.assertEqual(back_nr.end, (1, 0))
        self.assertEqual(back_nr.table_name, 'Example1')
        # reset
        self.table2.set_named_range("new", "A1:c2")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_1', 'nr_6', 'new'])
        back_nr = self.table2.get_named_range('new')
        self.assertEqual(back_nr.usage, None)
        self.assertEqual(back_nr.crange, (0, 0, 2, 1))
        self.assertEqual(back_nr.start, (0, 0))
        self.assertEqual(back_nr.end, (2, 1))
        self.assertEqual(back_nr.table_name, 'Example1')


    def test_body_table_delete_1(self):
        self.table2.delete_named_range("xxx")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_1', 'nr_6'])


    def test_body_table_delete_2(self):
        self.table2.delete_named_range("nr_1")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_6'])


    def test_body_table_delete_3(self):
        self.table2.set_named_range("new", "A1:c2")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_1', 'nr_6', 'new'])
        self.table2.delete_named_range("nr_1")
        self.table2.delete_named_range("nr_6")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['new'])
        self.table2.delete_named_range("new")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, [])
        self.table2.delete_named_range("new")
        self.table2.delete_named_range("xxx")
        self.table2.set_named_range("hop", "A1:C2")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['hop'])
        self.table2.set_named_range("hop", "A2:d8")
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['hop'])
        nr = self.table2.get_named_range('hop')
        self.assertEqual(nr.crange, (0, 1, 3, 7))


    def test_body_table_get_value_1(self):
        result = self.table2.get_named_range("nr_1").get_value()
        self.assertEqual(result, 1)


    def test_body_table_get_value_2(self):
        result = self.table2.get_named_range("nr_1").get_value(get_type = True)
        self.assertEqual(result, (1, 'float'))


    def test_body_table_get_value_3(self):
        result = self.table2.get_named_range("nr_1").get_values()
        self.assertEqual(result, [[1]])


    def test_body_table_get_value_4(self):
        result = self.table2.get_named_range("nr_1").get_values(flat = True)
        self.assertEqual(result, [1])


    def test_body_table_get_value_5(self):
        result = self.table2.get_named_range("nr_6").get_values(flat = True)
        self.assertEqual(result, [2, 3, 3, 4, 5, 6])


    def test_body_table_get_value_6(self):
        result = self.table2.get_named_range("nr_6").get_value()
        self.assertEqual(result, 2)


    def test_body_table_set_value_1(self):
        self.table2.get_named_range("nr_6").set_value('AAA')
        self.assertEqual(self.table2.get_value('D3'), 'AAA')
        self.assertEqual(self.table2.get_value('E3'), 3)


    def test_body_table_set_value_2(self):
        self.table2.get_named_range("nr_6").set_values([[10,11,12],[13,14,15]])
        self.assertEqual(self.table2.get_values(), [[1, 1, 1, 2, 3, 3, 3],
                                                    [1, 1, 1, 2, 3, 3, 3],
                                                    [1, 1, 1, 10, 11, 12, 3],
                                                    [1, 2, 3, 13, 14, 15, 7]])


    def test_body_change_name_table(self):
        self.table2.set_name('new table')
        result = [ nr.name for nr in self.table2.get_named_ranges()]
        self.assertEqual(result, ['nr_1', 'nr_6'])
        back_nr = self.table2.get_named_range('nr_6')
        self.assertEqual(back_nr.name, 'nr_6')
        self.assertEqual(back_nr.table_name, 'new table')
        self.assertEqual(back_nr.start, (3, 2))
        self.assertEqual(back_nr.end, (5, 3))
        self.assertEqual(back_nr.crange, (3, 2, 5, 3))
        self.assertEqual(back_nr.usage, 'print-range')



class TestTableColumn(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table(name=u"Example1").clone()


    def test_traverse_columns(self):
        self.assertEqual(len(list(self.table.traverse_columns())), 7)


    def test_get_column_list(self):
        self.assertEqual(len(list(self.table.get_columns())), 7)


    def test_get_column_list_style(self):
        table = self.table
        coordinates = [col.x for col in table.get_columns(style=ur"co2")]
        self.assertEqual(coordinates, [2, 3])


    def test_get_column(self):
        table = self.table
        column = table.get_column(3)
        self.assertEqual(column.get_style(), u"co2")
        self.assertEqual(column.x, 3)
        column = table.get_column(4)
        self.assertEqual(column.get_style(), u"co1")
        self.assertEqual(column.x, 4)


    def test_set_column(self):
        table = self.table.clone()
        column = table.get_column(3)
        column_back = table.set_column(4, column)
        self.assertEqual(column_back.x, 4)
        column = table.get_column(4)
        self.assertEqual(column.x, 4)
        self.assertEqual(column.get_style(), u"co2")


    def test_insert(self):
        table = self.table.clone()
        column = table.insert_column(3)
        self.assert_(type(column) is odf_column)
        self.assertEqual(column.x, 3)


    def test_insert_column(self):
        table = self.table.clone()
        column = table.insert_column(3, odf_create_column())
        self.assertEqual(table.get_width(), 8)
        self.assertEqual(table.get_row(0).get_width(), 8)
        self.assertEqual(column.x, 3)


    def test_append(self):
        table = self.table.clone()
        column = table.append_column()
        self.assert_(type(column) is odf_column)
        self.assertEqual(column.x, table.get_width() - 1)


    def test_append_column(self):
        table = self.table.clone()
        column = table.append_column(odf_create_column())
        self.assertEqual(table.get_columns_width(), 8)
        self.assertEqual(table.get_row(0).get_width(),  7)
        self.assertEqual(column.x, table.get_width() - 1)
        # The column must be inserted between the columns and the rows
        self.assert_(type(table.get_children()[-1]) is not odf_column)


    def test_delete_column(self):
        table = self.table.clone()
        table.delete_column(3)
        self.assertEqual(table.get_width(), 6)
        self.assertEqual(table.get_row(0).get_width(), 6)


    def test_get_column_cell_values(self):
        self.assertEqual(self.table.get_column_values(3), [2, 2, 2, 4])


    def test_set_column_cell_values(self):
        table = self.table.clone()
        table.set_column_values(5, [u"a", u"b", u"c", u"d"])
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, u"a", 3],
                 [1, 1, 1, 2, 3, u"b", 3],
                 [1, 1, 1, 2, 3, u"c", 3],
                 [1, 2, 3, 4, 5, u"d", 7]])


    def test_is_column_empty(self):
        table = odf_create_table(u"Empty", width=10, height=20)
        for x in xrange(10):
            self.assertEqual(table.is_column_empty(x), True)


    def test_is_column_empty_no(self):
        table = odf_create_table(u"Not Empty", width=10, height=20)
        table.set_value((4, 9), u"Bouh !")
        self.assertEqual(table.is_column_empty(4), False)



class TestCSV(TestCase):

    def setUp(self):
        self.table = import_from_csv(StringIO(csv_data), u"From CSV")


    def test_import_from_csv(self):
        expected = ('<table:table table:name="From CSV">'
                      '<table:table-column '
                      'table:number-columns-repeated="2"/>'
                      '<table:table-row>'
                        '<table:table-cell office:value-type="string" '
                          'office:string-value="A float">'
                          '<text:p>A float</text:p>'
                        '</table:table-cell>'
                        '<table:table-cell office:value-type="float" '
                          'office:value="3.14">'
                          '<text:p>3.14</text:p>'
                        '</table:table-cell>'
                      '</table:table-row>'
                      '<table:table-row>'
                        '<table:table-cell office:value-type="string" '
                          'office:string-value="A date">'
                          '<text:p>A date</text:p>'
                        '</table:table-cell>'
                        '<table:table-cell office:value-type="date" '
                          'office:date-value="1975-05-07T00:00:00">'
                          '<text:p>1975-05-07T00:00:00</text:p>'
                        '</table:table-cell>'
                      '</table:table-row>'
                    '</table:table>')
        self.assertEqual(self.table.serialize(), expected)


    def _test_export_to_csv(self):
        raise NotImplementedError



if __name__ == '__main__':
    main()
