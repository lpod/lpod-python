# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime
from unittest import TestCase, main

# Import from the XML Library
from lxml.etree import Element

# Import from lpod
from lpod.document import odf_get_document
from lpod.utils import DATE_FORMAT, _generate_xpath_query, _check_arguments
from lpod.xmlpart import odf_create_element


class GenerateXPathTestCase(TestCase):

    def test_element(self):
        query = _generate_xpath_query('text:p')
        self.assertEqual(query, '//text:p')


    def test_attribute(self):
        attributes = {'text:style-name': 'Standard'}
        query = _generate_xpath_query('text:p', attributes)
        self.assertEqual(query, '//text:p[@text:style-name="Standard"]')


    def test_two_attributes(self):
        attributes = {'text:style-name': 'Standard',
                      'text:outline-level': 1}
        query = _generate_xpath_query('text:h', attributes)
        expected = ('//text:h[@text:outline-level="1"]'
                    '[@text:style-name="Standard"]')
        self.assertEqual(query, expected)


    def test_position(self):
        query = _generate_xpath_query('text:h', position=2)
        self.assertEqual(query, '//text:h[2]')


    def test_attribute_position(self):
        attributes = {'text:style-name': 'Standard'}
        query = _generate_xpath_query('text:p', attributes, position=2)
        self.assertEqual(query, '//text:p[@text:style-name="Standard"][2]')


    def test_two_attributes_position(self):
        attributes = {'text:style-name': 'Standard',
                      'text:outline-level': 1}
        query = _generate_xpath_query('text:h', attributes, position=2)
        expected = ('//text:h[@text:outline-level="1"]'
                    '[@text:style-name="Standard"][2]')
        self.assertEqual(query, expected)



class CheckArgumentsTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_bad_context(self):
        self.assertRaises(TypeError, _check_arguments, context=self.document)


    def test_bad_element(self):
        self.assertRaises(TypeError, _check_arguments, element=Element)


    def test_str_xmlposition(self):
        self.assertRaises(ValueError, _check_arguments, xmlposition='after')


    def test_big_xmlposition(self):
        self.assertRaises(ValueError, _check_arguments, xmlposition=999)


    def test_str_position(self):
        self.assertRaises(TypeError, _check_arguments, position='1')


    def test_position_zero(self):
        self.assertRaises(ValueError, _check_arguments, position=0)


    def test_str_level(self):
        self.assertRaises(TypeError, _check_arguments, level='1')


    def test_level_zero(self):
        self.assertRaises(ValueError, _check_arguments, level=0)


    def test_bad_text(self):
        self.assertRaises(TypeError, _check_arguments, text='Hello')


    def test_bad_style(self):
        data = ('<style:master-page '
                'style:name="Standard" '
                'style:page-layout-name="Mpm1"/>')
        element = odf_create_element(data)
        self.assertRaises(TypeError, _check_arguments, style=element)


    def test_bad_family(self):
        self.assertRaises(ValueError, _check_arguments, family='heading')


    def test_bad_cell_type(self):
        self.assertRaises(ValueError, _check_arguments, cell_type='integer')


    def test_missing_currency(self):
        self.assertRaises(ValueError, _check_arguments, cell_type='currency')


    def test_bad_author(self):
        self.assertRaises(TypeError, _check_arguments, author='Plato')


    def test_bad_date(self):
        self.assertRaises(TypeError, _check_arguments,
                          date='2009-06-22T17:18:42')


    def test_bad_start_date(self):
        self.assertRaises(TypeError, _check_arguments,
                          start_date='2009-06-22T17:18:42')


    def test_bad_end_date(self):
        self.assertRaises(TypeError, _check_arguments,
                          end_date='2009-06-22T17:18:42')


    def test_bad_offset(self):
        self.assertRaises(TypeError, _check_arguments, offset='a word')


    def test_position_name(self):
        document = self.document
        self.assertRaises(ValueError, document.get_frame, position=1,
                          name='foo')
        self.assertRaises(ValueError, document.get_frame, position=None,
                          name=None)


class FormatsTestCase(TestCase):


    def test_date_format(self):
        date = datetime(2009, 06, 26, 11, 9, 36)
        self.assertEqual(date.strftime(DATE_FORMAT), '2009-06-26T11:09:36')



if __name__ == '__main__':
    main()
