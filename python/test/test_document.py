# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_template
from lpod.document import odf_new_document_from_class, odf_get_document
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.document import odf_create_list_item, odf_create_list
from lpod.document import odf_create_style, odf_create_style_text_properties
from lpod.document import odf_create_note, odf_create_annotation
from lpod.utils import _get_cell_coordinates, DateTime, Duration


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



class TestSection(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


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



class TestParagraph(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_get_paragraph_list(self):
        document = self.document
        paragraphs = document.get_paragraph_list()
        # The annotation paragraph is counted
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
        clone.insert_element(paragraph)
        last_paragraph = clone.get_paragraph_list()[-1]
        self.assertEqual(last_paragraph.get_text(), u'An inserted test')



class TestHeading(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


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
        clone.insert_element(heading)
        last_heading = clone.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



class TestFrame(TestCase):

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
        document.insert_element(frame1)
        document.insert_element(frame2)

        # Get OK ?
        get = document.get_frame(name='frame1')
        self.assertEqual(get.get_attribute('draw:name'), 'frame1')

        get = document.get_frame(position=2)
        self.assertEqual(get.get_attribute('draw:name'), 'frame2')



class TestImage(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_image(self):
        document = self.document

        # Test create
        image = odf_create_image('path')
        expected = '<draw:image xlink:href="path"/>'
        self.assertEqual(image.serialize(), expected)

        # Insert OK ?
        frame = odf_create_frame('frame_image', 'Graphics', '0cm', '0cm')
        document.insert_element(image, frame)
        document.insert_element(frame)

        # Get OK ?
        get = document.get_image(name='frame_image')
        self.assertEqual(get.get_attribute('xlink:href'), 'path')

        get = document.get_image(position=1)
        self.assertEqual(get.get_attribute('xlink:href'), 'path')



class TestTable(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document



    def test_create_cell_bool(self):
        cell = odf_create_cell(True)
        expected = ('<table:table-cell office:value-type="boolean" '
                      'office:boolean-value="true">'
                      '<text:p>true</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_bool_repr(self):
        cell = odf_create_cell(True, representation=u"VRAI")
        expected = ('<table:table-cell office:value-type="boolean" '
                      'office:boolean-value="true">'
                      '<text:p>VRAI</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_int(self):
        cell = odf_create_cell(23)
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="23">'
                      '<text:p>23</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_int_repr(self):
        cell = odf_create_cell(23, representation=u"00023")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="23">'
                      '<text:p>00023</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_float(self):
        cell = odf_create_cell(3.141592654)
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="3.141592654">'
                      '<text:p>3.141592654</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_float_repr(self):
        cell = odf_create_cell(3.141592654, representation=u"3,14")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="3.141592654">'
                      '<text:p>3,14</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_decimal(self):
        cell = odf_create_cell(Decimal('2.718281828'))
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="2.718281828">'
                      '<text:p>2.718281828</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_decimal_repr(self):
        cell = odf_create_cell(Decimal('2.718281828'),
                               representation=u"2,72")
        expected = ('<table:table-cell office:value-type="float" '
                      'office:value="2.718281828">'
                      '<text:p>2,72</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_date(self):
        cell = odf_create_cell(date(2009, 6, 30))
        expected = ('<table:table-cell office:value-type="date" '
                      'office:date-value="2009-06-30">'
                      '<text:p>2009-06-30</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_date_repr(self):
        cell = odf_create_cell(date(2009, 6, 30),
                               representation=u"30/6/2009")
        expected = ('<table:table-cell office:value-type="date" '
                      'office:date-value="2009-06-30">'
                      '<text:p>30/6/2009</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_datetime(self):
        cell = odf_create_cell(datetime(2009, 6, 30, 17, 33, 18))
        expected = ('<table:table-cell office:value-type="date" '
                'office:date-value="2009-06-30T17:33:18">'
                      '<text:p>2009-06-30T17:33:18</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_datetime_repr(self):
        cell = odf_create_cell(datetime(2009, 6, 30, 17, 33, 18),
                               representation=u"30/6/2009 17:33")
        expected = ('<table:table-cell office:value-type="date" '
                'office:date-value="2009-06-30T17:33:18">'
                      '<text:p>30/6/2009 17:33</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_str(self):
        cell = odf_create_cell('red')
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="red">'
                      '<text:p>red</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_str_repr(self):
        cell = odf_create_cell('red', representation=u"Red")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="red">'
                      '<text:p>Red</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_unicode(self):
        cell = odf_create_cell(u"Plato")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="Plato">'
                      '<text:p>Plato</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_unicode_repr(self):
        cell = odf_create_cell(u"Plato", representation=u"P.")
        expected = ('<table:table-cell office:value-type="string" '
                      'office:string-value="Plato">'
                      '<text:p>P.</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_timedelta(self):
        cell = odf_create_cell(timedelta(0, 8))
        expected = ('<table:table-cell office:value-type="time" '
                      'office:time-value="PT00H00M08S">'
                      '<text:p>PT00H00M08S</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_timedelta_repr(self):
        cell = odf_create_cell(timedelta(0, 8), representation=u"00:00:08")
        expected = ('<table:table-cell office:value-type="time" '
                      'office:time-value="PT00H00M08S">'
                      '<text:p>00:00:08</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_percentage(self):
        cell = odf_create_cell(90, cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>90</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_percentage_repr(self):
        cell = odf_create_cell(90, representation=u"90 %",
                               cell_type='percentage')
        expected = ('<table:table-cell office:value-type="percentage" '
                      'office:value="90">'
                      '<text:p>90 %</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_currency(self):
        cell = odf_create_cell(1.54, cell_type='currency', currency='EUR')
        expected = ('<table:table-cell office:value-type="currency" '
                      'office:value="1.54" office:currency="EUR">'
                      '<text:p>1.54</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_currency_repr(self):
        cell = odf_create_cell(1.54, representation=u"1,54 €",
                               cell_type='currency', currency='EUR')
        expected = ('<table:table-cell office:value-type="currency" '
                      'office:value="1.54" office:currency="EUR">'
                      '<text:p>1,54 &#8364;</text:p>'
                    '</table:table-cell>')
        self.assertEqual(cell.serialize(), expected)


    def test_create_cell_bad(self):
        self.assertRaises(TypeError, odf_create_cell, [])


    def test_create_cell_bad_repr(self):
        self.assertRaises(TypeError, odf_create_cell, '',
                          representation="This ain't unicode")


    def test_create_row(self):
        # Test 1
        row = odf_create_row()
        expected = '<table:table-row/>'
        self.assertEqual(row.serialize(), expected)

        # Test 2
        row = odf_create_row(1)
        expected = ('<table:table-row>'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
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
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>'
                    '<table:table-row>'
                      '<table:table-cell office:value-type="string" '
                        'office:string-value="">'
                        '<text:p></text:p>'
                      '</table:table-cell>'
                    '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)


    def test_insert_table(self):
        document = self.document
        clone = document.clone()
        table = odf_create_table('a_table', 'a_style')
        column = odf_create_column('a_column_style')
        row = odf_create_row()
        cell = odf_create_cell(u"")

        clone.insert_element(cell, row)
        clone.insert_element(column, table)
        clone.insert_element(row, table)
        clone.insert_element(table)

        expected = ('<table:table table:name="a_table" '
                      'table:style-name="a_style">'
                      '<table:table-column '
                        'table:style-name="a_column_style"/>'
                      '<table:table-row>'
                        '<table:table-cell office:value-type="string" '
                          'office:string-value="">'
                          '<text:p></text:p>'
                        '</table:table-cell>'
                      '</table:table-row>'
                    '</table:table>')
        self.assertEqual(table.serialize(), expected)

        # Get OK ?
        get = clone.get_table(name='a_table')
        self.assertEqual(get.get_attribute('table:name'), 'a_table')

        get = clone.get_table(position=1)
        self.assertEqual(get.get_attribute('table:name'), 'a_table')



class TestList(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_item(self):
        item = odf_create_list_item()
        expected = '<text:list-item/>'
        self.assertEqual(item.serialize(), expected)


    def test_create_list(self):
        item = odf_create_list_item()
        a_list = odf_create_list('a_style')
        expected = '<text:list text:style-name="a_style"/>'
        self.assertEqual(a_list.serialize(), expected)


    def test_insert_list(self):
        document = self.document
        clone = document.clone()
        item = odf_create_list_item()
        a_list = odf_create_list('a_style')
        clone.insert_element(item, a_list)
        clone.insert_element(a_list)

        expected = ('<text:list text:style-name="a_style">'
                    '<text:list-item/>'
                    '</text:list>')
        self.assertEqual(a_list.serialize(), expected)



class TestStyle(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_style(self):
        style = odf_create_style('style1', 'paragraph')
        expected = ('<style:style style:name="style1" '
                      'style:family="paragraph"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_properties(self):
        properties = odf_create_style_text_properties()
        properties.set_attribute('fo:color', '#0000ff')
        properties.set_attribute('fo:background-color', '#ff0000')
        expected = ('<style:text-properties fo:color="#0000ff" '
                      'fo:background-color="#ff0000"/>')
        self.assertEqual(properties.serialize(), expected)


    def test_get_style_list(self):
        document = self.document
        styles = document.get_style_list()
        self.assertEqual(len(styles), 12)


    def test_get_style_list_family(self):
        document = self.document
        styles = document.get_style_list(family='paragraph')
        self.assertEqual(len(styles), 10)


    def test_get_style_automatic(self):
        document = self.document
        style = document.get_style('P1', 'paragraph')
        self.assertNotEqual(style, None)


    def test_get_style_named(self):
        document = self.document
        style = document.get_style('Heading_20_1', 'paragraph')
        self.assertNotEqual(style, None)


    def test_insert_style(self):
        document = self.document
        clone = document.clone()
        style = odf_create_style('style1', 'paragraph')
        properties = odf_create_style_text_properties()
        properties.set_attribute('fo:color', '#0000ff')
        properties.set_attribute('fo:background-color', '#ff0000')
        clone.insert_element(properties, style)
        clone.insert_element(style)

        expected = ('<style:style style:name="style1" '
                                 'style:family="paragraph">'
                      '<style:text-properties fo:color="#0000ff" '
                                             'fo:background-color="#ff0000"/>'
                    '</style:style>')
        get1 = clone.get_style('style1', 'paragraph')
        self.assertEqual(get1.serialize(), expected)



class TestNote(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_create_note(self):
        document = self.document

        # Create OK ?
        note = odf_create_note(u'1', id='note1')
        body = odf_create_paragraph('Standard', u'a footnote')
        # TODO stop here and compare to the snippet

        # Insert OK ?
        clone = document.clone()
        paragraph = clone.get_paragraph(1)
        document.insert_note_body(body, note)
        document.insert_element(note, paragraph)

        # Get OK ?
        expected = ('<text:note text:note-class="footnote" text:id="note1">'
                      '<text:note-citation>1</text:note-citation>'
                      '<text:note-body>'
                        '<text:p text:style-name="Standard">'
                          'a footnote'
                        '</text:p>'
                      '</text:note-body>'
                    '</text:note>'
                    'This is the first paragraph.')
        get1 = clone.get_note('note1')
        get2 = clone.get_note_list(note_class='footnote')[-1]
        self.assertEqual(get1.serialize(), expected)
        self.assertEqual(get2.serialize(), expected)


    def test_get_note(self):
        raise NotImplementedError


    def test_get_note_list(self):
        raise NotImplementedError


    def test_insert_note(self):
        document = self.document
        clone = document.clone()
        raise NotImplementedError



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


    def test_get_annotation_list_bad_start_date_end_date(self):
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


    def test_insert_annotation(self):
        document = self.document
        clone = document.clone()
        creator = u"Plato"
        text = u"It's like you're in a cave."
        annotation = odf_create_annotation(creator, text)
        context = clone.get_paragraph(1)
        clone.insert_element(annotation, context, offset=27)
        annotations = clone.get_annotation_list()
        self.assertEqual(len(annotations), 2)
        first_annotation = annotations[0]
        self.assertEqual(first_annotation.get_text_content(), text)
        del clone



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
        document.insert_element(column, table)

        # 3 x "1 1 1 2 3 3 3"
        row = odf_create_row()
        row.set_attribute('table:number-rows-repeated', '3')
        # 3 x "1"
        cell = odf_create_cell(u'1')
        cell.set_attribute('table:number-columns-repeated', '3')
        document.insert_element(cell, row)
        # 1 x "2"
        cell = odf_create_cell(u'2')
        document.insert_element(cell, row)
        # 3 x "3"
        cell = odf_create_cell(u'3')
        cell.set_attribute('table:number-columns-repeated', '3')
        document.insert_element(cell, row)

        document.insert_element(row, table)

        # 1 x "1 2 3 4 5 6 7"
        row = odf_create_row()
        for i in xrange(1, 8):
            cell = odf_create_cell(unicode(i))
            document.insert_element(cell, row)
        document.insert_element(row, table)

        document.insert_element(table)

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



class TestMetadata(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def tearDown(self):
        del self.document


    def test_get_title(self):
        document = self.document
        title = document.get_title()
        expected = u"This is the title"
        self.assertEqual(title, expected)


    def test_set_title(self):
        document = self.document
        clone = document.clone()
        title = u"A new title"
        clone.set_title(title)
        self.assertEqual(clone.get_title(), title)


    def test_set_bad_title(self):
        document = self.document
        clone = document.clone()
        title = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_title, title)


    def test_get_description(self):
        document = self.document
        description = document.get_description()
        expected = u"This is the description"
        self.assertEqual(description, expected)


    def test_set_description(self):
        document = self.document
        clone = document.clone()
        description = u"A new description"
        clone.set_description(description)
        self.assertEqual(clone.get_description(), description)


    def test_set_bad_description(self):
        document = self.document
        clone = document.clone()
        description = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_description, description)


    def test_get_subject(self):
        document = self.document
        subject = document.get_subject()
        expected = u"This is the subject"
        self.assertEqual(subject, expected)


    def test_set_subject(self):
        document = self.document
        clone = document.clone()
        subject = u"A new subject"
        clone.set_subject(subject)
        self.assertEqual(clone.get_subject(), subject)


    def test_set_bad_subject(self):
        document = self.document
        clone = document.clone()
        subject = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_subject, subject)


    def test_get_language(self):
        document = self.document
        language = document.get_language()
        expected = 'fr-FR'
        self.assertEqual(language, expected)


    def test_set_language(self):
        document = self.document
        clone = document.clone()
        language = 'en-US'
        clone.set_language(language)
        self.assertEqual(clone.get_language(), language)


    def test_set_bad_language(self):
        document = self.document
        clone = document.clone()
        language = u"English"
        self.assertRaises(TypeError, clone.set_language, language)


    def test_get_modification_date(self):
        document = self.document
        date = document.get_modification_date()
        expected = DateTime.decode('2009-06-29T14:33:21')
        self.assertEqual(date, expected)


    def test_set_modification_date(self):
        document = self.document
        clone = document.clone()
        now = datetime.now().replace(microsecond=0)
        clone.set_modification_date(now)
        self.assertEqual(clone.get_modification_date(), now)


    def test_set_bad_modication_date(self):
        document = self.document
        clone = document.clone()
        date = '2009-06-29T14:15:45'
        self.assertRaises(TypeError, clone.set_modification_date, date)


    def test_get_creation_date(self):
        document = self.document
        date = document.get_creation_date()
        expected = datetime(2009, 2, 18, 20, 5, 10)
        self.assertEqual(date, expected)


    def test_set_creation_date(self):
        document = self.document
        clone = document.clone()
        now = datetime.now().replace(microsecond=0)
        clone.set_creation_date(now)
        self.assertEqual(clone.get_creation_date(), now)


    def test_set_bad_creation_date(self):
        document = self.document
        clone = document.clone()
        date = '2009-06-29T14:15:45'
        self.assertRaises(TypeError, clone.set_creation_date, date)


    def test_get_initial_creator(self):
        document = self.document
        creator = document.get_initial_creator()
        expected = None
        self.assertEqual(creator, expected)


    def test_set_initial_creator(self):
        document = self.document
        clone = document.clone()
        creator = u"Socrates"
        clone.set_initial_creator(creator)
        self.assertEqual(clone.get_initial_creator(), creator)


    def test_set_bad_initial_creator(self):
        document = self.document
        clone = document.clone()
        creator = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_initial_creator, creator)


    def test_get_keyword(self):
        document = self.document
        keyword = document.get_keyword()
        expected = u"These are the keywords"
        self.assertEqual(keyword, expected)


    def test_set_keyword(self):
        document = self.document
        clone = document.clone()
        keyword = u"New keywords"
        clone.set_keyword(keyword)
        self.assertEqual(clone.get_keyword(), keyword)


    def test_set_bad_keyword(self):
        document = self.document
        clone = document.clone()
        keyword = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_keyword, keyword)


    def test_get_editing_duration(self):
        document = self.document
        duration = document.get_editing_duration()
        expected = Duration.decode('PT00H06M53S')
        self.assertEqual(duration, expected)


    def test_set_editing_duration(self):
        document = self.document
        clone = document.clone()
        duration = timedelta(1, 2, 0, 0, 5, 6, 7)
        clone.set_editing_duration(duration)
        self.assertEqual(clone.get_editing_duration(), duration)


    def test_set_bad_editing_duration(self):
        document = self.document
        clone = document.clone()
        duration = 'PT00H01M27S'
        self.assertRaises(TypeError, clone.set_editing_duration, duration)


    def test_get_editing_cycles(self):
        document = self.document
        cycles = document.get_editing_cycles()
        expected = 8
        self.assertEqual(cycles, expected)


    def test_set_editing_cycles(self):
        document = self.document
        clone = document.clone()
        cycles = 1 # I swear it was a first shot!
        clone.set_editing_cycles(cycles)
        self.assertEqual(clone.get_editing_cycles(), cycles)


    def test_set_bad_editing_cycles(self):
        document = self.document
        clone = document.clone()
        cycles = '3'
        self.assertRaises(TypeError, clone.set_editing_duration, cycles)


    def test_get_generator(self):
        document = self.document
        generator = document.get_generator()
        expected = (u"OpenOffice.org/3.1$Unix "
                    u"OpenOffice.org_project/310m11$Build-9399")
        self.assertEqual(generator, expected)


    def test_set_generator(self):
        document = self.document
        clone = document.clone()
        generator = u"lpOD Project"
        clone.set_generator(generator)
        self.assertEqual(clone.get_generator(), generator)


    def test_set_bad_generator(self):
        document = self.document
        clone = document.clone()
        generator = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_generator, generator)


    def test_get_statistic(self):
        document = self.document
        statistic = document.get_statistic()
        expected = {'meta:table-count': 0,
                    'meta:image-count': 0,
                    'meta:object-count': 0,
                    'meta:page-count': 1,
                    'meta:paragraph-count': 9,
                    'meta:word-count': 51,
                    'meta:character-count': 279}
        self.assertEqual(statistic, expected)


    def test_set_statistic(self):
        document = self.document
        clone = document.clone()
        statistic = {'meta:table-count': 1,
                     'meta:image-count': 2,
                     'meta:object-count': 3,
                     'meta:page-count': 4,
                     'meta:paragraph-count': 5,
                     'meta:word-count': 6,
                     'meta:character-count': 7}
        clone.set_statistic(statistic)
        self.assertEqual(clone.get_statistic(), statistic)


    def test_set_bad_statistic(self):
        document = self.document
        clone = document.clone()
        generator = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_generator, generator)



if __name__ == '__main__':
    main()
