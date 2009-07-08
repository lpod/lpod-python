# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main
from datetime import datetime

# Import from lpod
from lpod.table import odf_table
from lpod.xmlpart import odf_create_element



class odf_table_TestCase(TestCase):

    def test_create_table(self):

        expected = ('<table:table table:name="table1" '
                      'table:style-name="Standard">'
                      '<table:table-column table:style-name="Standard"/>'
                      '<table:table-column table:style-name="Standard"/>'
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

        # Make the table
        data = ''.join(data)
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



if __name__ == '__main__':
    main()
