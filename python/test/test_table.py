# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import date, datetime, timedelta
from decimal import Decimal
from cStringIO import StringIO
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.table import _get_cell_coordinates, alpha_to_base10
from lpod.table import odf_create_cell, odf_create_row, odf_create_column
from lpod.table import odf_create_table, import_from_csv


csv_data = '"A float","3.14"\n"A date","1975-05-07"\n'



class TestCoordinates(TestCase):

    def test_alpha_to_base10(self):
        self.assertEqual(alpha_to_base10('ABC'), 731)


    def test_get_cell_coordinates_tuple(self):
        x1, y1 = (12, 34)
        x2, y2 = _get_cell_coordinates((x1, y1))
        self.assertEqual((x1, y1), (x2, y2))


    def test_get_cell_coordinates_alphanum(self):
        x, y = _get_cell_coordinates('ABC123')
        self.assertEqual((x, y), (730, 122))



class TestCreateCell(TestCase):

    def test_create_cell_bool(self):
        cell = odf_create_cell(True)
        expected = ('<table:table-cell office:value-type="boolean" '
                      'office:boolean-value="true">'
                      '<text:p>true</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_bool_repr(self):
        cell = odf_create_cell(True, representation=u"VRAI")
        expected = ('<table:table-cell office:value-type="boolean" '
                      'office:boolean-value="true">'
                      '<text:p>VRAI</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_int(self):
        cell = odf_create_cell(23)
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="23">'
                      '<text:p>23</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_int_repr(self):
        cell = odf_create_cell(23, representation=u"00023")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="23">'
                      '<text:p>00023</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_float(self):
        cell = odf_create_cell(3.141592654)
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="3.141592654">'
                      '<text:p>3.141592654</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_float_repr(self):
        cell = odf_create_cell(3.141592654, representation=u"3,14")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="3.141592654">'
                      '<text:p>3,14</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_decimal(self):
        cell = odf_create_cell(Decimal('2.718281828'))
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="2.718281828">'
                      '<text:p>2.718281828</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_decimal_repr(self):
        cell = odf_create_cell(Decimal('2.718281828'),
                               representation=u"2,72")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="2.718281828">'
                      '<text:p>2,72</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_date(self):
        cell = odf_create_cell(date(2009, 6, 30))
        expected = ('<table:table-cell office:value-type="date" '
                      'office:date-value="2009-06-30">'
                      '<text:p>2009-06-30</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_date_repr(self):
        cell = odf_create_cell(date(2009, 6, 30),
                               representation=u"30/6/2009")
        expected = ('<table:table-cell office:value-type="date" '
                      'office:date-value="2009-06-30">'
                      '<text:p>30/6/2009</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_datetime(self):
        cell = odf_create_cell(datetime(2009, 6, 30, 17, 33, 18))
        expected = ('<table:table-cell office:value-type="date" '
                'office:date-value="2009-06-30T17:33:18">'
                      '<text:p>2009-06-30T17:33:18</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_datetime_repr(self):
        cell = odf_create_cell(datetime(2009, 6, 30, 17, 33, 18),
                               representation=u"30/6/2009 17:33")
        expected = ('<table:table-cell office:value-type="date" '
                'office:date-value="2009-06-30T17:33:18">'
                      '<text:p>30/6/2009 17:33</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_str(self):
        cell = odf_create_cell('red')
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="red">'
                      '<text:p>red</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_str_repr(self):
        cell = odf_create_cell('red', representation=u"Red")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="red">'
                      '<text:p>Red</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_unicode(self):
        cell = odf_create_cell(u"Plato")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="Plato">'
                      '<text:p>Plato</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_unicode_repr(self):
        cell = odf_create_cell(u"Plato", representation=u"P.")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="Plato">'
                      '<text:p>P.</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_timedelta(self):
        cell = odf_create_cell(timedelta(0, 8))
        expected = ('<table:table-cell office:value-type="time" '
                      'office:time-value="PT00H00M08S">'
                      '<text:p>PT00H00M08S</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_timedelta_repr(self):
        cell = odf_create_cell(timedelta(0, 8), representation=u"00:00:08")
        expected = ('<table:table-cell office:value-type="time" '
                      'office:time-value="PT00H00M08S">'
                      '<text:p>00:00:08</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_percentage(self):
        cell = odf_create_cell(90, cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>90</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_percentage_repr(self):
        cell = odf_create_cell(90, representation=u"90 %",
                               cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>90 %</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_currency(self):
        cell = odf_create_cell(1.54, cell_type='currency', currency='EUR')
        expected = ('<table:table-cell office:value-type="currency" '
                      'office:value="1.54" office:currency="EUR">'
                      '<text:p>1.54</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_currency_repr(self):
        cell = odf_create_cell(1.54, representation=u"1,54 €",
                               cell_type='currency', currency='EUR')
        expected = ('<table:table-cell office:value-type="currency" '
                      'office:value="1.54" office:currency="EUR">'
                      '<text:p>1,54 &#8364;</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_bad(self):
        self.assertRaises(TypeError, odf_create_cell, [])



class TestCreateRow(TestCase):

    def test_create_row(self):
        row = odf_create_row()
        expected = '<table:table-row/>'
        self.assertEqual(row.serialize(), expected)


    def test_create_row_width(self):
        row = odf_create_row(1)
        expected = ('<table:table-row>'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>')
        self.assertEqual(row.serialize(), expected)


    def test_create_row_repeated(self):
        row = odf_create_row(repeated=3)
        expected = '<table:table-row table:number-rows-repeated="3"/>'
        self.assertEqual(row.serialize(), expected)


    def test_create_row_style(self):
        row = odf_create_row(style=u"ro1")
        expected = '<table:table-row table:style-name="ro1"/>'
        self.assertEqual(row.serialize(), expected)


    def test_create_row_all(self):
        row = odf_create_row(1, repeated=3, style=u"ro1")
        expected = ('<table:table-row table:number-rows-repeated="3" '
                      'table:style-name="ro1">'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>')
        self.assertEqual(row.serialize(), expected)



class TestCreateColumn(TestCase):

    def test_create_column(self):
        column = odf_create_column()
        expected = '<table:table-column/>'
        self.assertEqual(column.serialize(), expected)


    def test_create_column_style(self):
        column = odf_create_column(style=u"A Style")
        expected = '<table:table-column table:style-name="A Style"/>'
        self.assertEqual(column.serialize(), expected)


    def test_create_column_default_cell_style(self):
        column = odf_create_column(default_cell_style=u"A Style")
        expected = ('<table:table-column '
                      'table:default-cell-style-name="A Style"/>')
        self.assertEqual(column.serialize(), expected)


    def test_create_column_repeated(self):
        column = odf_create_column(repeated=3)
        expected = '<table:table-column table:number-columns-repeated="3"/>'
        self.assertEqual(column.serialize(), expected)


    def test_create_column_all(self):
        column =  odf_create_column(style=u"co1",
                default_cell_style="Standard", repeated=3)
        expected = ('<table:table-column table:style-name="co1" '
                      'table:default-cell-style-name="A Style"/>'
                      'table:number-columns-repeated="3"/>')



class TestCreateTable(TestCase):

    def test_create_table(self):
        table = odf_create_table(u"A Table")
        expected = '<table:table table:name="A Table"/>'
        self.assertEqual(table.serialize(), expected)


    def test_create_table_style(self):
        table = odf_create_table(u"A Table", style=u"A Style")
        expected = ('<table:table table:name="A Table" '
                      'table:style-name="A Style"/>')
        self.assertEqual(table.serialize(), expected)


    def test_create_table_width_height(self):
        table = odf_create_table(u"A Table", width=1, height=2)
        expected = ('<table:table table:name="A Table">'
                    '<table:table-column table:number-columns-repeated="1"/>'
                    '<table:table-row>'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>'
                    '<table:table-row>'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)



class TestTable(TestCase):

    def setUp(self):
        document = document = odf_get_document('samples/simple_table.ods')
        self.document = document
        self.body = document.get_body()


    def test_get_table_list(self):
        body = self.body
        self.assertEqual(len(body.get_table_list()), 3)


    def test_get_table_list_style(self):
        body = self.body
        self.assertEqual(len(body.get_table_list(style=u"ta1")), 3)


    def test_get_table_by_name(self):
        body = self.body.clone()
        body.append_element(odf_create_table(u"New Table"))
        table = body.get_table_by_name(u"New Table")
        self.assertEqual(table.get_table_name(), u"New Table")


    def test_get_table_by_position(self):
        body = self.body.clone()
        body.append_element(odf_create_table(u"New Table"))
        table = body.get_table_by_position(4)
        self.assertEqual(table.get_table_name(), u"New Table")


    def test_style(self):
        table = self.body.get_table_by_position(1)
        self.assertEqual(table.get_table_style(), u"ta1")


    def test_print(self):
        table = self.body.get_table_by_position(1)
        self.assertEqual(table.is_table_printable(), False)


    def test_width_height(self):
        table = self.body.get_table_by_name(u"Example1")
        self.assertEqual(table.get_table_size(), (7, 4))


    def test_empty(self):
        table = odf_create_table(u"Empty")
        self.assertEqual(table.get_table_size(), (0, 0))


    def test_traverse_rows(self):
        table = self.body.get_table_by_name(u"Example1")
        rows = list(table.traverse_rows())
        self.assertEqual(len(rows), 4)
        row = rows[0]
        self.assertEqual(len(row.get_children()), 7)


    def test_traverse_columns(self):
        table = self.body.get_table_by_name(u"Example1")
        columns = list(table.traverse_columns())
        self.assertEqual(len(columns), 7)



class TestCSV(TestCase):

    def setUp(self):
        self.table = import_from_csv(StringIO(csv_data), u"From CSV")


    def test_import_from_csv(self):
        expected = ('<table:table table:name="table1" '
                      'table:style-name="Standard">'
                      '<table:table-column table:style-name="Standard" '
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



class TestCell(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table_by_name(u"Example1").clone()


    def test_get_cell(self):
        table = import_from_csv(StringIO(csv_data), u"From CSV")
        cell_A2 = table.get_cell('A2')
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="A date">'
                      '<text:p>A date</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell_A2.serialize(), expected)


    def test_get_cell_list_regex(self):
        # Find these cells
        #   |A B C D E F G
        # --+-------------
        # 1 |- - - - 3 3 3
        # 2 |- - - - 3 3 3
        # 3 |- - - - 3 3 3
        # 4 |- - 3 - - - -
        table = self.table.clone()
        coordinates = [(x, y)
                for x, y, cell in table.get_cell_list(regex=ur'3')]
        expected = [(4, 0), (5, 0), (6, 0), (4, 1), (5, 1), (6, 1), (4, 2),
                (5, 2), (6, 2), (2, 3)]
        self.assertEqual(coordinates, expected)


    def test_get_cell_list_style(self):
        # Find these cells
        #   |A B C D E F G
        # --+-------------
        # 1 |0 1 2 3 4 5 6
        # 2 |- - - - - - -
        # 3 |- - - - - - -
        # 4 |- - - - - - -
        table = self.table.clone()
        # Set the first line to : 0 1 2 3 4 5 6
        for i in xrange(7):
            cell = odf_create_cell(value=i, style=u'A Style')
            table.set_cell((i, 0), cell)
        coordinates = [(x, y)
                for x, y, cell in table.get_cell_list(style=ur'Style')]
        expected = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        self.assertEqual(coordinates, expected)



class TestRow(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table_by_name(u"Example1").clone()


    def test_get_row_list_regex(self):
        # Find these rows
        #   |A B C D E F G
        # --+-------------
        # 1 |7 - - - - - -
        # 2 |- - - - - - -
        # 3 |- - - - - - -
        # 4 |7 - - - - - 7
        table = self.table.clone()
        # Set some cells to the value 7
        cell = odf_create_cell(7)
        table.set_cell((0, 0), cell)
        cell = odf_create_cell(7)
        table.set_cell((0, 3), cell)
        coordinates = [y for y, row in table.get_row_list(regex=ur'7')]
        expected = [0, 3]
        self.assertEqual(coordinates, expected)


    def test_get_row_list_style(self):
        # Find these rows
        #   |A B C D E F G
        # --+-------------
        # 1 |- - - - - - -
        # 2*|- - - - - - -
        # 3 |- - - - - - -
        # 4*|- - - - - - -
        table = self.table.clone()
        # Set the styles
        row1 = table.get_row(1)
        row1.set_row_style(u"My Style")
        row3 =  table.get_row(3)
        row3.set_row_style(u"My Style")
        coordinates = [y for y, row in table.get_row_list(style=ur'Style')]
        expected = [1, 3]
        self.assertEqual(coordinates, expected)



class TestColumn(TestCase):

    def setUp(self):
        document = odf_get_document('samples/simple_table.ods')
        body = document.get_body()
        self.table = body.get_table_by_name(u"Example1").clone()


    def test_get_column_list_style(self):
        # Find these columns
        #   |A B*C D*E F G
        # --+-------------
        # 1 |- - - - - - -
        # 2 |- - - - - - -
        # 3 |- - - - - - -
        # 4 |- - - - - - -
        table = self.table.clone()
        # Set the styles
        column1 = table.get_column(1)
        column1.set_column_style(u"My Style")
        column3 = table.get_column(3)
        column3.set_column_style(u"My Style")
        coordinates = [x
                for x, column in table.get_column_list(style=ur'Style')]
        expected = [1, 3]
        self.assertEqual(coordinates, expected)



class TestOOoBugs(TestCase):

    def test_bug_openoffice(self):
        """Ensure empty rows have been removed.
        """
        document = odf_get_document('samples/styled_table.ods')
        body = document.get_body()
        table = body.get_table_by_name(u'Feuille1')
        self.assertEqual(table.get_table_size(), (1024, 9))



if __name__ == '__main__':
    main()
