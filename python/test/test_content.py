# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import date, datetime, timedelta, time
from decimal import Decimal
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_type, odf_get_document
from lpod.document import odf_create_section
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.document import odf_create_style, odf_create_span
from lpod.document import odf_create_note, odf_create_annotation
from lpod.document import odf_create_variable_decl, odf_create_variable_set
from lpod.document import odf_create_variable_get
from lpod.document import odf_create_user_field_decl
from lpod.document import odf_create_user_field_get
from lpod.document import odf_create_page_number_variable
from lpod.document import odf_create_page_count_variable
from lpod.document import odf_create_date_variable, odf_create_time_variable
from lpod.document import odf_create_chapter_variable
from lpod.document import odf_create_filename_variable
from lpod.document import odf_create_initial_creator_variable
from lpod.document import odf_create_creation_date_variable
from lpod.document import odf_create_creation_time_variable
from lpod.document import odf_create_description_variable
from lpod.document import odf_create_title_variable
from lpod.document import odf_create_keywords_variable
from lpod.document import odf_create_subject_variable
from lpod.document import odf_create_draw_page, odf_create_link
from lpod.document import odf_create_bookmark, odf_create_bookmark_start
from lpod.document import odf_create_bookmark_end
from lpod.document import odf_create_reference_mark
from lpod.document import odf_create_reference_mark_start
from lpod.document import odf_create_reference_mark_end



from lpod.utils import _get_cell_coordinates, convert_unicode
from lpod.xmlpart import LAST_CHILD, NEXT_SIBLING, odf_element



class GetElementTestCase(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/basetext.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_element_missed(self):
        content = self.content
        paragraph = content.get_paragraph_by_position(999)
        self.assertEqual(paragraph, None)


    def test_get_element_list(self):
        content = self.content
        regex = ur'(first|second|a) paragraph'
        paragraphs = content._get_element_list('//text:p', regex=regex)
        self.assertEqual(len(paragraphs), 4)



class TestSection(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/basetext.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_simple_section(self):
        """The idea is to test only with the mandatory arguments (none
        in this case), not to test odf_create_element which is done in
        test_xmlpart.
        """
        element = odf_create_section()
        excepted = '<text:section/>'
        self.assertEqual(element.serialize(), excepted)


    def test_create_complex_section(self):
        """The idea is to test with all possible arguments. If some arguments
        are contradictory or trigger different behaviours, test all those
        combinations separately.
        """
        element = odf_create_section(style='Standard')
        excepted = '<text:section text:style-name="Standard"/>'
        self.assertEqual(element.serialize(), excepted)


    def test_get_section_list(self):
        content = self.content
        sections = content.get_section_list()
        self.assertEqual(len(sections), 2)
        second = sections[1]
        name = second.get_attribute('text:name')
        self.assertEqual(name, "Section2")


    def test_get_section_list_style(self):
        content = self.content
        sections = content.get_section_list(style='Sect1')
        self.assertEqual(len(sections), 2)
        section = sections[0]
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section1")


    def test_get_section(self):
        content = self.content
        section = content.get_section_by_position(2)
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section2")



class TestParagraph(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/basetext.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_paragraph_list(self):
        content = self.content
        paragraphs = content.get_paragraph_list()
        self.assertEqual(len(paragraphs), 6)
        second = paragraphs[1]
        text = second.get_text()
        self.assertEqual(text, 'This is the second paragraph.')


    def test_get_paragraph_list_style(self):
        content = self.content
        paragraphs = content.get_paragraph_list(style='Hanging_20_indent')
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, 'This is a paragraph with a named style.')


    def test_get_paragraph_list_context(self):
        content = self.content
        section2 = content.get_section_by_position(2)
        paragraphs = content.get_paragraph_list(context=section2)
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, "First paragraph of the second section.")


    def test_get_paragraph(self):
        content = self.content
        paragraph = content.get_paragraph_by_position(4)
        text = paragraph.get_text()
        expected = 'This is the first paragraph of the second title.'
        self.assertEqual(text, expected)


    def test_insert_paragraph(self):
        content = self.content
        clone = content.clone()
        paragraph = odf_create_paragraph(u'An inserted test',
                                         style='Text_20_body')
        body = clone.get_body()
        body.insert_element(paragraph, LAST_CHILD)
        last_paragraph = clone.get_paragraph_list()[-1]
        self.assertEqual(last_paragraph.get_text(), u'An inserted test')



class TestSpan(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/span_style.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_span(self):
        span = odf_create_span(u'my text', style='my_style')
        expected = ('<text:span text:style-name="my_style">'
                      'my text'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_get_span_list(self):
        content = self.content
        result = content.get_span_list()
        self.assertEqual(len(result), 2)
        element = result[0]
        expected = ('<text:span text:style-name="T1">'
                      'moustache'
                    '</text:span>')
        self.assertEqual(element.serialize(), expected)


    def test_get_span_list_style(self):
        content = self.content
        result = content.get_span_list(style='T2')
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:span text:style-name="T2">'
                      'rouge'
                    '</text:span>')
        self.assertEqual(element.serialize(), expected)


    def test_get_span(self):
        content = self.content
        span = content.get_span_by_position(2)
        expected = ('<text:span text:style-name="T2">'
                      'rouge'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_insert_span(self):
        span = odf_create_span('my_style', u'my text')
        clone = self.content.clone()
        paragraph = clone.get_paragraph_by_position(1)
        paragraph.insert_element(span, LAST_CHILD)



class TestHeading(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/basetext.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_heading_list(self):
        content = self.content
        headings = content.get_heading_list()
        self.assertEqual(len(headings), 3)
        second = headings[1]
        text = second.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style(self):
        content = self.content
        headings = content.get_heading_list(style='Heading_20_2')
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_level(self):
        content = self.content
        headings = content.get_heading_list(level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style_level(self):
        content = self.content
        headings = content.get_heading_list(style='Heading_20_2', level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_context(self):
        content = self.content
        section2 = content.get_section_by_position(2)
        headings = content.get_heading_list(context=section2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u"First Title of the Second Section");


    def test_get_heading(self):
        content = self.content
        heading = content.get_heading_by_position(2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_level(self):
        content = self.content
        heading = content.get_heading_by_position(1, level=2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_insert_heading(self):
        content = self.content
        clone = content.clone()
        heading = odf_create_heading(2, u'An inserted heading',
                                     style='Heading_20_2')
        body = clone.get_body()
        body.insert_element(heading, LAST_CHILD)
        last_heading = clone.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



class TestFrame(TestCase):

    def setUp(self):
        document = odf_get_document('samples/frame_image.odp').clone()
        self.content = document.get_xmlpart('content')


    def test_create_frame1(self):
        frame1 = odf_create_frame(u"A Frame", size=('10cm', '10cm'),
                                  style='Graphics')
        expected = ('<draw:frame draw:name="A Frame" svg:width="10cm" '
                    'svg:height="10cm" text:anchor-type="paragraph" '
                    'draw:style-name="Graphics"/>')
        self.assertEqual(frame1.serialize(), expected)


    def test_create_frame2(self):
        frame2 = odf_create_frame(u"Another Frame", size=('10cm', '10cm'),
                                  anchor_type='page', page_number=1,
                                  position=('10mm', '10mm'), style='Graphics')
        expected = ('<draw:frame draw:name="Another Frame" svg:width="10cm" '
                      'svg:height="10cm" text:anchor-type="page" '
                      'text:anchor-page-number="1" svg:x="10mm" '
                      'svg:y="10mm" draw:style-name="Graphics"/>')
        self.assertEqual(frame2.serialize(), expected)


    def test_get_frame_list(self):
        content = self.content
        result = content.get_frame_list()
        self.assertEqual(len(result), 2)


    def test_get_frame_list_title(self):
        content = self.content
        result = content.get_frame_list(title=u"Intitulé")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get_name(), 'draw:frame')


    def test_get_frame_by_name(self):
        content = self.content
        frame = content.get_frame_by_name(u"Logo")
        self.assertEqual(frame.get_name(), 'draw:frame')


    def test_get_frame_by_position(self):
        content = self.content
        frame = content.get_frame_by_position(2)
        self.assertEqual(frame.get_attribute('presentation:class'), u'notes')


    def test_get_frame_by_description(self):
        content = self.content
        element = content.get_frame_by_description(u"描述")
        self.assertEqual(element.get_name(), 'draw:frame')


    def test_insert_frame(self):
        clone = self.content.clone()
        frame1 = odf_create_frame(u"frame1", size=('10cm', '10cm'),
                                  style='Graphics')
        frame2 = odf_create_frame(u"frame2", size=('10cm', '10cm'),
                                  page_number=1, position=('10mm', '10mm'),
                                  style='Graphics')
        body = clone.get_body()
        body.append_element(frame1)
        body.append_element(frame2)
        result = clone.get_frame_list(style='Graphics')
        self.assertEqual(len(result), 2)
        element = clone.get_frame_by_name(u"frame1")
        self.assertEqual(element.get_name(), 'draw:frame')
        element = clone.get_frame_by_name(u"frame2")
        self.assertEqual(element.get_name(), 'draw:frame')



class TestImage(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/frame_image.odp')
        self.content = document.get_xmlpart('content')
        self.path = 'Pictures/10000000000001D40000003C8B3889D9.png'


    def tearDown(self):
        del self.content
        del self.document


    def test_create_image(self):
        image = odf_create_image(self.path)
        expected = '<draw:image xlink:href="%s"/>' % self.path
        self.assertEqual(image.serialize(), expected)


    def test_get_image_list(self):
        content = self.content
        result = content.get_image_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        self.assertEqual(element.get_attribute('xlink:href'), self.path)


    def test_get_image_name(self):
        content = self.content
        element = content.get_image_by_name(u"Logo")
        # Searched by frame but got the inner image with no name
        self.assertEqual(element.get_attribute('xlink:href'), self.path)


    def test_get_image_position(self):
        content = self.content
        element = content.get_image_by_position(1)
        self.assertEqual(element.get_attribute('xlink:href'), self.path)


    def test_insert_image(self):
        clone = self.content.clone()
        path = 'a/path'
        image = odf_create_image(path)
        frame = odf_create_frame(u"Image Frame", size=('0cm', '0cm'),
                                 style='Graphics')
        frame.insert_element(image, LAST_CHILD)
        clone.get_frame_by_position(1).insert_element(frame, NEXT_SIBLING)
        element = clone.get_image_by_name(u"Image Frame")
        self.assertEqual(element.get_attribute('xlink:href'), path)
        element = clone.get_image_by_position(2)
        self.assertEqual(element.get_attribute('xlink:href'), path)



class TestTable(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/table.ods')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
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
        table = odf_create_table(u'a_table', style='a_style')
        expected = ('<table:table table:name="a_table" '
                    'table:style-name="a_style"/>')
        self.assertEqual(table.serialize(), expected)

        # Test 2
        table = odf_create_table(u'a_table', width=1, height=2,
                                 style='a_style')
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
        content = self.content
        clone = content.clone()
        table = odf_create_table(u"New Table", style='a_style')
        column = odf_create_column(style='a_column_style')
        row = odf_create_row()
        cell = odf_create_cell(u"")

        table.insert_element(column, LAST_CHILD)
        row.insert_element(cell, LAST_CHILD)
        table.insert_element(row, LAST_CHILD)
        expected = ('<table:table table:name="New Table" '
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

        body = clone.get_body()
        body.insert_element(table, LAST_CHILD)

        # Get OK ?
        table = clone.get_table_by_name(u"New Table")
        self.assertEqual(table.get_attribute('table:name'), u"New Table")

        table = clone.get_table_by_position(4)
        self.assertEqual(table.get_attribute('table:name'), u"New Table")



class TestStyle(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/span_style.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_style(self):
        style = odf_create_style('style1', 'paragraph')
        expected = ('<style:style style:name="style1" '
                      'style:family="paragraph"/>')
        self.assertEqual(style.serialize(), expected)


    def test_get_style_list(self):
        content = self.content
        styles = content.get_style_list()
        self.assertEqual(len(styles), 3)


    def test_get_style_list_family(self):
        content = self.content
        styles = content.get_style_list(family='paragraph')
        self.assertEqual(len(styles), 1)


    def test_get_style_automatic(self):
        content = self.content
        style = content.get_style(u'P1', 'paragraph')
        self.assertNotEqual(style, None)


    def test_insert_style(self):
        content = self.content
        clone = content.clone()
        style = odf_create_style('style1', 'paragraph', area='text',
                **{'fo:color': '#0000ff',
                   'fo:background-color': '#ff0000'})
        auto_styles = clone.get_category_context('automatic')
        auto_styles.insert_element(style, LAST_CHILD)

        expected = ('<style:style style:name="style1" '
                                 'style:family="paragraph">'
                      '<style:text-properties fo:color="#0000ff" '
                                             'fo:background-color="#ff0000"/>'
                    '</style:style>')
        get1 = clone.get_style(u'style1', 'paragraph')
        self.assertEqual(get1.serialize(), expected)



class TestNote(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/note.odt')
        self.content = document.get_xmlpart('content')
        expected = ('<text:note text:note-class="footnote" text:id="note1">'
                      '<text:note-citation>1</text:note-citation>'
                      '<text:note-body>'
                        '<text:p>'
                          'a footnote'
                        '</text:p>'
                      '</text:note-body>'
                    '</text:note>')
        self.expected = expected


    def test_create_note(self):

        # With an odf_element
        note_body = odf_create_paragraph(u'a footnote', style='Standard')
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=note_body)
        expected = self.expected.replace('<text:p>',
                                         '<text:p text:style-name="Standard">')
        self.assertEqual(note.serialize(), expected)

        # With an unicode object
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=u'a footnote')
        self.assertEqual(note.serialize(), self.expected)


    def test_get_note(self):
        content = self.content
        note = content.get_note_by_id('ftn0')
        self.assertEqual(note.get_name(), 'text:note')


    def test_get_note_list(self):
        content = self.content
        notes = content.get_note_list()
        self.assertEqual(len(notes), 2)



    def test_get_note_list_footnote(self):
        content = self.content
        notes = content.get_note_list(note_class='footnote')
        self.assertEqual(len(notes), 1)


    def test_get_note_list_endnote(self):
        content = self.content
        notes = content.get_note_list(note_class='endnote')
        self.assertEqual(len(notes), 1)


    def test_insert_note(self):
        clone = self.content.clone()
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=u'a footnote')
        paragraph = clone.get_paragraph_by_position(1)
        paragraph.insert_element(note, LAST_CHILD)


    def test_get_formeted_text(self):
        document = self.document
        content = self.content
        paragraph = content.get_element('//text:p')
        list_whith_note = odf_create_list()
        list_whith_note.append_item(paragraph)
        body = content.get_body()
        body.append_element(list_whith_note)
        expected = (u"- Un paragraphe[1] d'apparence(i) banale.\n"
                    u"---\n"
                    u"[1] C'est-à-dire l'élément « text:p ».\n\n"
                    u"\n------\n"
                    u"(i) Les apparences sont trompeuses !\n")
        self.assertEqual(document.get_formated_text(), expected)



class TestAnnotation(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/note.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_annotation(self):
        # Create
        annotation = odf_create_annotation(u"Lost Dialogs", creator=u"Plato",
                date=datetime(2009, 6, 22, 17, 18, 42))
        expected = ('<office:annotation>'
                      '<text:p>'
                        'Lost Dialogs'
                      '</text:p>'
                      '<dc:creator>Plato</dc:creator>'
                      '<dc:date>2009-06-22T17:18:42</dc:date>'
                    '</office:annotation>')
        self.assertEqual(annotation.serialize(), expected)


    def test_get_annotation_list(self):
        content = self.content
        annotations = content.get_annotation_list()
        self.assertEqual(len(annotations), 1)
        annotation = annotations[0]
        creator = annotation.get_creator()
        self.assertEqual(creator, u"Auteur inconnu")
        date = annotation.get_date()
        self.assertEqual(date, datetime(2009, 8, 3, 12, 9, 45))
        text = annotation.get_text_content()
        self.assertEqual(text, u"Sauf qu'il est commenté !")


    def test_get_annotation_list_author(self):
        content = self.content
        creator = u"Auteur inconnu"
        annotations = content.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author(self):
        content = self.content
        creator = u"Plato"
        annotations = content.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date(self):
        content = self.content
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date(self):
        content = self.content
        start_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_end_date(self):
        content = self.content
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_end_date(self):
        content = self.content
        end_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = content.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date_end_date(self):
        content = self.content
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date_end_date(self):
        content = self.content
        start_date = datetime(2009, 5, 1, 0, 0, 0)
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_start_date_end_date(self):
        content = self.content
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author_start_date_end_date(self):
        content = self.content
        creator = u"Plato"
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = content.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_bad_start_date_end_date(self):
        content = self.content
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 6, 23, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = content.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_insert_annotation(self):
        content = self.content
        clone = content.clone()
        creator = u"Plato"
        text = u"It's like you're in a cave."
        annotation = odf_create_annotation(text, creator=creator)
        context = clone.get_paragraph_by_position(1)
        context.wrap_text(annotation, offset=27)
        annotations = clone.get_annotation_list()
        self.assertEqual(len(annotations), 2)
        first_annotation = annotations[0]
        self.assertEqual(first_annotation.get_text_content(), text)
        del clone



class TestVariables(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/variable.odt')


    def test_create_variable_decl(self):
        variable_decl = odf_create_variable_decl(u'你好 Zoé', 'float')
        expected = ('<text:variable-decl office:value-type="float" '
                      'text:name="%s"/>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_decl.serialize(), expected)


    def test_create_variable_set_float(self):
        variable_set = odf_create_variable_set(u'你好 Zoé', value=42)
        expected = ('<text:variable-set text:name="%s" '
                      'office:value-type="float" office:value="42" '
                      'text:display="none"/>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_set.serialize(), expected)


    def test_create_variable_set_datetime(self):
        date = datetime(2009, 5, 17, 23, 23, 00)
        variable_set = odf_create_variable_set(u'你好 Zoé', value=date,
                                               display=True)
        expected = ('<text:variable-set text:name="%s" '
                      'office:value-type="date" '
                      'office:date-value="2009-05-17T23:23:00">'
                      '2009-05-17T23:23:00'
                    '</text:variable-set>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_set.serialize(), expected)


    def test_create_variable_get(self):
        variable_get = odf_create_variable_get(u'你好 Zoé', value=42)
        expected = ('<text:variable-get text:name="%s" '
                      'office:value-type="float" office:value="42">'
                      '42'
                    '</text:variable-get>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_get.serialize(), expected)


    def test_get_variable_decl(self):
        clone = self.document.clone()
        content = clone.get_xmlpart('content')
        variable_decl = content.get_variable_decl(u"Variabilité")
        expected = ('<text:variable-decl office:value-type="float" '
                      'text:name="%s"/>' % convert_unicode(u"Variabilité"))
        self.assertEqual(variable_decl.serialize(), expected)


    def test_get_variable_set(self):
        clone = self.document.clone()
        content = clone.get_xmlpart('content')
        variable_sets = content.get_variable_sets(u"Variabilité")
        self.assertEqual(len(variable_sets), 1)
        expected = ('<text:variable-set text:name="%s" '
                      'office:value-type="float" office:value="123" '
                      'style:data-style-name="N1">123</text:variable-set>' %
                        convert_unicode(u"Variabilité"))
        self.assertEqual(variable_sets[0].serialize(), expected)


    def test_get_variable_get(self):
        clone = self.document.clone()
        content = clone.get_xmlpart('content')
        value = content.get_variable_value(u"Variabilité")
        self.assertEqual(value, 123)



class TestUserFields(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/variable.odt')


    def test_create_user_field(self):

        # decl
        # ----

        user_field_decl = odf_create_user_field_decl(u'你好 Zoé', 42)
        expected = (('<text:user-field-decl text:name="%s" '
                       'office:value-type="float" office:value="42"/>') %
                      convert_unicode(u'你好 Zoé'))
        self.assertEqual(user_field_decl.serialize(), expected)


        # get
        # ---

        user_field_get = odf_create_user_field_get(u'你好 Zoé', value=42)
        expected = ('<text:user-field-get text:name="%s" '
                      'office:value-type="float" office:value="42">'
                      '42'
                    '</text:user-field-get>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(user_field_get.serialize(), expected)


    def test_get_user_field(self):
        clone = self.document.clone()
        content = clone.get_xmlpart('content')

        # decl
        # ----

        decls = content.get_user_field_decls()
        user_field_decl = odf_create_user_field_decl(u'你好 Zoé', 42)
        decls.insert_element(user_field_decl, LAST_CHILD)

        user_field_decl = content.get_user_field_decl(u'你好 Zoé')
        expected = (('<text:user-field-decl text:name="%s" '
                       'office:value-type="float" office:value="42"/>') %
                      convert_unicode(u'你好 Zoé'))
        self.assertEqual(user_field_decl.serialize(), expected)

        # get value
        # ---------

        value = content.get_user_field_value(u'你好 Zoé')
        self.assertEqual(value, 42)



class TestLinks(TestCase):

    def setUp(self):
        document = odf_get_document('samples/basetext.odt')
        clone = document.clone()

        self.content = clone.get_xmlpart('content')
        self.paragraph = self.content.get_paragraph_by_position(1)


    def test_create_link1(self):
        link = odf_create_link('http://example.com/')
        expected = '<text:a xlink:href="http://example.com/"/>'
        self.assertEqual(link.serialize(), expected)


    def test_create_link2(self):
        link = odf_create_link('http://example.com/', name=u'link2',
                               target_frame='_blank', style='style1',
                               visited_style='style2')
        expected = ('<text:a xlink:href="http://example.com/" '
                      'office:name="link2" office:target-frame-name="_blank" '
                      'xlink:show="new" text:style-name="style1" '
                      'text:visited-style-name="style2"/>')
        self.assertEqual(link.serialize(), expected)


    def test_get_link(self):
        link1 = odf_create_link('http://example.com/', name='link1')
        link2 = odf_create_link('http://example.com/', name='link2')

        paragraph = self.paragraph
        paragraph.append_element(link1)
        paragraph.append_element(link2)

        element = self.content.get_link_by_name(u'link2')
        expected = ('<text:a xlink:href="http://example.com/" '
                      'office:name="link2"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list(self):
        link1 = odf_create_link('http://example.com/', name='link1')
        link2 = odf_create_link('http://example.com/', name='link2')

        paragraph = self.paragraph
        paragraph.append_element(link1)
        paragraph.append_element(link2)

        element = self.content.get_link_list()[1]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link2"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_name(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')

        paragraph = self.paragraph
        paragraph.append_element(link1)
        paragraph.append_element(link2)

        # name
        element = self.content.get_link_list(name='link1')[0]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link1" office:title="title1"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_title(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')

        paragraph = self.paragraph
        paragraph.append_element(link1)
        paragraph.append_element(link2)

        # title
        element = self.content.get_link_list(title='title2')[0]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link2" office:title="title2"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_name_and_title(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')

        paragraph = self.paragraph
        paragraph.append_element(link1)
        paragraph.append_element(link2)

        # name and title
        element = self.content.get_link_list(name='link1', title='title1')[0]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link1" office:title="title1"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_not_found(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')

        paragraph = self.paragraph
        paragraph.append_element(link1)
        paragraph.append_element(link2)

        # Not found
        element = self.content.get_link_list(name='link1', title='title2')
        self.assertEqual(element, [])



class TestPageNumber(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/variable.odt')


    def test_create_page_number(self):

        # Simple
        page_number = odf_create_page_number_variable()
        expected = '<text:page-number text:select-page="current"/>'
        self.assertEqual(page_number.serialize(), expected)

        # With arguments
        page_number = odf_create_page_number_variable(select_page='next',
                                                      page_adjust=1)
        expected = ('<text:page-number text:select-page="next" '
                    'text:page-adjust="1"/>')
        self.assertEqual(page_number.serialize(), expected)



class TestPageCount(TestCase):

    def test_create_page_number(self):

        page_count = odf_create_page_count_variable()
        expected = '<text:page-count/>'
        self.assertEqual(page_count.serialize(), expected)



class TestDate(TestCase):

    def test_create_date(self):

        # Simple
        date_elt = odf_create_date_variable(datetime(2009, 7, 20))
        expected = ('<text:date text:date-value="2009-07-20T00:00:00">'
                      '2009-07-20'
                    '</text:date>')
        self.assertEqual(date_elt.serialize(), expected)

        # Fixed
        date_elt = odf_create_date_variable(datetime(2009, 7, 20),
                                            fixed=True)
        expected = ('<text:date text:date-value="2009-07-20T00:00:00" '
                      'text:fixed="true">'
                      '2009-07-20'
                    '</text:date>')
        self.assertEqual(date_elt.serialize(), expected)

        # Change the representation
        date_elt =  odf_create_date_variable(datetime(2009, 7, 20),
                                             representation=u'20 juil. 09')
        expected = ('<text:date text:date-value="2009-07-20T00:00:00">'
                      '20 juil. 09'
                    '</text:date>')
        self.assertEqual(date_elt.serialize(), expected)



class TestTime(TestCase):

    def test_create_time(self):

        # Simple
        time_elt = odf_create_time_variable(time(19,30))
        expected = ('<text:time text:time-value="1900-01-01T19:30:00">'
                      '19:30:00'
                    '</text:time>')
        self.assertEqual(time_elt.serialize(), expected)

        # Fixed
        time_elt = odf_create_time_variable(time(19, 30), fixed=True)
        expected = ('<text:time text:time-value="1900-01-01T19:30:00" '
                      'text:fixed="true">'
                      '19:30:00'
                    '</text:time>')
        self.assertEqual(time_elt.serialize(), expected)

        # Change the representation
        time_elt =  odf_create_time_variable(time(19, 30),
                                    representation=u'19h30')
        expected = ('<text:time text:time-value="1900-01-01T19:30:00">'
                      '19h30'
                    '</text:time>')
        self.assertEqual(time_elt.serialize(), expected)



class TestChapter(TestCase):

    def test_create_chapter(self):

        # Simple
        chapter = odf_create_chapter_variable()
        expected = '<text:chapter text:display="name"/>'
        self.assertEqual(chapter.serialize(), expected)

        # Complex
        chapter = odf_create_chapter_variable(display='number-and-name',
                                              outline_level=1)
        expected = ('<text:chapter text:display="number-and-name" '
                      'text:outline-level="1"/>')
        self.assertEqual(chapter.serialize(), expected)



class TestFilename(TestCase):

    def test_create_filename(self):

        # Simple
        filename = odf_create_filename_variable()
        expected = '<text:file-name text:display="full"/>'
        self.assertEqual(filename.serialize(), expected)

        # Fixed
        filename = odf_create_filename_variable(fixed=True)
        expected = '<text:file-name text:display="full" text:fixed="true"/>'
        self.assertEqual(filename.serialize(), expected)



class TestSomeMetaInformations(TestCase):

    def test_create_elements(self):

        elt = odf_create_initial_creator_variable()
        expected = '<text:initial-creator/>'
        self.assertEqual(elt.serialize(), expected)

        elt = odf_create_creation_date_variable()
        expected = '<text:creation-date/>'
        self.assertEqual(elt.serialize(), expected)

        elt = odf_create_creation_time_variable()
        expected = '<text:creation-time/>'
        self.assertEqual(elt.serialize(), expected)

        elt = odf_create_description_variable()
        expected = '<text:description/>'
        self.assertEqual(elt.serialize(), expected)

        elt = odf_create_title_variable()
        expected = '<text:title/>'
        self.assertEqual(elt.serialize(), expected)

        elt = odf_create_subject_variable()
        expected = '<text:subject/>'
        self.assertEqual(elt.serialize(), expected)

        elt = odf_create_keywords_variable()
        expected = '<text:keywords/>'
        self.assertEqual(elt.serialize(), expected)



class TestGetCell(TestCase):

    def setUp(self):
        self.document = document = odf_new_document_from_type('text')
        self.content = content = document.get_xmlpart('content')

        # Encode this table
        #   A B C D E F G
        # 1 1 1 1 2 3 3 3
        # 2 1 1 1 2 3 3 3
        # 3 1 1 1 2 3 3 3
        # 4 1 2 3 4 5 6 7
        table = odf_create_table(u'a_table', style='Standard')
        column = odf_create_column('Standard')
        column.set_attribute('table:number-columns-repeated', '7')
        table.insert_element(column, LAST_CHILD)

        # 3 x "1 1 1 2 3 3 3"
        row = odf_create_row()
        row.set_attribute('table:number-rows-repeated', '3')
        # 3 x "1"
        cell = odf_create_cell(u'1')
        cell.set_attribute('table:number-columns-repeated', '3')
        row.insert_element(cell, LAST_CHILD)
        # 1 x "2"
        cell = odf_create_cell(u'2')
        row.insert_element(cell, LAST_CHILD)
        # 3 x "3"
        cell = odf_create_cell(u'3')
        cell.set_attribute('table:number-columns-repeated', '3')
        row.insert_element(cell, LAST_CHILD)

        table.insert_element(row, LAST_CHILD)

        # 1 x "1 2 3 4 5 6 7"
        row = odf_create_row()
        for i in xrange(1, 8):
            cell = odf_create_cell(unicode(i))
            row.insert_element(cell, LAST_CHILD)
        table.insert_element(row, LAST_CHILD)

        body = content.get_body()
        body.insert_element(table, LAST_CHILD)


    def tearDown(self):
        del self.content
        del self.document


    def test_get_cell_coordinates(self):
        x, y = _get_cell_coordinates('ABC123')
        self.assertEqual((x, y), (731, 123))



class TestDrawPage(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odp')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_simple_page(self):
        element = odf_create_draw_page(u"Page de titre")
        expected = '<draw:page draw:name="Page de titre"/>'
        self.assertEqual(element.serialize(), expected)


    def test_create_complex_page(self):
        element = odf_create_draw_page(u"Introduction", page_id='id1',
                                       master_page='prs-novelty',
                                       page_layout='AL1T0', style='dp1')
        expected = ('<draw:page draw:name="Introduction" '
                    'draw:style-name="dp1" '
                    'draw:master-page-name="prs-novelty" '
                    'presentation:presentation-page-layout-name="AL1T0" '
                    'draw:id="id1"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_draw_page_list(self):
        content = self.content
        result = content.get_draw_page_list()
        self.assertEqual(len(result), 2)


    def test_get_draw_page_list_style(self):
        content = self.content.clone()
        result = content.get_draw_page_list(style='dp1')
        self.assertEqual(len(result), 2)
        result = content.get_draw_page_list(style='dp2')
        self.assertEqual(len(result), 0)


    def test_get_draw_page(self):
        content = self.content.clone()
        result = content.get_draw_page_by_name(u"Titre")
        self.assert_(isinstance(result, odf_element))
        result = content.get_draw_page_by_name(u"Conclusion")
        self.assertEqual(result, None)



class BookmarkTest(TestCase):

    def setUp(self):
        clone = odf_get_document('samples/bookmark.odt').clone()
        self.content = clone.get_xmlpart('content')
        self.body = clone.get_body()

    def test_create_bookmark(self):
        bookmark = odf_create_bookmark(u'你好 Zoé')
        expected = ('<text:bookmark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(bookmark.serialize(), expected)


    def test_create_bookmark_start(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(bookmark_start.serialize(), expected)


    def test_create_bookmark_end(self):
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(bookmark_end.serialize(), expected)


    def test_get_bookmark(self):
        bookmark = odf_create_bookmark(u'你好 Zoé')
        self.body.append_element(bookmark)

        get = self.content.get_bookmark_by_name(u'你好 Zoé')
        expected = ('<text:bookmark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_list(self):
        content = self.content
        result = self.content.get_bookmark_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = '<text:bookmark text:name="Rep&#232;re de texte"/>'
        self.assertEqual(element.serialize(), expected)


    def test_get_bookmark_start(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        self.body.append_element(bookmark_start)

        get = self.content.get_bookmark_start_by_name(u'你好 Zoé')
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_start_list(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        self.body.append_element(bookmark_start)

        get = self.content.get_bookmark_start_list()[0]
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_end(self):
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        self.body.append_element(bookmark_end)

        get = self.content.get_bookmark_end_by_name(u'你好 Zoé')
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_end_list(self):
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        self.body.append_element(bookmark_end)

        get = self.content.get_bookmark_end_list()[0]
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)



class reference_markTest(TestCase):

    def setUp(self):
        clone = odf_get_document('samples/bookmark.odt').clone()
        self.content = clone.get_xmlpart('content')
        self.body = clone.get_body()

    def test_create_reference_mark(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark.serialize(), expected)


    def test_create_reference_mark_start(self):
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark_start.serialize(), expected)


    def test_create_reference_mark_end(self):
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark_end.serialize(), expected)


    def test_get_reference_mark(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        self.body.append_element(reference_mark)

        get = self.content.get_reference_mark_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_list(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        self.body.append_element(reference_mark)

        get = self.content.get_reference_mark_list()[0]
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start(self):
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        self.body.append_element(reference_mark_start)

        get = self.content.get_reference_mark_start_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start_list(self):
        content = self.content
        result = content.get_reference_mark_start_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-start '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_reference_mark_end(self):
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        self.body.append_element(reference_mark_end)

        get = self.content.get_reference_mark_end_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_end_list(self):
        content = self.content
        result = content.get_reference_mark_end_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-end '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)



if __name__ == '__main__':
    main()
