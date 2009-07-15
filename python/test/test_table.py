# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main
from datetime import datetime

# Import from lpod
from lpod.table import odf_table
from lpod.xmlpart import odf_create_element
from lpod.document import odf_create_cell, odf_get_document



def get_example():
    # Encode this table
    #   A B C D E F G
    # 1 1 1 1 2 3 3 3
    # 2 1 1 1 2 3 3 3
    # 3 1 1 1 2 3 3 3
    # 4 1 2 3 4 5 6 7

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



class odf_table_TestCase(TestCase):

    def test_create_table(self):

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
        table1 = odf_table('table1', 'Standard', data)
        data1 = table1.get_odf_element().serialize()

        self.assertEqual(data1, expected)

        # With an odf_element
        odf_element = odf_create_element(expected)

        table2 = odf_table(odf_element=odf_element)
        data2 = table2.get_odf_element().serialize()

        self.assertEqual(data2, expected)


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


    def test_get_odf_element(self):
        data = get_example()
        odf_element = odf_create_element(data)
        table = odf_table(odf_element=odf_element)

        table_serialized = table.get_odf_element().serialize()
        self.assertEqual(table_serialized, data)


    def test_change_table(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        # Force repeat
        table1 = odf_table(name='table', style='Standard', data=data1)
        table1 = odf_table(odf_element=table1.get_odf_element())

        # Change the value of C2 to 3, not with a new cell, but with the same
        cell = table1.get_cell('C2')
        cell.set_attribute('office:value', u'3')
        paragraph = cell.get_element('text:p')
        paragraph.set_text(u'3')

        # Expected
        data2 = ((1, 1, 1, 1),
                 (1, 1, 3, 1),
                 (2, 2, 2, 2))
        table2 = odf_table(name='table', style='Standard', data=data2)

        self.assertEqual(table1.get_odf_element().serialize(),
                         table2.get_odf_element().serialize())


    def test_set_cell_table(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        # Force repeat
        table1 = odf_table(name='table', style='Standard', data=data1)
        table1 = odf_table(odf_element=table1.get_odf_element())

        # Change the value of C2 to 3 with a new cell
        cell = odf_create_cell(3)
        table1.set_cell('C2', cell)

        # Expected
        data2 = ((1, 1, 1, 1),
                 (1, 1, 3, 1),
                 (2, 2, 2, 2))
        table2 = odf_table(name='table', style='Standard', data=data2)

        self.assertEqual(table1.get_odf_element().serialize(),
                         table2.get_odf_element().serialize())


    def test_bug_openoffice(self):
        document = odf_get_document('samples/table-example.ods')
        content = document.get_xmlpart('content')

        table = content.get_table('Feuille1')
        table = odf_table(odf_element=table)

        self.assertEqual(table.get_size(), (1024, 9))


    def test_add_row(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        table1 = odf_table(name='table', style='Standard', data=data1)

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
        table2 = odf_table(name='table', style='Standard', data=data2)
        self.assertEqual(table1.get_odf_element().serialize(),
                         table2.get_odf_element().serialize())


    def test_add_column(self):
        data1 = ((1, 1, 1, 1),
                 (1, 1, 1, 1),
                 (2, 2, 2, 2))
        table1 = odf_table(name='table', style='Standard', data=data1)

        table1.add_column()
        self.assertEqual(table1.get_size(), (5, 3))

        table1.add_column(number=2, position=2)
        self.assertEqual(table1.get_size(), (7, 3))

        # Test the table
        data2 = ((1, None, None, 1, 1, 1, None),
                 (1, None, None, 1, 1, 1, None),
                 (2, None, None, 2, 2, 2, None))
        table2 = odf_table(name='table', style='Standard', data=data2)
        self.assertEqual(table1.get_odf_element().serialize(),
                         table2.get_odf_element().serialize())



if __name__ == '__main__':
    main()
