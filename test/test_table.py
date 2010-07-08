# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
from datetime import date, datetime, timedelta
from decimal import Decimal as dec
from cStringIO import StringIO
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.table import _alpha_to_digit, _digit_to_alpha
from lpod.table import _get_cell_coordinates, odf_cell, odf_row
from lpod.table import odf_create_cell, odf_create_row, odf_create_column
from lpod.table import odf_create_table, import_from_csv, odf_column


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


    def test_get_cell_coordinates_tuple(self):
        x1, y1 = (12, 34)
        x2, y2 = _get_cell_coordinates((x1, y1))
        self.assertEqual((x1, y1), (x2, y2))


    def test_get_cell_coordinates_alphanum(self):
        x, y = _get_cell_coordinates('ABC123')
        self.assertEqual((x, y), (730, 122))



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
                      '<text:p>90</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_percentage_repr(self):
        cell = odf_create_cell(90, text=u"90 %", cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>90 %</text:p>'
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
        expected = ('<table:table-column table:style-name="co1" '
                      'table:default-cell-style-name="A Style"/>'
                      'table:number-columns-repeated="3"/>')



class TestCreateTable(TestCase):

    def test_default(self):
        table = odf_create_table(u"A Table")
        expected = '<table:table table:name="A Table"/>'
        self.assertEqual(table.serialize(), expected)


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


    def test_set_cell_value(self):
        cell = self.cell.clone()
        cell.set_value(u"€")
        self.assertEqual(cell.get_value(), u"€")
        self.assertEqual(cell.get_type(), 'string')


    def test_get_cell_type(self):
        cell = self.cell.clone()
        self.assertEqual(cell.get_type(), 'float')
        cell.set_value(u"€")
        self.assertEqual(cell.get_type(), 'string')


    def test_set_cell_type(self):
        cell = self.cell.clone()
        cell.set_type('time')
        self.assertEqual(cell.get_type(), 'time')


    def test_get_cell_currency(self):
        cell = odf_create_cell(123, cell_type='currency', currency='EUR')
        self.assertEqual(cell.get_currency(), 'EUR')


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
        self.assertEqual(self.cell.get_stylename(), u"ce1")


    def test_set_cell_style(self):
        cell = self.cell.clone()
        cell.set_stylename(u"ce2")
        self.assertEqual(cell.get_stylename(), u"ce2")
        cell.set_stylename(None)
        self.assertEqual(cell.get_stylename(), None)



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
        self.assertEqual(self.row.get_stylename(), u"ro1")


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

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        table = body.get_table(name=u"Example1").clone()
        self.row_repeats = table.get_row(0)
        self.row = table.get_row(1)


    def test_traverse(self):
        self.assertEqual(len(list(self.row.traverse())), 7)


    def test_get_cell_list(self):
        self.assertEqual(len(list(self.row.get_cell_list())), 7)


    def test_get_cell_list_regex(self):
        coordinates = [x for x, cell in self.row.get_cell_list(content=ur'3')]
        expected = [4, 5, 6]
        self.assertEqual(coordinates, expected)


    def test_get_cell_list_style(self):
        coordinates = [x
                for x, cell in self.row.get_cell_list(style=ur"ce1")]
        expected = [1, 5]
        self.assertEqual(coordinates, expected)


    def test_get_cell_alpha(self):
        row = self.row
        cell_5 = row.get_cell('F')
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.get_text_content(), u"3")
        self.assertEqual(cell_5.get_type(), 'float')
        self.assertEqual(cell_5.get_stylename(), u"ce1")


    def test_get_cell_int(self):
        row = self.row
        cell_5 = row.get_cell(5)
        self.assertEqual(cell_5.get_value(), 3)
        self.assertEqual(cell_5.get_text_content(), u"3")
        self.assertEqual(cell_5.get_type(), 'float')
        self.assertEqual(cell_5.get_stylename(), u"ce1")


    def test_set_cell(self):
        row = self.row.clone()
        row.set_value(1, 3.14)
        self.assertEqual(row.get_values(),
                [1, dec('3.14'), 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_set_cell_repeat(self):
        row = self.row_repeats.clone()
        row.set_value(1, 3.14)
        self.assertEqual(row.get_values(),
                [1, dec('3.14'), 1, 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 7)


    def test_insert(self):
        row = self.row.clone()
        cell = row.insert_cell(3)
        self.assert_(type(cell) is odf_cell)


    def test_insert_cell(self):
        row = self.row.clone()
        row.insert_cell(3, odf_create_cell(u"Inserted"))
        self.assertEqual(row.get_width(), 8)
        self.assertEqual(row.get_values(),
                [1, 1, 1, u"Inserted", 2, 3, 3, 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)


    def test_insert_cell_repeat(self):
        row = self.row_repeats.clone()
        row.insert_cell(6, odf_create_cell(u"Inserted"))
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, u"Inserted", 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)


    def test_insert_cell_repeat_repeat(self):
        row = self.row_repeats.clone()
        row.insert_cell(6, odf_create_cell(u"Inserted", repeated=3))
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, u"Inserted", u"Inserted", u"Inserted", 3])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 10)


    def test_append(self):
        row = self.row.clone()
        cell = row.append_cell()
        self.assert_(type(cell) is odf_cell)


    def test_append_cell(self):
        row = self.row.clone()
        row.append_cell(odf_create_cell(u"Appended"))
        self.assertEqual(row.get_values(),
                [1, 1, 1, 2, 3, 3, 3, u"Appended"])
        # Test repetitions are synchronized
        self.assertEqual(row.get_width(), 8)


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
        self.assertEqual(self.column.get_stylename(), u"co1")


    def test_set_column_style(self):
        column = self.column.clone()
        column.set_stylename(u"co2")
        self.assertEqual(column.get_stylename(), u"co2")
        column.set_stylename(None)
        self.assertEqual(column.get_stylename(), None)



class TestTable(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        self.body = body = document.get_body()
        self.table = body.get_table(name=u"Example1")


    def test_get_table_list(self):
        body = self.body
        self.assertEqual(len(body.get_table_list()), 3)


    def test_get_table_list_style(self):
        body = self.body
        self.assertEqual(len(body.get_table_list(style=u"ta1")), 3)


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
        self.assertEqual(self.table.get_stylename(), u"ta1")


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


    def  test_set_table_values(self):
        table = self.table.clone()
        values = [[u"a", u"b", u"c", u"d", u"e", u"f", u"g"],
                  [u"h", u"i", u"j", u"k", u"l", u"m", u"n"],
                  [u"o", u"p", u"q", u"r", u"s", u"t", u"u"],
                  [u"v", u"w", u"x", u"y", u"z", u"aa", u"ab"]]
        table.set_values(values)
        self.assertEqual(table.get_values(), values)


    def test_rstrip_table(self):
        document = odf_get_document('samples/styled_table.ods')
        table = document.get_body().get_table(name=u'Feuille1').clone()
        table.rstrip()
        self.assertEqual(table.get_size(), (5, 9))



class TestTableRow(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        self.table = document.get_body().get_table(name=u"Example1")


    def test_traverse_rows(self):
        self.assertEqual(len(list(self.table.traverse())), 4)


    def test_get_row_values(self):
        self.assertEqual(self.table.get_row_values(3), [1, 2, 3, 4, 5, 6, 7])


    def test_get_row_list(self):
        self.assertEqual(len(list(self.table.get_row_list())), 4)


    def test_get_row_list_regex(self):
        coordinates = [y for y, row in self.table.get_row_list(content=ur'4')]
        self.assertEqual(coordinates, [3])


    def test_get_row_list_style(self):
        table = self.table.clone()
        # Set a different style manually
        row = table.get_element_list('table:table-row')[2]
        row.set_stylename(u"A Style")
        coordinates = [y for y, row in table.get_row_list(style=ur'A Style')]
        self.assertEqual(coordinates, [2])


    def test_get_row(self):
        row = self.table.get_row(3)
        self.assertEqual(row.get_values(), [1, 2, 3, 4, 5, 6, 7])


    def test_get_row_repeat(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_element_list('table:table-row')[1].set_repeated(2)
        row = table.get_row(4)
        self.assertEqual(row.get_values(), [1, 2, 3, 4, 5, 6, 7])


    def test_set_row(self):
        table = self.table.clone()
        row = table.get_row(3)
        row.set_value(3, u"Changed")
        table.set_row(1, row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1,          2, 3, 3, 3],
                 [1, 2, 3, u"Changed", 5, 6, 7],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 2, 3,          4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)


    def test_set_row_repeat(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_element_list('table:table-row')[2].set_repeated(3)
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


    def test_insert_row(self):
        table = self.table.clone()
        row = table.get_row(3)
        table.insert_row(2, row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)


    def test_insert_row_repeated(self):
        table = self.table.clone()
        # Set a repetition manually
        table.get_element_list('table:table-row')[2].set_repeated(3)
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
        table.append_row(row)
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7],
                 [1, 1, 1, 2, 3, 3, 3]])
        # test columns are synchronized
        self.assertEqual(table.get_width(), 7)


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
        table.get_element_list('table:table-row')[2].set_repeated(3)
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
        self.assertEqual(cell.get_stylename(), u"ce1")


    def test_get_cell_tuple(self):
        table = self.table
        cell = table.get_cell((3, 2))
        self.assertEqual(cell.get_value(), 2)
        self.assertEqual(cell.get_text_content(), u"2")
        self.assertEqual(cell.get_type(), 'float')
        self.assertEqual(cell.get_stylename(), u"ce1")


    def test_set_cell_value(self):
        table = self.table.clone()
        table.set_value('D3', u"Changed")
        self.assertEqual(table.get_values(),
                [[1, 1, 1,          2, 3, 3, 3],
                 [1, 1, 1,          2, 3, 3, 3],
                 [1, 1, 1, u"Changed", 3, 3, 3],
                 [1, 2, 3,          4, 5, 6, 7]])


    def test_get_cell_list(self):
        self.assertEqual(len(list(self.table.get_cell_list())), 28)


    def test_get_cell_list_regex(self):
        table = self.table
        coordinates = [(x, y)
                for x, y, cell in table.get_cell_list(content=ur'3')]
        expected = [(4, 0), (5, 0), (6, 0), (4, 1), (5, 1), (6, 1), (4, 2),
                (5, 2), (6, 2), (2, 3)]
        self.assertEqual(coordinates, expected)


    def test_get_cell_list_style(self):
        table = self.table
        coordinates = [(x, y)
                for x, y, cell in table.get_cell_list(style=ur"ce1")]
        expected = [(1, 1), (5, 1), (3, 2)]
        self.assertEqual(coordinates, expected)


    def test_insert(self):
        table = self.table.clone()
        cell = table.insert_cell('B3')
        self.assert_(type(cell) is odf_cell)


    def test_insert_cell(self):
        table = self.table.clone()
        table.insert_cell('B3', odf_create_cell(u"Inserted"))
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None],
                 [1, 1, 1, 2, 3, 3, 3, None],
                 [1, u"Inserted", 1, 1, 2, 3, 3, 3],
                 [1, 2, 3, 4, 5, 6, 7, None]])
        # Test columns are synchronized
        self.assertEqual(table.get_width(), 8)


    def test_append(self):
        table = self.table.clone()
        cell = table.append_cell(1)
        self.assert_(type(cell) is odf_cell)


    def test_append_cell(self):
        table = self.table.clone()
        table.append_cell(1, odf_create_cell(u"Appended"))
        self.assertEqual(table.get_values(),
                [[1, 1, 1, 2, 3, 3, 3, None],
                 [1, 1, 1, 2, 3, 3, 3, u"Appended"],
                 [1, 1, 1, 2, 3, 3, 3, None],
                 [1, 2, 3, 4, 5, 6, 7, None]])
        # Test columns are synchronized
        self.assertEqual(table.get_width(), 8)


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



class TestTableColumn(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table(name=u"Example1").clone()


    def test_traverse_columns(self):
        self.assertEqual(len(list(self.table.traverse_columns())), 7)


    def test_get_column_list(self):
        self.assertEqual(len(list(self.table.get_column_list())), 7)


    def test_get_column_list_style(self):
        table = self.table
        coordinates = [x for x, col in table.get_column_list(style=ur"co2")]
        self.assertEqual(coordinates, [2, 3])


    def test_get_column(self):
        table = self.table
        column = table.get_column(3)
        self.assertEqual(column.get_stylename(), u"co2")
        column = table.get_column(4)
        self.assertEqual(column.get_stylename(), u"co1")


    def test_set_column(self):
        table = self.table.clone()
        column = table.get_column(3)
        table.set_column(4, column)
        column = table.get_column(4)
        self.assertEqual(column.get_stylename(), u"co2")


    def test_insert(self):
        table = self.table.clone()
        column = table.insert_column(3)
        self.assert_(type(column) is odf_column)


    def test_insert_column(self):
        table = self.table.clone()
        table.insert_column(3, odf_create_column())
        self.assertEqual(table.get_width(), 8)
        self.assertEqual(table.get_row(0).get_width(), 8)


    def test_append(self):
        table = self.table.clone()
        column = table.append_column()
        self.assert_(type(column) is odf_column)


    def test_append_column(self):
        table = self.table.clone()
        table.append_column(odf_create_column())
        self.assertEqual(table.get_width(), 8)
        self.assertEqual(table.get_row(0).get_width(),  7)
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
