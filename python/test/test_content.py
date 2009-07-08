# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_new_document_from_class, odf_get_document
from lpod.document import odf_create_paragraph, odf_create_heading
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_cell, odf_create_row
from lpod.document import odf_create_column, odf_create_table
from lpod.document import odf_create_list_item, odf_create_list
from lpod.document import odf_create_style, odf_create_style_text_properties
from lpod.document import odf_create_note, odf_create_annotation
from lpod.document import odf_create_span
from lpod.utils import _get_cell_coordinates


class GetElementTestCase(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_element_list_bad_context(self):
        content = self.content
        self.assertRaises(TypeError, content.get_paragraph_list,
                          context=content)


    def test_get_element_missed(self):
        content = self.content
        paragraph = content.get_paragraph(999)
        self.assertEqual(paragraph, None)



class TestSection(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


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
        section = content.get_section(2)
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section2")



class TestParagraph(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_paragraph_list(self):
        content = self.content
        paragraphs = content.get_paragraph_list()
        # The annotation paragraph is counted
        self.assertEqual(len(paragraphs), 7)
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
        section2 = content.get_section(2)
        paragraphs = content.get_paragraph_list(context=section2)
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, "First paragraph of the second section.")


    def test_get_paragraph(self):
        content = self.content
        paragraph = content.get_paragraph(4)
        text = paragraph.get_text()
        expected = 'This is the first paragraph of the second title.'
        self.assertEqual(text, expected)


    def test_insert_paragraph(self):
        content = self.content
        clone = content.clone()
        paragraph = odf_create_paragraph('Text_20_body',
                                         u'An inserted test')
        clone.insert_element(paragraph, clone.get_body())
        last_paragraph = clone.get_paragraph_list()[-1]
        self.assertEqual(last_paragraph.get_text(), u'An inserted test')



class TestSpan(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_span(self):

        # Create OK ?
        span = odf_create_span('my_style', u'my text')
        expected = ('<text:span text:style-name="my_style">'
                      'my text'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_insert_span(self):

        span = odf_create_span('my_style', u'my text')

        # Insert OK?
        clone = self.content.clone()
        paragraph = clone.get_paragraph(1)
        clone.insert_element(span, paragraph)


    def test_get_span(self):

        span = odf_create_span('my_style', u'my text')
        clone = self.content.clone()
        paragraph = clone.get_paragraph(1)
        clone.insert_element(span, paragraph)

        # Get OK ?
        span1 = clone.get_span(1)
        span2 = clone.get_span_list()[0]

        # We have the text with the tag, so, ...
        expected = ('<text:span text:style-name="my_style">'
                      'my text'
                    '</text:span>'
                    'This is the first paragraph.')

        self.assertEqual(span1.serialize(), expected)
        self.assertEqual(span2.serialize(), expected)



class TestHeading(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
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
        section2 = content.get_section(2)
        headings = content.get_heading_list(context=section2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u"First Title of the Second Section");


    def test_get_heading(self):
        content = self.content
        heading = content.get_heading(2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_level(self):
        content = self.content
        heading = content.get_heading(1, level=2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_insert_heading(self):
        content = self.content
        clone = content.clone()
        heading = odf_create_heading('Heading_20_2', 2,
                                     u'An inserted heading')
        clone.insert_element(heading, clone.get_body())
        last_heading = clone.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



class TestFrame(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_frame(self):
        content = self.content

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
        content.insert_element(frame1, content.get_body())
        content.insert_element(frame2, content.get_body())

        # Get OK ?
        get = content.get_frame(name='frame1')
        self.assertEqual(get.get_attribute('draw:name'), 'frame1')

        get = content.get_frame(position=2)
        self.assertEqual(get.get_attribute('draw:name'), 'frame2')



class TestImage(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_image(self):
        image = odf_create_image('path')
        expected = '<draw:image xlink:href="path"/>'
        self.assertEqual(image.serialize(), expected)


    def test_insert_image(self):
        content = self.content
        frame = odf_create_frame('frame_image', 'Graphics', '0cm', '0cm')
        image = odf_create_image('path')
        content.insert_element(image, frame)
        content.insert_element(frame, content.get_body())

        # XXX cannot test "insert" and "get" until the test document embeds
        # an image
        get = content.get_image(name='frame_image')
        self.assertEqual(get.get_attribute('xlink:href'), 'path')

        get = content.get_image(position=1)
        self.assertEqual(get.get_attribute('xlink:href'), 'path')



class TestTable(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
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
        content = self.content
        clone = content.clone()
        table = odf_create_table('a_table', 'a_style')
        column = odf_create_column('a_column_style')
        row = odf_create_row()
        cell = odf_create_cell(u"")

        clone.insert_element(column, table)
        clone.insert_element(cell, row)
        clone.insert_element(row, table)
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

        body = clone.get_element('//office:text')
        clone.insert_element(table, body)

        # Get OK ?
        table = clone.get_table(name='a_table')
        self.assertEqual(table.get_attribute('table:name'), 'a_table')

        table = clone.get_table(position=1)
        self.assertEqual(table.get_attribute('table:name'), 'a_table')



class TestList(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
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
        content = self.content
        clone = content.clone()
        item = odf_create_list_item()
        a_list = odf_create_list('a_style')
        clone.insert_element(item, a_list)
        clone.insert_element(a_list, clone.get_body())

        expected = ('<text:list text:style-name="a_style">'
                    '<text:list-item/>'
                    '</text:list>')
        self.assertEqual(a_list.serialize(), expected)



class TestStyle(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
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
        content = self.content
        styles = content.get_style_list()
        self.assertEqual(len(styles), 3)


    def test_get_style_list_family(self):
        content = self.content
        styles = content.get_style_list(family='paragraph')
        self.assertEqual(len(styles), 1)


    def test_get_style_automatic(self):
        content = self.content
        style = content.get_style('P1', 'paragraph')
        self.assertNotEqual(style, None)


    def test_insert_style(self):
        content = self.content
        clone = content.clone()
        style = odf_create_style('style1', 'paragraph')
        properties = odf_create_style_text_properties()
        properties.set_attribute('fo:color', '#0000ff')
        properties.set_attribute('fo:background-color', '#ff0000')
        clone.insert_element(properties, style)
        clone.insert_element(style, clone.get_category_context('automatic'))

        expected = ('<style:style style:name="style1" '
                                 'style:family="paragraph">'
                      '<style:text-properties fo:color="#0000ff" '
                                             'fo:background-color="#ff0000"/>'
                    '</style:style>')
        get1 = clone.get_style('style1', 'paragraph')
        self.assertEqual(get1.serialize(), expected)



class TestNote(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_note(self):
        content = self.content

        # Create OK ?
        note = odf_create_note(u'1', id='note1')
        body = odf_create_paragraph('Standard', u'a footnote')
        # TODO stop here and compare to the snippet

        # Insert OK ?
        clone = content.clone()
        paragraph = clone.get_paragraph(1)
        content.insert_note_body(body, note)
        content.insert_element(note, paragraph)

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
        content = self.content
        clone = content.clone()
        raise NotImplementedError



class TestAnnotation(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
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
        content = self.content
        annotations = content.get_annotation_list()
        self.assertEqual(len(annotations), 1)
        annotation = annotations[0]
        creator = annotation.get_creator()
        self.assertEqual(creator, u"Auteur inconnu")
        date = annotation.get_date()
        self.assertEqual(date, datetime(2009, 6, 22, 17, 18, 42))
        text = annotation.get_text_content()
        self.assertEqual(text, u"This is an annotation")


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
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date(self):
        content = self.content
        start_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_end_date(self):
        content = self.content
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = content.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_end_date(self):
        content = self.content
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = content.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date_end_date(self):
        content = self.content
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
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
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
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
        self.document = document = odf_new_document_from_class('text')
        self.content = content = document.get_xmlpart('content')

        # Encode this table
        #   A B C D E F G
        # 1 1 1 1 2 3 3 3
        # 2 1 1 1 2 3 3 3
        # 3 1 1 1 2 3 3 3
        # 4 1 2 3 4 5 6 7
        table = odf_create_table('a_table', 'Standard')
        column = odf_create_column('Standard')
        column.set_attribute('table:number-columns-repeated', '7')
        content.insert_element(column, table)

        # 3 x "1 1 1 2 3 3 3"
        row = odf_create_row()
        row.set_attribute('table:number-rows-repeated', '3')
        # 3 x "1"
        cell = odf_create_cell(u'1')
        cell.set_attribute('table:number-columns-repeated', '3')
        content.insert_element(cell, row)
        # 1 x "2"
        cell = odf_create_cell(u'2')
        content.insert_element(cell, row)
        # 3 x "3"
        cell = odf_create_cell(u'3')
        cell.set_attribute('table:number-columns-repeated', '3')
        content.insert_element(cell, row)

        content.insert_element(row, table)

        # 1 x "1 2 3 4 5 6 7"
        row = odf_create_row()
        for i in xrange(1, 8):
            cell = odf_create_cell(unicode(i))
            content.insert_element(cell, row)
        content.insert_element(row, table)

        content.insert_element(table, content.get_body())


    def tearDown(self):
        del self.content
        del self.document


    def test_get_cell_coordinates(self):
        x, y = _get_cell_coordinates('ABC123')
        self.assertEqual((x, y), (731, 123))


    def test_get_cell(self):
        content = self.content
        table = content.get_table(name='a_table')

        cell = content.get_cell('D3', table)
        paragraph = content.get_paragraph(1, context=cell)
        self.assertEqual(paragraph.get_text(), '2')

        cell = content.get_cell('F3', table)
        paragraph = content.get_paragraph(1, context=cell)
        self.assertEqual(paragraph.get_text(), '3')

        cell = content.get_cell('D4', table)
        paragraph = content.get_paragraph(1, context=cell)
        self.assertEqual(paragraph.get_text(), '4')



if __name__ == '__main__':
    main()
