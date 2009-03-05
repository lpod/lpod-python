# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import new_odf_document_from_template
from lpod.document import new_odf_document_from_class, get_odf_document
from lpod.document import generate_xpath_query, check_arguments


class NewDocumentFromTemplateTestCase(TestCase):

    def test_bad_template(self):
        self.assertRaises(ValueError, new_odf_document_from_template,
                          '../templates/notexisting')

    def test_text_template(self):
        new_odf_document_from_template('../templates/text.ott')


    def test_spreadsheet_template(self):
        new_odf_document_from_template('../templates/spreadsheet.ots')


    def test_presentation_template(self):
        new_odf_document_from_template('../templates/presentation.otp')


    def test_drawing_template(self):
        new_odf_document_from_template('../templates/drawing.otg')



class NewdocumentFromClassTestCase(TestCase):

    def test_bad_class(self):
        self.assertRaises(ValueError, new_odf_document_from_class,
                          'foobar')


    def test_text_class(self):
        new_odf_document_from_class('text')


    def test_spreadsheet_class(self):
        new_odf_document_from_class('spreadsheet')


    def test_presentation_class(self):
        new_odf_document_from_class('presentation')


    def test_drawing_class(self):
        new_odf_document_from_class('drawing')



class GetDocumentTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        document = get_odf_document(path)


    def test_odf_xml(self):
        path = 'samples/example.xml'
        document = get_odf_document(path)


    def test_http(self):
        uri = 'http://test.lpod-project.org/example.odt'
        document = get_odf_document(uri)


    def test_ftp(self):
        uri = 'ftp://test.lpod-project.org/example.odt'
        document = get_odf_document(uri)



class GenerateXPathTestCase(TestCase):

    def test_element(self):
        query = generate_xpath_query('text:p')
        self.assertEqual(query, '//text:p')


    def test_attributes(self):
        raise NotImplementedError


    def test_position(self):
        raise NotImplementedError



class CheckArgumentsTestCase(TestCase):

    def test_bad_context(self):
        document = get_odf_document('samples/example.odt')
        self.assertRaises(TypeError, check_arguments, context=document)


    def test_str_position(self):
        self.assertRaises(TypeError, check_arguments, position='foo')


    def test_position_zero(self):
        self.assertRaises(ValueError, check_arguments, position=0)


    def test_bad_style(self):
        raise NotImplementedError


    def test_str_level(self):
        raise NotImplementedError


    def test_level_zero(self):
        raise NotImplementedError



class DocumentTestCase(TestCase):

    def setUp(self):
        self.document = get_odf_document('samples/example.odt')


    def tearDown(self):
        del self.document



if __name__ == '__main__':
    main()
