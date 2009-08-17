# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.paragraph import odf_create_paragraph, odf_paragraph
from lpod.xmlpart import LAST_CHILD


class TestParagraph(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_paragraph_list(self):
        content = self.content
        paragraphs = content.get_paragraph_list()
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
        section2 = content.get_section_by_position(2)
        paragraphs = content.get_paragraph_list(context=section2)
        self.assertEqual(len(paragraphs), 2)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, "First paragraph of the second section.")


    def test_get_paragraph_by_content(self):
        content = self.content
        regex = ur'(first|second|a) paragraph'
        paragraph = content.get_paragraph_by_content(regex)
        text = paragraph.get_text()
        self.assertEqual(text, u'This is the first paragraph.')


    def test_get_paragraph_by_content_context(self):
        content = self.content
        section2 = content.get_section_by_position(2)
        regex = ur'([Ff]irst|second|a) paragraph'
        paragraph = content.get_paragraph_by_content(regex, context=section2)
        text = paragraph.get_text()
        self.assertEqual(text, u'First paragraph of the second section.')


    def test_odf_paragraph(self):
        content = self.content
        paragraph = content.get_paragraph_by_position(1)
        self.assert_(isinstance(paragraph, odf_paragraph))


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


    def test_get_paragraph_missed(self):
        content = self.content
        paragraph = content.get_paragraph_by_position(999)
        self.assertEqual(paragraph, None)



if __name__ == '__main__':
    main()
