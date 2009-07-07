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


if __name__ == '__main__':
    main()
