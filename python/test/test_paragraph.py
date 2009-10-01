# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.paragraph import odf_create_paragraph, odf_paragraph
from lpod.element import LAST_CHILD, odf_create_element


class TestParagraph(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.body = document.get_body()


    def test_get_paragraph_list(self):
        body = self.body
        paragraphs = body.get_paragraph_list()
        self.assertEqual(len(paragraphs), 7)
        second = paragraphs[1]
        text = second.get_text()
        self.assertEqual(text, 'This is the second paragraph.')


    def test_get_paragraph_list_style(self):
        body = self.body
        paragraphs = body.get_paragraph_list(style='Hanging_20_indent')
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, 'This is a paragraph with a named style.')


    def test_get_paragraph_list_context(self):
        body = self.body
        section2 = body.get_section_by_position(2)
        paragraphs = section2.get_paragraph_list()
        self.assertEqual(len(paragraphs), 2)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, "First paragraph of the second section.")


    def test_get_paragraph_by_content(self):
        body = self.body
        regex = ur'(first|second|a) paragraph'
        paragraph = body.get_paragraph_by_content(regex)
        text = paragraph.get_text()
        self.assertEqual(text, u'This is the first paragraph.')


    def test_get_paragraph_by_content_context(self):
        body = self.body
        section2 = body.get_section_by_position(2)
        regex = ur'([Ff]irst|second|a) paragraph'
        paragraph = section2.get_paragraph_by_content(regex)
        text = paragraph.get_text()
        self.assertEqual(text, u'First paragraph of the second section.')


    def test_odf_paragraph(self):
        body = self.body
        paragraph = body.get_paragraph_by_position(1)
        self.assert_(isinstance(paragraph, odf_paragraph))


    def test_get_paragraph(self):
        body = self.body
        paragraph = body.get_paragraph_by_position(4)
        text = paragraph.get_text()
        expected = 'This is the first paragraph of the second title.'
        self.assertEqual(text, expected)


    def test_insert_paragraph(self):
        body = self.body.clone()
        paragraph = odf_create_paragraph(u'An inserted test',
                                         style='Text_20_body')
        body.insert_element(paragraph, LAST_CHILD)
        last_paragraph = body.get_paragraph_list()[-1]
        self.assertEqual(last_paragraph.get_text(), u'An inserted test')


    def test_get_paragraph_missed(self):
        body = self.body
        paragraph = body.get_paragraph_by_position(999)
        self.assertEqual(paragraph, None)



class TestSetSpan(TestCase):

    def test_text(self):
        text = u"Le Père Noël a une moustache rouge."
        paragraph = odf_create_paragraph(text)
        paragraph.set_span(u"highlight", regex=u"rouge")
        expected = ('<text:p>Le P&#232;re No&#235;l a une moustache '
                      '<text:span '
                        'text:style-name="highlight">rouge</text:span>.'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_tail(self):
        data = (u"<text:p>Le Père Noël a une "
                  u"<text:span>moustache</text:span> rouge.</text:p>")
        paragraph = odf_create_element(data)
        paragraph.set_span(u"highlight", regex=u"rouge")
        expected = ('<text:p>Le P&#232;re No&#235;l a une '
                      '<text:span>moustache</text:span> '
                      '<text:span '
                        'text:style-name="highlight">rouge</text:span>.'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_text_several(self):
        text = u"Le Père rouge a une moustache rouge."
        paragraph = odf_create_paragraph(text)
        paragraph.set_span(u"highlight", regex=u"rouge")
        expected = ('<text:p>Le P&#232;re '
                      '<text:span '
                         'text:style-name="highlight">rouge</text:span> '
                      'a une moustache '
                      '<text:span '
                        'text:style-name="highlight">rouge</text:span>.'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_tail_several(self):
        data = (u"<text:p>Le <text:span>Père</text:span> rouge a une "
                  u"moustache rouge.</text:p>")
        paragraph = odf_create_element(data)
        paragraph.set_span(u"highlight", regex=u"rouge")
        expected = ('<text:p>Le <text:span>P&#232;re</text:span> '
                      '<text:span '
                        'text:style-name="highlight">rouge</text:span> '
                      'a une moustache '
                      '<text:span '
                        'text:style-name="highlight">rouge</text:span>.'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_offset(self):
        text = u"Le Père Noël a une moustache rouge."
        paragraph = odf_create_paragraph(text)
        paragraph.set_span(u"highlight", offset=text.index(u"moustache"))
        expected = ('<text:p>Le P&#232;re No&#235;l a une '
                      '<text:span text:style-name="highlight">moustache '
                      'rouge.</text:span>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_offset_length(self):
        text = u"Le Père Noël a une moustache rouge."
        paragraph = odf_create_paragraph(text)
        paragraph.set_span(u"highlight", offset=text.index(u"moustache"),
                           length=len(u"moustache"))
        expected = ('<text:p>Le P&#232;re No&#235;l a une '
                      '<text:span text:style-name="highlight">moustache'
                      '</text:span> rouge.'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)



if __name__ == '__main__':
    main()
