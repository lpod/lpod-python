# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import new_odf_document_from_template
from lpod.document import new_odf_document_from_class, get_odf_document
from lpod.document import generate_xpath_query, check_arguments
from lpod.xmlpart import odf_create_element


class NewDocumentFromTemplateTestCase(TestCase):

    def test_bad_template(self):
        self.assertRaises(ValueError, new_odf_document_from_template,
                          '../templates/notexisting')

    def test_text_template(self):
        uri = '../templates/text.ott'
        self.assert_(new_odf_document_from_template(uri))


    def test_spreadsheet_template(self):
        uri = '../templates/spreadsheet.ots'
        self.assert_(new_odf_document_from_template(uri))


    def test_presentation_template(self):
        uri = '../templates/presentation.otp'
        self.assert_(new_odf_document_from_template(uri))


    def test_drawing_template(self):
        uri = '../templates/drawing.otg'
        self.assert_(new_odf_document_from_template(uri))



class NewdocumentFromClassTestCase(TestCase):

    def test_bad_class(self):
        self.assertRaises(ValueError, new_odf_document_from_class,
                          'foobar')


    def test_text_class(self):
        self.assert_(new_odf_document_from_class('text'))


    def test_spreadsheet_class(self):
        self.assert_(new_odf_document_from_class('spreadsheet'))


    def test_presentation_class(self):
        self.assert_(new_odf_document_from_class('presentation'))


    def test_drawing_class(self):
        self.assert_(new_odf_document_from_class('drawing'))



class GetDocumentTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        self.assert_(get_odf_document(path))


    def test_odf_xml(self):
        path = 'samples/example.xml'
        self.assert_(get_odf_document(path))


    def test_http(self):
        uri = 'http://test.lpod-project.org/example.odt'
        self.assert_(get_odf_document(uri))


    def test_ftp(self):
        uri = 'ftp://test.lpod-project.org/example.odt'
        self.assert_(get_odf_document(uri))



class GenerateXPathTestCase(TestCase):

    def test_element(self):
        query = generate_xpath_query('text:p')
        self.assertEqual(query, '//text:p')


    def test_attribute(self):
        attributes = {'text:style-name': 'Standard'}
        query = generate_xpath_query('text:p', attributes)
        self.assertEqual(query, '//text:p[@text:style-name="Standard"]')


    def test_two_attributes(self):
        attributes = {'text:style-name': 'Standard',
                      'text:level': 1}
        query = generate_xpath_query('text:h', attributes)
        expected = '//text:h[@text:style-name="Standard"][@text:level="1"]'
        self.assertEqual(query, expected)


    def test_position(self):
        query = generate_xpath_query('text:h', position=2)
        self.assertEqual(query, '//text:h[2]')


    def test_attribute_position(self):
        attributes = {'text:style-name': 'Standard'}
        query = generate_xpath_query('text:p', attributes, position=2)
        self.assertEqual(query, '//text:p[@text:style-name="Standard"][2]')


    def test_two_attributes_position(self):
        attributes = {'text:style-name': 'Standard',
                      'text:level': 1}
        query = generate_xpath_query('text:h', attributes, position=2)
        expected = '//text:h[@text:style-name="Standard"][@text:level="1"][2]'
        self.assertEqual(query, expected)



class CheckArgumentsTestCase(TestCase):

    def test_bad_context(self):
        document = get_odf_document('samples/example.odt')
        self.assertRaises(TypeError, check_arguments, context=document)


    def test_str_position(self):
        self.assertRaises(TypeError, check_arguments, position='1')


    def test_position_zero(self):
        self.assertRaises(ValueError, check_arguments, position=0)


    def test_bad_style(self):
        data = ('<style:master-page '
                'style:name="Standard" '
                'style:page-layout-name="Mpm1"/>')
        element = odf_create_element(data)
        self.assertRaises(TypeError, check_arguments, style=element)


    def test_str_level(self):
        self.assertRaises(TypeError, check_arguments, level='1')


    def test_level_zero(self):
        self.assertRaises(ValueError, check_arguments, level=0)



class DocumentTestCase(TestCase):

    def setUp(self):
        self.document = get_odf_document('samples/example.odt')


    def tearDown(self):
        del self.document



if __name__ == '__main__':
    main()
