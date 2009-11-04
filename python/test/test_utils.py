# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.table import odf_create_cell
from lpod.variable import odf_create_variable_set, odf_create_user_field_decl
from lpod.utils import _make_xpath_query
from lpod.utils import get_value, set_value, convert_unicode


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
        query = _make_xpath_query('descendant::text:h', position=2)
        self.assertEqual(query, '(descendant::text:h)[2]')


    def test_attribute_position(self):
        query = _make_xpath_query('descendant::text:p',
                text_style=u"Standard", position=2)
        self.assertEqual(query,
                '(descendant::text:p[@text:style-name="Standard"])[2]')


    def test_two_attributes_position(self):
        query = _make_xpath_query('descendant::text:h',
                text_style=u"Standard", outline_level=1, position=2)
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



if __name__ == '__main__':
    main()
