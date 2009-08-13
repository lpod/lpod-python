# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.link import odf_create_link


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
