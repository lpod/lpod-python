# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_template
from lpod.document import odf_new_document_from_type, odf_get_document


class NewDocumentFromTemplateTestCase(TestCase):

    def test_bad_template(self):
        self.assertRaises(ValueError, odf_new_document_from_template,
                          '../templates/notexisting')

    def test_text_template(self):
        uri = '../templates/text.ott'
        self.assert_(odf_new_document_from_template(uri))


    def test_spreadsheet_template(self):
        uri = '../templates/spreadsheet.ots'
        self.assert_(odf_new_document_from_template(uri))


    def test_presentation_template(self):
        uri = '../templates/presentation.otp'
        self.assert_(odf_new_document_from_template(uri))


    def test_drawing_template(self):
        uri = '../templates/drawing.otg'
        self.assert_(odf_new_document_from_template(uri))



class NewdocumentFromTypeTestCase(TestCase):

    def test_bad_type(self):
        self.assertRaises(ValueError, odf_new_document_from_type,
                          'foobar')


    def test_text_type(self):
        self.assert_(odf_new_document_from_type('text'))


    def test_spreadsheet_type(self):
        self.assert_(odf_new_document_from_type('spreadsheet'))


    def test_presentation_type(self):
        self.assert_(odf_new_document_from_type('presentation'))


    def test_drawing_type(self):
        self.assert_(odf_new_document_from_type('drawing'))



class GetDocumentTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        self.assert_(odf_get_document(path))


    def test_odf_xml(self):
        path = 'samples/example.xml'
        self.assert_(odf_get_document(path))


    def test_http(self):
        uri = 'http://ftp.lpod-project.org/example.odt'
        self.assert_(odf_get_document(uri))


    def test_ftp(self):
        uri = 'ftp://ftp.lpod-project.org/example.odt'
        self.assert_(odf_get_document(uri))



class DocumentTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_get_body(self):
        document = self.document
        body = document.get_body()
        self.assertEqual(body.get_name(), 'office:text')


    def test_clone(self):
        document = self.document
        document.get_xmlpart('content')
        self.assertNotEqual(document._odf_document__xmlparts, {})
        clone = document.clone()
        self.assertNotEqual(clone._odf_document__xmlparts, {})
        parts = clone._odf_document__xmlparts
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts.keys(), ['content'])
        container = clone.container
        self.assertEqual(container.uri, None)


class TestStyle(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_get_style_list(self):
        document = self.document
        styles = document.get_style_list()
        self.assertEqual(len(styles), 18)


    def test_get_style_list_family(self):
        document = self.document
        styles = document.get_style_list(family='paragraph')
        self.assertEqual(len(styles), 11)


    def test_get_style_automatic(self):
        document = self.document
        style = document.get_style(u'P1', 'paragraph')
        self.assertNotEqual(style, None)


    def test_get_style_named(self):
        document = self.document
        style = document.get_style(u'Heading_20_1', 'paragraph')
        self.assertNotEqual(style, None)



if __name__ == '__main__':
    main()
