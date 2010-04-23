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
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.table import odf_create_cell
from lpod.utils import _make_xpath_query
from lpod.utils import get_value, set_value, convert_unicode, oooc_to_ooow
from lpod.variable import odf_create_variable_set, odf_create_user_field_decl

class GenerateXPathTestCase(TestCase):

    def test_element(self):
        query = _make_xpath_query('descendant::text:p')
        self.assertEqual(query, 'descendant::text:p')


    def test_attribute(self):
        query = _make_xpath_query('descendant::text:p',
                text_style=u"Standard")
        self.assertEqual(query,
                         'descendant::text:p[@text:style-name="Standard"]')


    def test_two_attributes(self):
        query = _make_xpath_query('descendant::text:h',
                text_style=u"Standard", outline_level=1)
        expected = ('descendant::text:h[@text:outline-level="1"]'
                    '[@text:style-name="Standard"]')
        self.assertEqual(query, expected)


    def test_position(self):
        query = _make_xpath_query('descendant::text:h', position=1)
        self.assertEqual(query, '(descendant::text:h)[2]')


    def test_attribute_position(self):
        query = _make_xpath_query('descendant::text:p',
                text_style=u"Standard", position=1)
        self.assertEqual(query,
                '(descendant::text:p[@text:style-name="Standard"])[2]')


    def test_two_attributes_position(self):
        query = _make_xpath_query('descendant::text:h',
                text_style=u"Standard", outline_level=1, position=1)
        expected = ('(descendant::text:h[@text:outline-level="1"]'
                    '[@text:style-name="Standard"])[2]')
        self.assertEqual(query, expected)



class Get_ValueTestCase(TestCase):

    def test_with_cell(self):

        cell = odf_create_cell(42)
        self.assertEqual(get_value(cell), 42)


    def test_with_variable(self):

        variable_set = odf_create_variable_set(u'你好 Zoé', 42)
        self.assertEqual(get_value(variable_set), 42)


    def test_with_user_field(self):
        user_field_decl = odf_create_user_field_decl(u'你好 Zoé', 42)
        self.assertEqual(get_value(user_field_decl), 42)



class Set_Get_ValueTestCase(TestCase):

    def test_with_cell(self):
        cell = odf_create_cell(42)
        set_value(cell, u'你好 Zoé')
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="%s">'
                      '<text:p>'
                        '%s'
                      '</text:p>'
                    '</table:table-cell>') % (
                                (convert_unicode(u'你好 Zoé'),) * 2)
        self.assertEqual(cell.serialize(), expected)


    def test_with_variable(self):
        variable_set = odf_create_variable_set(u'你好 Zoé', 42)
        set_value(variable_set, u'你好 Zoé')
        expected = ('<text:variable-set office:value-type="string" '
                      'office:string-value="%s" text:name="%s" '
                      'text:display="none">'
                      '%s'
                    '</text:variable-set>') % (
                            (convert_unicode(u'你好 Zoé'),) * 3)
        self.assertEqual(variable_set.serialize(), expected)


    def test_with_user_field(self):
        user_field_decl = odf_create_user_field_decl(u'你好 Zoé', 42)
        set_value(user_field_decl, u'你好 Zoé')
        expected = (('<text:user-field-decl office:value-type="string" '
                       'office:string-value="%s" text:name="%s"/>') %
                            ((convert_unicode(u'你好 Zoé'),) * 2))
        self.assertEqual(user_field_decl.serialize(), expected)



class get_by_position_TestCase(TestCase):

    def setUp(self):
        doc = odf_get_document("samples/example.odt")
        self.body = doc.get_body()


    def test_first(self):
        last_paragraph = self.body.get_paragraph_by_position(0)
        expected = u"This is the first paragraph."
        self.assertEqual(last_paragraph.get_text(recursive=True), expected)


    def test_next_to_last(self):
        last_paragraph = self.body.get_paragraph_by_position(-2)
        expected = u"This is an annotation."
        self.assertEqual(last_paragraph.get_text(recursive=True), expected)


    def test_last(self):
        last_paragraph = self.body.get_paragraph_by_position(-1)
        expected = u"With diacritical signs: éè"
        self.assertEqual(last_paragraph.get_text(recursive=True), expected)



class FormulaConvertTestCase(TestCase):

    def test_addition(self):
        formula = "oooc:=[.A2]+[.A3]"
        excepted = "ooow:<A2>+<A3>"
        self.assertEqual(oooc_to_ooow(formula), excepted)


    def test_sum(self):
        formula = "oooc:=SUM([.B2:.B4])"
        excepted = "ooow:sum <B2:B4>"
        self.assertEqual(oooc_to_ooow(formula), excepted)


    def test_addition_sum(self):
        formula = "oooc:=[.A2]-[.A3]+SUM([.B2:.B4])*[.D4]"
        excepted = "ooow:<A2>-<A3>+sum <B2:B4>*<D4>"
        self.assertEqual(oooc_to_ooow(formula), excepted)



if __name__ == '__main__':
    main()
