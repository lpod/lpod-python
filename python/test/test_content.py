# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.document import odf_create_section
from lpod.document import odf_create_frame, odf_create_image
from lpod.document import odf_create_style, odf_create_span
from lpod.document import odf_create_link
from lpod.xmlpart import LAST_CHILD, NEXT_SIBLING


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



if __name__ == '__main__':
    main()
