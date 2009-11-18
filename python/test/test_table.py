# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_type, odf_get_document
from lpod.element import LAST_CHILD, odf_create_element
from lpod.table import odf_create_row, odf_create_cell, odf_table
from lpod.table import odf_create_table, odf_create_column
from lpod.table import _get_cell_coordinates



def get_example():
    # Encode this table
    #   |A B C D E F G
    # --+-------------
    # 1 |1 1 1 2 3 3 3
    # 2 |1 1 1 2 3 3 3
    # 3 |1 1 1 2 3 3 3
    # 4 |1 2 3 4 5 6 7

    # Header
    data = ['<table:table table:name="a_table" '
              'table:style-name="Standard">'
              '<table:table-column table:style-name="Standard" '
                'table:number-columns-repeated="7"/>']

    # 3x "1 1 1 2 3 3 3"
    data.append('<table:table-row table:number-rows-repeated="3">')
    for i in range(1, 4):
        data.append(('<table:table-cell office:value-type="string" '
                      'office:string-value="%d"'
                      '%s>'
                      '<text:p>%d</text:p>'
                     '</table:table-cell>') %
                  (i,
                   ' table:number-columns-repeated="3"' if i != 2 else '',
                   i))
    data.append('</table:table-row>')

    # 1x "1 2 3 4 5 6 7"
    data.append('<table:table-row>')
    for i in range(1, 8):
        data.append(('<table:table-cell office:value-type="string" '
                        'office:string-value="%d">'
                        '<text:p>%d</text:p>'
                     '</table:table-cell>') % (i, i))
    data.append('</table:table-row>')

    # Footer
    data.append('</table:table>')

    return ''.join(data)



class TestGetCell(TestCase):

    def setUp(self):
        self.document = document = odf_new_document_from_type('text')
        self.body = body = document.get_body()

        # Encode this table
        #   A B C D E F G
        # 1 1 1 1 2 3 3 3
        # 2 1 1 1 2 3 3 3
        # 3 1 1 1 2 3 3 3
        # 4 1 2 3 4 5 6 7
        table = odf_create_table(u'a_table', style='Standard')
        column = odf_create_column(style=u'Standard')
        column.set_attribute('table:number-columns-repeated', '7')
        table.append_element(column)

        # 3 x "1 1 1 2 3 3 3"
        row = odf_create_row()
        row.set_attribute('table:number-rows-repeated', '3')
        # 3 x "1"
        cell = odf_create_cell(u'1')
        cell.set_attribute('table:number-columns-repeated', '3')
        row.append_element(cell)
        # 1 x "2"
        cell = odf_create_cell(u'2')
        row.append_element(cell)
        # 3 x "3"
        cell = odf_create_cell(u'3')
        cell.set_attribute('table:number-columns-repeated', '3')
        row.append_element(cell)

        table.append_element(row)

        # 1 x "1 2 3 4 5 6 7"
        row = odf_create_row()
        for i in xrange(1, 8):
            cell = odf_create_cell(unicode(i))
            row.append_element(cell)
        table.append_element(row)

        body.append_element(table)


    def test_get_cell_coordinates(self):
        x, y = _get_cell_coordinates('ABC123')
        self.assertEqual((x, y), (730, 122))



class TestTable(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/table.ods')
        self.body = document.get_body()


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


    def test_create_row(self):
        # Test 1
        row = odf_create_row()
        expected = '<table:table-row/>'
        self.assertEqual(row.serialize(), expected)

        # Test 2
        row = odf_create_row(1)
        expected = ('<table:table-row>'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>')
        self.assertEqual(row.serialize(), expected)


    def test_create_column(self):
        # Test create
        column = odf_create_column(style=u'A Style')
        expected = '<table:table-column table:style-name="A Style"/>'
        self.assertEqual(column.serialize(), expected)


    def test_create_table1(self):
        # Test 1
        table = odf_create_table(u'a_table', style='A Style')
        expected = ('<table:table table:name="a_table" '
                    'table:style-name="A Style"/>')
        self.assertEqual(table.serialize(), expected)


    def test_create_table2(self):
        # Test 2
        table = odf_create_table(u'a_table', width=1, height=2,
                                 style='A Style')
        expected = ('<table:table table:name="a_table" '
                    'table:style-name="A Style">'
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


    def test_insert_table(self):
        table = odf_create_table(u"New Table", style='A Style')
        column = odf_create_column(style=u'a_column_style')
        row = odf_create_row()
        cell = odf_create_cell(u"")

        table.append_element(column)
        row.append_element(cell)
        table.append_element(row)
        expected = ('<table:table table:name="New Table" '
                      'table:style-name="A Style">'
                      '<table:table-column '
                        'table:style-name="a_column_style"/>'
                      '<table:table-row>'
                        '<table:table-cell office:value-type="string" '
                          'office:string-value="">'
                          '<text:p></text:p>'
                        '</table:table-cell>'
                      '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)


    def test_get_table_by_name(self):
        body = self.body.clone()

        table = odf_create_table(u"New Table", style='A Style')
        body.append_element(table)

        # Get OK ?
        table = body.get_table_by_name(u"New Table")
        self.assertEqual(table.get_attribute('table:name'), u"New Table")


    def test_get_table_by_position(self):
        body = self.body.clone()
        table = odf_create_table(u"New Table", style='A Style')
        body.append_element(table)
        # Get OK ?
        table = body.get_table_by_position(4)
        self.assertEqual(table.get_attribute('table:name'), u"New Table")



class odf_table_TestCase(TestCase):

    def test_create_table_with_data(self):

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

        # With the python data
        data = [ (u'A float', 3.14),
                 (u'A date', datetime(1975, 5, 7)) ]
        table = odf_table('table1', style=u'Standard', data=data)
        serialized = table.to_odf_element().serialize()

        self.assertEqual(serialized, expected)


    def test_create_table_with_odf_element(self):

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


        # With an odf_element
        odf_element = odf_create_element(expected)

        table = odf_table(odf_element=odf_element)
        serialized = table.to_odf_element().serialize()

        self.assertEqual(serialized, expected)


    def test_create_with_repeat(self):
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)

        get_value = lambda coordinates: int(table.get_cell(coordinates).
                                      get_attribute('office:string-value'))

        # Tests
        self.assertEqual(get_value('C2'), 1)
        self.assertEqual(get_value('G3'), 3)
        self.assertEqual(get_value('B4'), 2)

        self.assertRaises(IndexError, get_value, 'A5')


    def test_get_cell(self):
        # With the python data
        data = [ (u'A float', 3.14),
                 (u'A date', datetime(1975, 5, 7)) ]

        table = odf_table('table1', 'Standard', data)
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
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)
        coordinates = table.get_cell_list(regex=ur'3')
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
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)
        # Set the first line to : 0 1 2 3 4 5 6
        for i in xrange(7):
            cell = odf_create_cell(value=i, style=u'A Style')
            table.set_cell((i, 0), cell)
        coordinates = table.get_cell_list(style=ur'Style')
        expected = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        self.assertEqual(coordinates, expected)


    def test_get_row_list_regex(self):
        # Find these rows
        #   |A B C D E F G
        # --+-------------
        # 1 |7 - - - - - -
        # 2 |- - - - - - -
        # 3 |- - - - - - -
        # 4 |7 - - - - - 7
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)
        # Set some cells to the value 7
        cell = odf_create_cell(value=7)
        table.set_cell((0, 0), cell)
        cell = odf_create_cell(value=7)
        table.set_cell((0, 3), cell)
        coordinates = table.get_row_list(regex=ur'7')
        expected = [0, 3]
        self.assertEqual(coordinates, expected)


    def test_get_row_list_style(self):
        # Find these rows
        #   |A B C D E F G
        # --+-------------
        # 1 |- - - - - - -
        # 2 |1 - - - - - 3
        # 3 |1 - - - - - 3
        # 4 |- - - - - - -
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)
        # Set the styles
        cell = table.get_cell((0, 1))
        cell.set_attribute('table:style-name', u'A Style')
        cell = table.get_cell((6, 1))
        cell.set_attribute('table:style-name', u'A Style')
        cell = table.get_cell((0, 2))
        cell.set_attribute('table:style-name', u'A Style')
        cell = table.get_cell((6, 2))
        cell.set_attribute('table:style-name', u'A Style')
        coordinates = table.get_row_list(style=ur'Style')
        expected = [1, 2]
        self.assertEqual(coordinates, expected)


    def test_get_column_list_regex(self):
        # Find these columns
        #   |A B C D E F G
        # --+-------------
        # 1 |- - - 2 - - -
        # 2 |- - - 2 - - -
        # 3 |- - - 2 - - -
        # 4 |- 2 - - - - -
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)
        coordinates = table.get_column_list(regex=ur'2')
        expected = [1, 3]
        self.assertEqual(coordinates, expected)


    def test_get_column_list_style(self):
        # Find these columns
        #   |A B C D E F G
        # --+-------------
        # 1 |1 - - - - - -
        # 2 |1 - - - - - -
        # 3 |- - - - - - 3
        # 4 |- - - - - - 7
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)
        # Set the styles
        cell = table.get_cell((0, 0))
        cell.set_attribute('table:style-name', u'A Style')
        cell = table.get_cell((0, 1))
        cell.set_attribute('table:style-name', u'A Style')
        cell = table.get_cell((6, 2))
        cell.set_attribute('table:style-name', u'A Style')
        cell = table.get_cell((6, 3))
        cell.set_attribute('table:style-name', u'A Style')
        coordinates = table.get_column_list(style=ur'[sS]tyle')
        expected = [0, 6]
        self.assertEqual(coordinates, expected)


    def test_to_odf_element(self):
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)

        table_serialized = table.to_odf_element().serialize()
        self.assertEqual(table_serialized, data)


    def test_change_table(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        # Force repeat
        table1 = odf_table(name=u'table', style='Standard', data=data1)
        table1 = odf_table(odf_element=table1.to_odf_element())

        # Change the value of C2 to 3, not with a new cell, but with the same
        cell = table1.get_cell('C2')
        cell.set_attribute('office:value', u'3')
        paragraph = cell.get_element('text:p')
        paragraph.set_text(u'3')

        # Expected
        data2 = ((1, 1, 1, 1),
                 (1, 1, 3, 1),
                 (2, 2, 2, 2))
        table2 = odf_table(name=u'table', style='Standard', data=data2)

        self.assertEqual(table1.to_odf_element().serialize(),
                         table2.to_odf_element().serialize())


    def test_set_cell_table(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        # Force repeat
        table1 = odf_table(name=u'table', style='Standard', data=data1)
        table1 = odf_table(odf_element=table1.to_odf_element())

        # Change the value of C2 to 3 with a new cell
        cell = odf_create_cell(3)
        table1.set_cell('C2', cell)

        # Expected
        data2 = ((1, 1, 1, 1),
                 (1, 1, 3, 1),
                 (2, 2, 2, 2))
        table2 = odf_table(name=u'table', style='Standard', data=data2)

        self.assertEqual(table1.to_odf_element().serialize(),
                         table2.to_odf_element().serialize())


    def test_bug_openoffice(self):
        document = odf_get_document('samples/table.ods')
        body = document.get_body()
        table = body.get_table_by_name(u'Feuille1')
        table = odf_table(odf_element=table)
        self.assertEqual(table.get_size(), (1024, 9))


    def test_add_row(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        table1 = odf_table(name=u'table', style='Standard', data=data1)

        table1.add_row()
        self.assertEqual(table1.get_size(), (4, 4))

        table1.add_row(number=2, position=2)
        self.assertEqual(table1.get_size(), (4, 6))

        # Test the table
        data2 = ((1, 1, 1, 1),
                 (None, None, None, None),
                 (None, None, None, None),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2),
                 (None, None, None, None))
        table2 = odf_table(name=u'table', style='Standard', data=data2)
        self.assertEqual(table1.to_odf_element().serialize(),
                         table2.to_odf_element().serialize())


    def test_add_column(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        table1 = odf_table(name=u'table', style='Standard', data=data1)

        table1.add_column()
        self.assertEqual(table1.get_size(), (5, 3))

        table1.add_column(number=2, position=2)
        self.assertEqual(table1.get_size(), (7, 3))

        # Test the table
        data2 = ((1, None, None, 1, 1, 1, None),
                 (1, None, None, 1, 1, 1, None),
                 (2, None, None, 2, 2, 2, None))
        table2 = odf_table(name=u'table', style='Standard', data=data2)
        self.assertEqual(table1.to_odf_element().serialize(),
                         table2.to_odf_element().serialize())



if __name__ == '__main__':
    main()
