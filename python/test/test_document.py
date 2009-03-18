# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_template
from lpod.document import odf_new_document_from_class, odf_get_document
from lpod.document import _generate_xpath_query, _check_arguments
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
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


    def test_clone(self):
        document = self.document
        document._odf_document__get_xmlpart('content')
        self.assertNotEqual(document._odf_document__xmlparts, {})
        clone = document.clone()
        self.assertEqual(clone._odf_document__xmlparts, {})
        container = clone.container
        self.assertEqual(container.uri, None)


    def test_get_element_list_bad_context(self):
        document = self.document
        self.assertRaises(TypeError, document.get_paragraph_list,
                          context=document)


    def test_get_element_missed(self):
        document = self.document
        paragraph = document.get_paragraph(999)
        self.assertEqual(paragraph, None)


    #
    # Sections
    #

    def test_get_section_list(self):
        document = self.document
        sections = document.get_section_list()
        self.assertEqual(len(sections), 2)
        second = sections[1]
        name = second.get_attribute('text:name')
        self.assertEqual(name, "Section2")


    def test_get_section_list_style(self):
        document = self.document
        sections = document.get_section_list(style='Sect1')
        self.assertEqual(len(sections), 2)
        section = sections[0]
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section1")


    def test_get_section(self):
        document = self.document
        section = document.get_section(2)
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section2")


    #
    # Paragraphs
    #

    def test_get_paragraph_list(self):
        document = self.document
        paragraphs = document.get_paragraph_list()
        self.assertEqual(len(paragraphs), 6)
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
        section2 = document.get_section(2)
        paragraphs = document.get_paragraph_list(context=section2)
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, "First paragraph of the second section.")


    def test_get_paragraph(self):
        document = self.document
        paragraph = document.get_paragraph(4)
        text = paragraph.get_text()
        expected = 'This is the first paragraph of the second title.'
        self.assertEqual(text, expected)


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
        self.assertEqual(len(headings), 3)
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
        document = self.document
        section2 = document.get_section(2)
        headings = document.get_heading_list(context=section2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, "First Title of the Second Section");


    def test_get_heading(self):
        document = self.document
        heading = document.get_heading(2)
        text = heading.get_text()
        self.assertEqual(text, 'Level 2 Title')


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



class CreateTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_frame(self):
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


    def test_create_image(self):
        # Test create
        image = odf_create_image('path')
        expected = '<draw:image xlink:href="path"/>'
        self.assertEqual(image.serialize(), expected)

        # Insert OK ?
        frame = odf_create_frame('frame_image', 'Graphics', '0cm', '0cm')
        self.document.insert_image(image, frame)


    def test_create_cell(self):
        # Test create
        cell = odf_create_cell()
        expected = '<table:table-cell office:value-type="String"/>'
        self.assertEqual(cell.serialize(), expected)


    def test_create_row(self):
        # Test 1
        row = odf_create_row()
        expected = '<table:table-row/>'
        self.assertEqual(row.serialize(), expected)

        # Test 2
        row = odf_create_row(1)
        expected = ('<table:table-row>'
                    '<table:table-cell office:value-type="String"/>'
                    '</table:table-row>')
        self.assertEqual(row.serialize(), expected)


    def test_create_column(self):
        # Test create
        column = odf_create_column('a_style')
        expected = '<table:table-column table:style-name="a_style"/>'
        self.assertEqual(column.serialize(), expected)


    def test_create_table(self):
        # Test 1
        table = odf_create_table('a_table', 'a_style')
        expected = ('<table:table table:name="a_table" '
                    'table:style-name="a_style"/>')
        self.assertEqual(table.serialize(), expected)

        # Test 2
        table = odf_create_table('a_table', 'a_style', 1, 2)
        expected = ('<table:table table:name="a_table" '
                    'table:style-name="a_style">'
                    '<table:table-row>'
                    '<table:table-cell office:value-type="String"/>'
                    '</table:table-row>'
                    '<table:table-row>'
                    '<table:table-cell office:value-type="String"/>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)


    def test_create_insert_table(self):
        table = odf_create_table('a_table', 'a_style')
        column = odf_create_column('a_column_style')
        row = odf_create_row()
        cell = odf_create_cell()

        document = self.document
        document.insert_table(table)
        document.insert_column(column, table)
        document.insert_row(row, table)
        document.insert_cell(cell, row)

        expected = ('<table:table table:name="a_table" '
                    'table:style-name="a_style">'
                    '<table:table-column table:style-name="a_column_style"/>'
                    '<table:table-row>'
                    '<table:table-cell office:value-type="String"/>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)


if __name__ == '__main__':
    main()
