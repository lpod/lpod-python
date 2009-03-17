# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_template
from lpod.document import odf_new_document_from_class, odf_get_document
from lpod.document import _generate_xpath_query, _check_arguments
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame
from lpod.xmlpart import odf_create_element


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



class NewdocumentFromClassTestCase(TestCase):

    def test_bad_class(self):
        self.assertRaises(ValueError, odf_new_document_from_class,
                          'foobar')


    def test_text_class(self):
        self.assert_(odf_new_document_from_class('text'))


    def test_spreadsheet_class(self):
        self.assert_(odf_new_document_from_class('spreadsheet'))


    def test_presentation_class(self):
        self.assert_(odf_new_document_from_class('presentation'))


    def test_drawing_class(self):
        self.assert_(odf_new_document_from_class('drawing'))



class GetDocumentTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        self.assert_(odf_get_document(path))


    def test_odf_xml(self):
        path = 'samples/example.xml'
        self.assert_(odf_get_document(path))


    def test_http(self):
        uri = 'http://test.lpod-project.org/example.odt'
        self.assert_(odf_get_document(uri))


    def test_ftp(self):
        uri = 'ftp://test.lpod-project.org/example.odt'
        self.assert_(odf_get_document(uri))



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

    def test_bad_context(self):
        document = odf_get_document('samples/example.odt')
        self.assertRaises(TypeError, _check_arguments, context=document)


    def test_str_position(self):
        self.assertRaises(TypeError, _check_arguments, position='1')


    def test_position_zero(self):
        self.assertRaises(ValueError, _check_arguments, position=0)


    def test_bad_style(self):
        data = ('<style:master-page '
                'style:name="Standard" '
                'style:page-layout-name="Mpm1"/>')
        element = odf_create_element(data)
        self.assertRaises(TypeError, _check_arguments, style=element)


    def test_str_level(self):
        self.assertRaises(TypeError, _check_arguments, level='1')


    def test_level_zero(self):
        self.assertRaises(ValueError, _check_arguments, level=0)



class DocumentTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_get_paragraph_list(self):
        document = self.document
        paragraphs = document.get_paragraph_list()
        self.assertEqual(len(paragraphs), 5)
        second = paragraphs[1]
        text = second.get_text()
        self.assertEqual(text, 'This is the second paragraph.')


    def test_get_paragraph_list_style(self):
        document = self.document
        paragraphs = document.get_paragraph_list(style='Hanging_20_indent')
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, 'This is a paragraph with a named style.')


    def test_get_paragraph_list_context(self):
        document = self.document
        paragraphs = document.get_paragraph_list(style='Hanging_20_indent')
        paragraph = paragraphs[0]
        paragraphs = document.get_paragraph_list(style='Hanging_20_indent',
                                                 context=paragraph)
        self.assertEqual(len(paragraphs), 0)


    def test_get_paragraph(self):
        document = self.document
        paragraph = document.get_paragraph(4)
        text = paragraph.get_text()
        expected = 'This is the first paragraph of the second title.'
        self.assertEqual(text, expected)


    def test_get_paragraph_missed(self):
        document = self.document
        paragraph = document.get_paragraph(999)
        self.assertEqual(paragraph, None)


    def test_insert_paragraph(self):
        document = self.document
        paragraph = odf_create_paragraph('Text_20_body',
                                         'An inserted test')
        document.insert_paragraph(paragraph)
        last_paragraph = document.get_paragraph_list()[-1]
        self.assertEqual(last_paragraph.get_text(), 'An inserted test')



    def test_get_heading_list(self):
        document = self.document
        headings = document.get_heading_list()
        self.assertEqual(len(headings), 2)
        second = headings[1]
        text = second.get_text()
        self.assertEqual(text, 'Level 2 Title')


    def test_get_heading_list_style(self):
        document = self.document
        headings = document.get_heading_list(style='Heading_20_2')
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, 'Level 2 Title')


    def test_get_heading_list_level(self):
        document = self.document
        headings = document.get_heading_list(level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, 'Level 2 Title')


    def test_get_heading_list_style_level(self):
        document = self.document
        headings = document.get_heading_list(style='Heading_20_2', level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, 'Level 2 Title')


    def test_get_heading_list_context(self):
        raise NotImplementedError


    def test_get_heading(self):
        document = self.document
        heading = document.get_heading(2)
        text = heading.get_text()
        self.assertEqual(text, 'Level 2 Title')


    def test_get_heading_missed(self):
        document = self.document
        heading = document.get_heading(999)
        self.assertEqual(heading, None)


    def test_get_heading_level(self):
        document = self.document
        heading = document.get_heading(1, level=2)
        text = heading.get_text()
        self.assertEqual(text, 'Level 2 Title')


    def test_insert_heading(self):
        document = self.document
        heading = odf_create_heading('Heading_20_2', 2,
                                       'An inserted heading')
        document.insert_heading(heading)
        last_heading = document.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), 'An inserted heading')


    def test_frame(self):
        # Test 1
        frame = odf_create_frame('frame1', 'Graphics', '10cm', '10cm')
        expected = ('<draw:frame draw:name="frame1" '
                    'draw:style-name="Graphics" svg:width="10cm" '
                    'svg:height="10cm" text:anchor-type="paragraph"/>')
        self.assertEqual(frame.serialize(), expected)

        # Test 2
        frame = odf_create_frame('frame1', 'Graphics', '10cm', '10cm',
                                 page=1, x='10mm', y='10mm')
        expected = ('<draw:frame draw:name="frame1" '
                    'draw:style-name="Graphics" svg:width="10cm" '
                    'svg:height="10cm" text:anchor-type="page" '
                    'text:anchor-page-number="1" svg:x="10mm" svg:y="10mm"/>')
        self.assertEqual(frame.serialize(), expected)

        # Insert OK ?
        self.document.insert_frame(frame)




if __name__ == '__main__':
    main()
