# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.paragraph import odf_create_paragraph, odf_paragraph
from lpod.element import odf_create_element


class TestParagraph(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.body = document.get_body()


    def test_get_paragraph_list(self):
        body = self.body
        paragraphs = body.get_paragraphs()
        self.assertEqual(len(paragraphs), 7)
        second = paragraphs[1]
        text = second.get_text()
        self.assertEqual(text, 'This is the second paragraph.')


    def test_get_paragraph_list_style(self):
        body = self.body
        paragraphs = body.get_paragraphs(style='Hanging_20_indent')
        self.assertEqual(len(paragraphs), 1)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, 'This is a paragraph with a named style.')


    def test_get_paragraph_list_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        paragraphs = section2.get_paragraphs()
        self.assertEqual(len(paragraphs), 2)
        paragraph = paragraphs[0]
        text = paragraph.get_text()
        self.assertEqual(text, "First paragraph of the second section.")


    def test_get_paragraph_by_content(self):
        body = self.body
        regex = ur'(first|second|a) paragraph'
        paragraph = body.get_paragraph(content=regex)
        text = paragraph.get_text()
        self.assertEqual(text, u'This is the first paragraph.')


    def test_get_paragraph_by_content_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        regex = ur'([Ff]irst|second|a) paragraph'
        paragraph = section2.get_paragraph(content=regex)
        text = paragraph.get_text()
        self.assertEqual(text, u'First paragraph of the second section.')


    def test_odf_paragraph(self):
        body = self.body
        paragraph = body.get_paragraph()
        self.assert_(isinstance(paragraph, odf_paragraph))


    def test_get_paragraph(self):
        body = self.body
        paragraph = body.get_paragraph(position=3)
        text = paragraph.get_text()
        expected = 'This is the first paragraph of the second title.'
        self.assertEqual(text, expected)


    def test_insert_paragraph(self):
        body = self.body.clone()
        paragraph = odf_create_paragraph(u'An inserted test',
                                         style='Text_20_body')
        body.append(paragraph)
        last_paragraph = body.get_paragraphs()[-1]
        self.assertEqual(last_paragraph.get_text(), u'An inserted test')


    def test_get_paragraph_missed(self):
        body = self.body
        paragraph = body.get_paragraph(position=999)
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
