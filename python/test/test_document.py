# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_template
from lpod.document import odf_new_document_from_class, odf_get_document
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.document import odf_create_item, odf_create_list
from lpod.document import odf_create_style, odf_create_style_text_properties
from lpod.document import odf_create_note, odf_create_annotation
from lpod.utils import _get_cell_coordinates


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
        # FIXME the annotation paragraph is counted
        self.assertEqual(len(paragraphs), 7)
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
        clone = document.clone()
        paragraph = odf_create_paragraph('Text_20_body',
                                         u'An inserted test')
        clone.insert_paragraph(paragraph)
        last_paragraph = clone.get_paragraph_list()[-1]
        self.assertEqual(last_paragraph.get_text(), u'An inserted test')


    #
    # Headings
    #

    def test_get_heading_list(self):
        document = self.document
        headings = document.get_heading_list()
        self.assertEqual(len(headings), 3)
        second = headings[1]
        text = second.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style(self):
        document = self.document
        headings = document.get_heading_list(style='Heading_20_2')
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_level(self):
        document = self.document
        headings = document.get_heading_list(level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style_level(self):
        document = self.document
        headings = document.get_heading_list(style='Heading_20_2', level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_context(self):
        document = self.document
        section2 = document.get_section(2)
        headings = document.get_heading_list(context=section2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u"First Title of the Second Section");


    def test_get_heading(self):
        document = self.document
        heading = document.get_heading(2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_level(self):
        document = self.document
        heading = document.get_heading(1, level=2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_insert_heading(self):
        document = self.document
        clone = document.clone()
        heading = odf_create_heading('Heading_20_2', 2,
                                     u'An inserted heading')
        clone.insert_heading(heading)
        last_heading = clone.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



class CreateTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_frame(self):
        document = self.document

        # Test 1
        frame1 = odf_create_frame('frame1', 'Graphics', '10cm', '10cm')
        expected = ('<draw:frame draw:name="frame1" '
                    'draw:style-name="Graphics" svg:width="10cm" '
                    'svg:height="10cm" text:anchor-type="paragraph"/>')
        self.assertEqual(frame1.serialize(), expected)

        # Test 2
        frame2 = odf_create_frame('frame2', 'Graphics', '10cm', '10cm',
                                  page=1, x='10mm', y='10mm')
        expected = ('<draw:frame draw:name="frame2" '
                    'draw:style-name="Graphics" svg:width="10cm" '
                    'svg:height="10cm" text:anchor-type="page" '
                    'text:anchor-page-number="1" svg:x="10mm" svg:y="10mm"/>')
        self.assertEqual(frame2.serialize(), expected)

        # Insert OK ?
        document.insert_frame(frame1)
        document.insert_frame(frame2)

        # Get OK ?
        get = document.get_frame(name='frame1')
        self.assertEqual(get.get_attribute('draw:name'), 'frame1')

        get = document.get_frame(position=2)
        self.assertEqual(get.get_attribute('draw:name'), 'frame2')


    def test_create_image(self):
        document = self.document

        # Test create
        image = odf_create_image('path')
        expected = '<draw:image xlink:href="path"/>'
        self.assertEqual(image.serialize(), expected)

        # Insert OK ?
        frame = odf_create_frame('frame_image', 'Graphics', '0cm', '0cm')
        document.insert_image(image, frame)
        document.insert_frame(frame)

        # Get OK ?
        get = document.get_image(name='frame_image')
        self.assertEqual(get.get_attribute('xlink:href'), 'path')

        get = document.get_image(position=1)
        self.assertEqual(get.get_attribute('xlink:href'), 'path')



    def test_create_cell(self):
        # Test create
        cell = odf_create_cell()
        expected = '<table:table-cell office:value-type="string"/>'
        self.assertEqual(cell.serialize(), expected)


    def test_create_row(self):
        # Test 1
        row = odf_create_row()
        expected = '<table:table-row/>'
        self.assertEqual(row.serialize(), expected)

        # Test 2
        row = odf_create_row(1)
        expected = ('<table:table-row>'
                    '<table:table-cell office:value-type="string"/>'
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
                    '<table:table-cell office:value-type="string"/>'
                    '</table:table-row>'
                    '<table:table-row>'
                    '<table:table-cell office:value-type="string"/>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)


    def test_create_insert_table(self):
        table = odf_create_table('a_table', 'a_style')
        column = odf_create_column('a_column_style')
        row = odf_create_row()
        cell = odf_create_cell()

        # Insert OK ?
        document = self.document
        document.insert_table(table)
        document.insert_column(column, table)
        document.insert_row(row, table)
        document.insert_cell(cell, row)

        expected = ('<table:table table:name="a_table" '
                    'table:style-name="a_style">'
                    '<table:table-column table:style-name="a_column_style"/>'
                    '<table:table-row>'
                    '<table:table-cell office:value-type="string"/>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)

        # Get OK ?
        get = document.get_table(name='a_table')
        self.assertEqual(get.get_attribute('table:name'), 'a_table')

        get = document.get_table(position=1)
        self.assertEqual(get.get_attribute('table:name'), 'a_table')


    def test_create_item(self):
        # Test create
        item = odf_create_item()
        expected = '<text:list-item/>'
        self.assertEqual(item.serialize(), expected)


    def test_create_insert_list(self):
        # Test create / insert
        item = odf_create_item()
        a_list = odf_create_list('a_style')
        document = self.document
        document.insert_item(item, a_list)
        document.insert_list(a_list)

        expected = ('<text:list text:style-name="a_style">'
                    '<text:list-item/>'
                    '</text:list>')
        self.assertEqual(a_list.serialize(), expected)


    def test_create_style(self):
        document = self.document

        # Create OK ?
        style = odf_create_style('style1', 'paragraph')

        properties = odf_create_style_text_properties()
        properties.set_attribute('fo:color', '#0000ff')
        properties.set_attribute('fo:background-color', '#ff0000')

        # Insert OK ?
        document.insert_style_properties(properties, style)
        document.insert_style(style)

        expected = ('<style:style style:name="style1" '
                                 'style:family="paragraph">'
                      '<style:text-properties fo:color="#0000ff" '
                                             'fo:background-color="#ff0000"/>'
                    '</style:style>')
        get1 = document.get_style('style1')
        get2 = document.get_style_list()[-1]
        self.assertEqual(get1.serialize(), expected)
        self.assertEqual(get2.serialize(), expected)


    def test_create_note(self):
        document = self.document

        # Create OK ?
        note = odf_create_note(u'1', id='note1')
        body = odf_create_paragraph('Standard', u'a footnote')

        # Insert OK ?
        document.insert_note_body(body, note)
        document.insert_note(note)

        # Get OK ?
        expected = ('<text:note text:note-class="footnote" text:id="note1">'
                      '<text:note-citation>1</text:note-citation>'
                      '<text:note-body>'
                        '<text:p text:style-name="Standard">'
                          'a footnote'
                        '</text:p>'
                      '</text:note-body>'
                    '</text:note>')
        get1 = document.get_note('note1')
        get2 = document.get_note_list(note_class='footnote')[-1]
        self.assertEqual(get1.serialize(), expected)
        self.assertEqual(get2.serialize(), expected)



class TestAnnotation(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_annotation(self):
        # Create
        annotation = odf_create_annotation(u"Plato", u"Lost Dialogs",
                datetime(2009, 6, 22, 17, 18, 42))
        expected = ('<office:annotation>'
                      '<dc:creator>Plato</dc:creator>'
                      '<dc:date>2009-06-22T17:18:42</dc:date>'
                      '<text:p>'
                        'Lost Dialogs'
                      '</text:p>'
                    '</office:annotation>')
        self.assertEqual(annotation.serialize(), expected)


    def test_get_annotation_list(self):
        document = self.document
        annotations = document.get_annotation_list()
        self.assertEqual(len(annotations), 1)
        annotation = annotations[0]
        creator = annotation.get_creator()
        self.assertEqual(creator, u"Auteur inconnu")
        date = annotation.get_date()
        self.assertEqual(date, datetime(2009, 6, 22, 17, 18, 42))
        text = annotation.get_text_content()
        self.assertEqual(text, u"This is an annotation")


    def test_get_annotation_list_author(self):
        document = self.document
        creator = u"Auteur inconnu"
        annotations = document.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author(self):
        document = self.document
        creator = u"Plato"
        annotations = document.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date(self):
        document = self.document
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = document.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date(self):
        document = self.document
        start_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = document.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_end_date(self):
        document = self.document
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = document.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_end_date(self):
        document = self.document
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = document.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date_end_date(self):
        document = self.document
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = document.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_start_date_end_date(self):
        document = self.document
        start_date = datetime(2009, 5, 1, 0, 0, 0)
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = document.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_start_date_end_date(self):
        document = self.document
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = document.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author_start_date_end_date(self):
        document = self.document
        creator = u"Plato"
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = document.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_bad_start_date_end_date(self):
        document = self.document
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 6, 23, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = document.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)



class TestGetCell(TestCase):

    def setUp(self):
        document = odf_new_document_from_class('text')

        # Encode this table
        #   A B C D E F G
        # 1 1 1 1 2 3 3 3
        # 2 1 1 1 2 3 3 3
        # 3 1 1 1 2 3 3 3
        # 4 1 2 3 4 5 6 7
        table = odf_create_table('a_table', 'Standard')
        column = odf_create_column('Standard')
        column.set_attribute('table:number-columns-repeated', '7')
        document.insert_column(column, table)

        # 3 x "1 1 1 2 3 3 3"
        row = odf_create_row()
        row.set_attribute('table:number-rows-repeated', '3')
        # 3 x "1"
        cell = odf_create_cell()
        cell.set_attribute('table:number-columns-repeated', '3')
        paragraph = odf_create_paragraph('Standard', u'1')
        document.insert_paragraph(paragraph, cell)
        document.insert_cell(cell, row)
        # 1 x "2"
        cell = odf_create_cell()
        paragraph = odf_create_paragraph('Standard', u'2')
        document.insert_paragraph(paragraph, cell)
        document.insert_cell(cell, row)
        # 3 x "3"
        cell = odf_create_cell()
        cell.set_attribute('table:number-columns-repeated', '3')
        paragraph = odf_create_paragraph('Standard', u'3')
        document.insert_paragraph(paragraph, cell)
        document.insert_cell(cell, row)

        document.insert_row(row, table)

        # 1 x "1 2 3 4 5 6 7"
        row = odf_create_row()
        for i in xrange(1, 8):
            cell = odf_create_cell()
            paragraph = odf_create_paragraph('Standard', unicode(i))
            document.insert_paragraph(paragraph, cell)
            document.insert_cell(cell, row)
        document.insert_row(row, table)

        document.insert_table(table)

        self.document = document


    def test_get_cell_coordinates(self):
        x, y = _get_cell_coordinates('ABC123')
        self.assertEqual((x, y), (731, 123))


    def test_get_cell(self):
        document = self.document
        table = document.get_table(name='a_table')

        cell = document.get_cell('D3', table)
        paragraph = document.get_paragraph(1, context=cell)
        self.assertEqual(paragraph.get_text(), '2')

        cell = document.get_cell('F3', table)
        paragraph = document.get_paragraph(1, context=cell)
        self.assertEqual(paragraph.get_text(), '3')

        cell = document.get_cell('D4', table)
        paragraph = document.get_paragraph(1, context=cell)
        self.assertEqual(paragraph.get_text(), '4')


if __name__ == '__main__':
    main()
